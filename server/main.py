import asyncio
import logging
import json
import os
from enum import Enum
from dataclasses import dataclass, asdict

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    JobRequest,
    WorkerOptions,
    cli,
    stt,
    utils,
)
from livekit.plugins import deepgram
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger("transcriber")
logging.basicConfig(level=logging.INFO)

@dataclass
class Language:
    code: str
    name: str
    flag: str

languages = {
    "en": Language(code="en", name="English", flag="🇺🇸"),
    "es": Language(code="es", name="Spanish", flag="🇪🇸"),
    "fr": Language(code="fr", name="French", flag="🇫🇷"),
    "de": Language(code="de", name="German", flag="🇩🇪"),
    "ja": Language(code="ja", name="Japanese", flag="🇯🇵"),
}

LanguageCode = Enum("LanguageCode", {code: lang.name for code, lang in languages.items()})

class Translator:
    def __init__(self, room: rtc.Room, lang: Enum):
        self.room = room
        self.lang = lang
        self.prompt = (
            f"You are a translator for language: {lang.value}. "
            f"Your only response should be the exact translation of input text in the {lang.value} language."
        )
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-pro")

    async def translate(self, message: str, track: rtc.Track):
        loop = asyncio.get_event_loop()

        def get_translation():
            response = self.model.generate_content([
                {"role": "system", "parts": [self.prompt]},
                {"role": "user", "parts": [message]},
            ])
            return response.text.strip()

        translated = await loop.run_in_executor(None, get_translation)

        segment = rtc.TranscriptionSegment(
            id=utils.misc.shortuuid("SG_"),
            text=translated,
            start_time=0,
            end_time=0,
            language=self.lang.name,
            final=True,
        )
        transcription = rtc.Transcription(
            self.room.local_participant.identity,
            track.sid,
            [segment]
        )
        await self.room.local_participant.publish_transcription(transcription)
        print(f"[🔁 Translation] {message} -> ({self.lang.name}) {translated}")

def prewarm(proc: JobProcess):
    logger.info("[Prewarm] Optional setup complete.")

async def entrypoint(job: JobContext):
    stt_provider = deepgram.STT()
    translators = {}

    async def _forward_transcription(stt_stream: stt.SpeechStream, participant: rtc.RemoteParticipant, track: rtc.Track):
        async for ev in stt_stream:
            if ev.type == stt.SpeechEventType.INTERIM_TRANSCRIPT:
                print(ev.alternatives[0].text, end="\r", flush=True)
            elif ev.type == stt.SpeechEventType.FINAL_TRANSCRIPT:
                message = ev.alternatives[0].text
                print(f"[✔ Final] {participant.identity}: {message}")

                # Publish original transcription
                segment = rtc.TranscriptionSegment(
                    id=utils.misc.shortuuid("SG_"),
                    text=message,
                    start_time=0,
                    end_time=0,
                    language="en",
                    final=True,
                )
                transcription = rtc.Transcription(
                    participant.identity, track.sid, [segment]
                )
                await job.room.local_participant.publish_transcription(transcription)

                # Translate to each participant's requested language
                for translator in translators.values():
                    asyncio.create_task(translator.translate(message, track))

    async def transcribe_track(participant: rtc.RemoteParticipant, track: rtc.Track):
        audio_stream = rtc.AudioStream(track)
        stt_stream = stt_provider.stream()

        asyncio.create_task(_forward_transcription(stt_stream, participant, track))

        async for ev in audio_stream:
            stt_stream.push_frame(ev.frame)

    @job.room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            logger.info(f"[Audio] Track subscribed from {participant.identity}")
            asyncio.create_task(transcribe_track(participant, track))

    @job.room.on("participant_attributes_changed")
    def on_attributes_changed(attrs: dict[str, str], participant: rtc.Participant):
        lang = attrs.get("captions_language")
        if lang and lang != "en" and lang not in translators:
            try:
                translators[lang] = Translator(job.room, LanguageCode[lang])
                logger.info(f"[Language] Added translator for: {lang}")
            except KeyError:
                logger.warning(f"[Language] Unsupported code: {lang}")

    await job.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    @job.room.local_participant.register_rpc_method("get/languages")
    async def get_languages(data: rtc.RpcInvocationData):
        logger.info("[RPC] get/languages called")
        langs = [asdict(lang) for lang in languages.values()]
        return json.dumps(langs)

async def request_fnc(req: JobRequest):
    await req.accept(name="agent", identity="agent")

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            request_fnc=request_fnc,
        )
    )
