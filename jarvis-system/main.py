import speech_recognition as sr
import pyttsx3
import logging
import os
import datetime
import webbrowser
import wikipedia
import subprocess
import random
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile


# This is Logger for the application
LOG_DIR = "logs"
LOG_FILE_NAME = "application.log"

os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, LOG_FILE_NAME)

logging.basicConfig(
    filename=log_path,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# Supported languages: code -> (Google STT locale, spoken phrase that switches to it)
# Add an entry here to support a new language end-to-end.
LANGUAGES = {
    "en": {"stt_locale": "en-IN", "switch_phrase": "switch to english"},
    "hi": {"stt_locale": "hi-IN", "switch_phrase": "switch to hindi"},
    # "ta": {"stt_locale": "ta-IN", "switch_phrase": "switch to tamil"},
    # "fr": {"stt_locale": "fr-FR", "switch_phrase": "switch to french"},
}

# Changed only when the user explicitly says a switch phrase above.
# We deliberately do NOT auto-detect language from short voice commands —
# language-detection libraries (e.g. langdetect) are built for paragraphs of
# text and are unreliable on 2-4 word phrases (e.g. "exit" gets misread as
# Catalan, romanized Hindi gets misread as Indonesian). Explicit switching
# is slower to set up but never guesses wrong.
CURRENT_LANG = "en"


def translate_text(text, source_lang, target_lang):
    """Translate text between languages. Returns the original text
    unchanged if source and target are the same, or if translation fails.
    """
    if source_lang == target_lang:
        return text
    try:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        logging.error(f"Translation error ({source_lang}->{target_lang}): {e}")
        return text


# Taking the male voice from my system
def get_voice_id():
    temp_engine = pyttsx3.init('nsss')
    voices = temp_engine.getProperty("voices")
    temp_engine.stop()
    if len(voices) > 3:
        return voices[3].id
    elif voices:
        return voices[0].id
    return None

VOICE_ID = get_voice_id()


def speak(text, lang=None):
    """Convert text to voice.

    All existing calls in this file write English text, e.g. speak("Good bye sir").
    If lang isn't given explicitly, we use CURRENT_LANG (set explicitly by the
    user via a "switch to <language>" command) and auto-translate the English
    text into it before speaking, so no other code in this file needs to change.

    For English, uses the local pyttsx3 engine (fast, offline, no network).
    For any other language, uses gTTS (Google Text-to-Speech), since pyttsx3's
    system voices are typically English-only and mispronounce other languages.
    """
    if lang is None:
        lang = CURRENT_LANG

    if lang != "en":
        text = translate_text(text, source_lang="en", target_lang=lang)

    print(f"JARVIS ({lang}): {text}")

    if lang == "en":
        try:
            # Re-init a fresh engine each call — pyttsx3's nsss driver on macOS
            # frequently goes silent (no error, no audio) if the same engine
            # instance is reused across many say()/runAndWait() cycles.
            local_engine = pyttsx3.init('nsss')
            local_engine.setProperty('rate', 170)
            if VOICE_ID:
                local_engine.setProperty('voice', VOICE_ID)
            local_engine.say(text)
            local_engine.runAndWait()
            local_engine.stop()
            return
        except Exception as e:
            print(f"Speech error: {e}")
            logging.error(f"Speech error: {e}")
            # fall through to gTTS as a backup

    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            subprocess.run(["afplay", f.name])
        os.remove(f.name)
    except Exception as e:
        print(f"gTTS speech error: {e}")
        logging.error(f"gTTS speech error: {e}")


def takeCommand():
    """Listen to the mic and transcribe speech using the currently active
    language's STT locale (CURRENT_LANG, changed only by an explicit
    'switch to <language>' voice command).
    """
    stt_locale = LANGUAGES[CURRENT_LANG]["stt_locale"]

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")

        # Adjust for background noise
        r.adjust_for_ambient_noise(source, duration=1)

        r.pause_threshold = 0.8
        r.energy_threshold = 300

        audio = r.listen(source, timeout=5, phrase_time_limit=6)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language=stt_locale)
        print(f"User said ({stt_locale}): {query}")
        return query

    except Exception as e:
        print(e)
        return "None"


# this function will wish you
def wish_me():
    hour = (datetime.datetime.now().hour)

    if hour >= 0 and hour <= 12:
        speak("Good Morning sir! How are you doing?")

    elif hour >= 12 and hour <= 18:
        speak("Good afternoon sir! How are you doing?")

    else:
        speak("Good evening sir! How are you doing?")

    speak("I am JARVIS. Tell me sir how can i help you? Say 'switch to hindi' or 'switch to english' any time to change my language.")


