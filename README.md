# JARVIS — Multilingual Voice Assistant

A Python-based voice assistant for macOS that listens through your microphone, understands natural speech in **English and Hindi**, and talks back. It can look things up on Wikipedia, open apps, play music, tell jokes, and more — all hands-free.

Built as a personal project to explore speech recognition, text-to-speech, and multilingual NLP pipelines end to end.

---

## Features

- 🎙️ **Voice-controlled** — no typing, just speak naturally
- 🌐 **Multilingual** — switch between English and Hindi on the fly with a spoken command
- 📚 **Wikipedia lookups** — ask "who is..." or "what is..." and get a spoken summary
- 🎵 **Music playback** — play a random song, or ask for one by name
- 🖥️ **System commands** — open Calculator, TextEdit, Terminal, Calendar, and more
- 😄 **Small talk** — jokes, greetings, and casual conversation
- 🛡️ **Graceful error handling** — network hiccups or bad lookups won't crash the app

## Demo

```
JARVIS: Good Morning sir! How are you doing?
JARVIS: I am JARVIS. Tell me sir how can i help you?
Listening...
Recognizing...
User said: who is Shahrukh Khan according to Wikipedia
JARVIS: Searching wikipedia
JARVIS: Shah Rukh Khan (pronounced ['ʃaːɦʊʏ xäːn] ; born as Shahrukh Khan
on 2 November 1965), popularly known by the initials SRK, is an Indian
actor and film producer renowned for his work in Hindi cinema...
```

## How it works

| Stage | Library | Purpose |
|---|---|---|
| Speech-to-text | `speech_recognition` (Google Web Speech API) | Converts microphone audio to text |
| Translation | `deep-translator` | Translates non-English input to English for intent-matching, and replies back to the active language |
| Text-to-speech (English) | `pyttsx3` | Fast, offline voice output |
| Text-to-speech (other languages) | `gTTS` + `afplay` | Correct pronunciation for non-English replies |
| Knowledge lookups | `wikipedia` | Answers factual "who is" / "what is" questions |
| System actions | `subprocess` (macOS `open`) | Launches apps and URLs |

Language switching is **explicit**, not auto-detected — you say "switch to hindi" or "switch to english." Automatic language detection was tested and found unreliable on short voice commands (a 2–3 word phrase doesn't carry enough signal for libraries like `langdetect` to guess correctly), so this project favors a command the user controls over a guess that can silently misfire.

## Requirements

- macOS (uses `open`, `afplay`, and the `nsss` pyttsx3 driver)
- Python 3.8
- A working microphone and speakers
- Internet connection (required for speech recognition, translation, Wikipedia, and non-English speech)

## Setup

```bash
# Create and activate the environment
conda create -n jarvissystem python=3.8
conda activate jarvissystem

# Install dependencies
pip install SpeechRecognition pyttsx3 wikipedia pyaudio
pip install deep-translator gTTS
```

> If `pyaudio` fails to install on macOS, install the system library first:
> `brew install portaudio`, then retry the pip install.

The first time you run it, macOS will ask for microphone permission — approve it under **System Settings → Privacy & Security → Microphone**.

## Usage

```bash
conda activate jarvissystem
python main.py
```

Then just talk. Some things to try:

| Say | JARVIS does |
|---|---|
| "what time is it" | Speaks the current time |
| "what is your name" | Introduces itself |
| "tell me a joke" | Tells a random programming joke |
| "who is \<person\>" | Reads a 2-sentence Wikipedia summary |
| "play music" | Plays a random song from your library |
| "play \<song name\>" | Finds and plays that specific song |
| "open calculator" | Opens Calculator |
| "switch to hindi" | Switches to Hindi mode |
| "switch to english" | Switches back to English |
| "exit" | Says goodbye and quits |

## Adding a new language

Add one entry to the `LANGUAGES` dictionary in `main.py`:

```python
LANGUAGES = {
    "en": {"stt_locale": "en-IN", "switch_phrase": "switch to english"},
    "hi": {"stt_locale": "hi-IN", "switch_phrase": "switch to hindi"},
    "ta": {"stt_locale": "ta-IN", "switch_phrase": "switch to tamil"},  # new
}
```

No other code changes are needed — translation and speech output key off this dictionary automatically.

## Known limitations

- macOS-only (`open`/`afplay` commands and the `nsss` TTS driver are platform-specific)
- Only English and Hindi are wired up by default
- Non-English speech output requires internet (gTTS) and has more latency than the offline English voice
- Wikipedia lookups return a short 2-sentence summary only
- Song name matching is a simple substring match

## Project structure

```
.
├── main.py              # Entire application
├── logs/
│   └── application.log  # Runtime errors and translation/speech failures
└── README.md
```

## License

This project is open for personal and educational use. Feel free to fork and adapt it.
