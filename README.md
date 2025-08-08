# Live AI-generated Real-Time Translation System

## Introduction

This project demonstrates a powerful real-time translation system that automatically transcribes and translates live speech into multiple languages. Perfect for multilingual conferences, educational sessions, or international meetings.

## Key Features

- **Real-Time Translation**: Instant translation of live speech
- **Multi-Language Support**: Currently supports English, French, German, Spanish, and Japanese
- **Single Host System**: Optimized for one speaker with multiple listeners
- **Language Preferences**: Each listener can choose their preferred language
- **High-Quality Speech Recognition**: Powered by Deepgram's advanced STT
- **Neural Translation**: Utilizing Gemini API for accurate translations

## Technical Stack

- 🌐 **LiveKit**: Real-time communication infrastructure
- 🤖 **LiveKit Agents**: Backend processing and coordination
- 👂 **Deepgram**: Speech-to-text processing
- 🌍 **Google Gemini AI**: Neural machine translation
- ⚡ **Next.js**: Frontend framework

## System Architecture

1. **Room Creation & Management**
   - Automatic agent joining on room creation
   - Dynamic host detection and mic stream subscription

2. **Speech Processing Pipeline**
   - Real-time audio streaming
   - Speech-to-text conversion via Deepgram
   - Neural translation processing

3. **Translation Distribution**
   - Language-specific routing
   - Real-time caption delivery
   - Multi-user synchronization

## Running the demo

### Run the agent
1. `cd server`
2. `python -m venv .venv`
3. `source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `cp .env.example .env`
6. add values for keys in `.env`
7. `python main.py dev`

### Run the client
1. `cd client/web`
2. `pnpm i`
3. `cp .env.example .env.local`
4. add values for keys in `.env.local`
5. `pnpm dev`
6. open a browser and navigate to `http://localhost:3000`

## Known Limitations

- Single host restriction per session
- Occasional UI glitches when multiple browser windows are open
- STT performance may degrade with multiple concurrent connections

## Extending the System

You can easily add support for additional languages by modifying the language configuration in the agent code. The system is designed to be modular and extensible.

## Need Professional Implementation?

Looking to implement a similar system for your organization? We specializes in building custom AI-powered solutions.

🔗 [Contact Us for Professional Implementation](https://93uwdbaosfb.typeform.com/to/ZNEb9H9A)


## Documentation
For more information about LiveKit Agents and their capabilities, visit: [LiveKit Agents Documentation](https://docs.livekit.io/agents/)

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