def play_music(song_name=None):
    music_dir = os.path.expanduser("~/Music/Music/Media")   # Apple Music library folder
    AUDIO_EXTENSIONS = (".mp3", ".m4a", ".wav", ".aac", ".flac")

    try:
        all_files = os.listdir(music_dir)
        songs = [f for f in all_files if f.lower().endswith(AUDIO_EXTENSIONS)]

        if not songs:
            speak("No music files found in your music directory.")
            return

        if song_name:
            # Fuzzy match: does the requested name appear in any filename?
            song_name_clean = song_name.strip().lower()
            matches = [s for s in songs if song_name_clean in s.lower()]

            if matches:
                chosen = matches[0]
                speak(f"Playing {chosen} for you sir")
                subprocess.Popen(["open", os.path.join(music_dir, chosen)])
                return
            else:
                speak(f"I couldn't find a song matching {song_name}. Playing something random instead.")

        random_song = random.choice(songs)
        speak(f"Playing a random song sir: {random_song}")
        subprocess.Popen(["open", os.path.join(music_dir, random_song)])

    except FileNotFoundError:
        speak("Sorry sir, I could not find your music folder.")
    except Exception as e:
        speak("Sorry sir, something went wrong trying to play music.")
        logging.error(f"play_music error: {e}")


wish_me()
while True:

    raw_query = takeCommand()

    if raw_query == "None":
        print("none")
        continue

    # Translate the query into English (if we're not already in English mode)
    # so all the existing intent-matching below keeps working unchanged.
    query = translate_text(raw_query, source_lang=CURRENT_LANG, target_lang="en").lower()
    print(f"[lang: {CURRENT_LANG}] {query}")

    # --- Language switching (checked first, works from any current language) ---
    matched_switch = False
    for code, info in LANGUAGES.items():
        if info["switch_phrase"] in query:
            CURRENT_LANG = code
            speak(f"Okay, I will now speak in {code}.", lang=code)
            matched_switch = True
            break
    if matched_switch:
        continue

    if "time" in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"Sir the time is {strTime}")

    elif "your name" in query or "who are you" in query:
        speak("My name is Adhok")

    # Small talk
    elif "how are you" in query:
        speak("I am functioning at full capacity sir!")

    elif "who made you" in query:
        speak("I was created by Bappy sir, a brilliant mind!")

    elif "thank you" in query:
        speak("It's my pleasure sir. Always happy to help.")

    elif "play music" in query or "play" in query or "music" in query:
        # Try to pull out a specific song name from phrases like
        # "play shape of you" or "play music by adele"
        song_name = None
        for prefix in ["play music by", "play song by", "play song", "play music", "play"]:
            if prefix in query:
                candidate = query.split(prefix, 1)[1].strip()
                candidate = candidate.replace("by", "").strip()
                if candidate:
                    song_name = candidate
                break
        play_music(song_name)

    elif "exit" in query:
        speak("Good bye sir")
        exit()

    # Calculator
    elif "open calculator" in query or "calculator" in query:
        speak("Opening calculator")
        subprocess.Popen(["open", "-a", "Calculator"])

    # Notepad
    elif "open notepad" in query:
        speak("Opening Notepad")
        subprocess.Popen(["open", "-a", "TextEdit"])

    elif "open google" in query:
        speak("open google")
        subprocess.Popen(["open", "https://www.google.com"])

    # Command Prompt
    elif "open terminal" in query or "open cmd" in query:
        speak("Opening Command Prompt terminal")
        subprocess.Popen(["open", "-a", "Terminal"])

    # Calendar
    elif "open calendar" in query or "calendar" in query:
        speak("Opening Calendar")
        subprocess.Popen(["open", "https://calendar.google.com"])

    # Jokes
    elif "joke" in query:
        jokes = [
            "Why don't programmers like nature? Too many bugs.",
            "I told my computer I needed a break. It said no problem, it will go to sleep.",
            "Why do Java developers wear glasses? Because they don't C sharp."
        ]
        speak(random.choice(jokes))

    # YouTube search
    elif "youtube" in query:
        speak("Opening YouTube for you.")
        yt_query = query.replace("youtube", "")
        subprocess.Popen([
            "open",
            f"https://www.youtube.com/results?search_query={yt_query}"
        ])

    elif "open facebook" in query:
        speak("ok sir. opening facebook")
        subprocess.Popen(["open", "https://www.facebook.com"])

    # This query for search something from wikipedia
    elif 'wikipedia' in query or "who is" in query or "what is" in query:
        speak("Searching wikipedia")

        search_term = query.replace("wikipedia", "")
        search_term = search_term.replace("who is", "").replace("what is", "")
        search_term = search_term.replace("according to", "")
        search_term = search_term.strip()

        try:
            results = wikipedia.summary(search_term, sentences=2)
            speak("According to wikipedia ")
            print(results)
            speak(results)

        except wikipedia.exceptions.DisambiguationError as e:
            speak("There are multiple results for that. Can you be more specific?")
            print(f"Disambiguation options: {e.options[:5]}")

        except wikipedia.exceptions.PageError:
            speak("Sorry sir, I could not find anything on that topic.")

        except Exception as e:
            speak("Sorry sir, I'm having trouble reaching wikipedia right now.")
            print(f"Wikipedia error: {e}")