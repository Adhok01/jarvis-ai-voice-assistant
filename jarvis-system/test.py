import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something...")
    r.adjust_for_ambient_noise(source, duration=1)
    audio = r.listen(source)

print("Recognizing...")

try:
    print(r.recognize_google(audio))
except Exception as e:
    print(e)