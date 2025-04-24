import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 1.0)

def speak(text):
    print(f"JARVIS: {text}")
    engine.say(text)
    try:
        engine.runAndWait()
    except RuntimeError:
        # Handle the "run loop already started" error
        pass
