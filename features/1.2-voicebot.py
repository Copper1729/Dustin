import re
import os
import webbrowser
import subprocess
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
# voice.py
import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return "Spoken successfully"

def get_response(user_input):
    # Your assistant logic here
    return f"You said: {user_input}"
# ---- Config ----
API_KEY = "GEMINI_API_KEY"  # keep in .env for safety
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"
recognizer = sr.Recognizer()
tts = pyttsx3.init()
tts.setProperty('rate', 180)

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"[\*_`]+", "", text).strip()

def speak(text):
    text = clean_text(text)
    print("Gemini:", text)
    tts.say(text)
    tts.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening... Speak now.")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            speak("Didn't catch that. Please try again.")
            return None

    try:
        phrase = recognizer.recognize_google(audio)
        print("You:", phrase)
        return phrase
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        speak("Speech service is unavailable.")
        return None

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content(f"Answer in maximum 5 lines: {prompt}")
        return resp.text
    except Exception as e:
        return f"API Error: {e}"

# ---- Command Execution ----
def execute_command(cmd):
    cmd = cmd.lower()

    # --- System apps ---
    if "open notepad" in cmd:
        os.system("notepad.exe")
        speak("Opening Notepad")
        return True
    if "open calculator" in cmd:
        os.system("calc.exe")
        speak("Opening Calculator")
        return True

    # --- Websites ---
    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "twitter": "https://twitter.com",
        "instagram": "https://www.instagram.com",
        "github": "https://github.com"
    }
    for site, url in websites.items():
        if f"open {site}" in cmd:
            webbrowser.open(url)
            speak(f"Opening {site}")
            return True

    # --- Third-party Apps (Shortcuts or EXE paths) ---
    apps = {
        # path
    }
    for app, path in apps.items():
        if f"open {app}" in cmd:
            if os.path.exists(path):
                try:
                    if path.endswith(".lnk"):
                        os.startfile(path)  # ✅ better for shortcuts
                    else:
                        subprocess.Popen(path)
                    speak(f"Opening {app}")
                except Exception as e:
                    speak(f"Error opening {app}: {e}")
            else:
                speak(f"Could not find {app} at the specified path.")
            return True

    # --- YouTube search ---
    if "play" in cmd and "youtube" in cmd:
        query = cmd.replace("play", "").replace("on youtube", "").strip()
        url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(url)
        speak(f"Searching {query} on YouTube")
        return True

    return False

# ---- Main ----
if __name__ == "__main__":
    speak("Voice assistant (Gemini) is ready!")
    while True:
        cmd = listen()
        if not cmd:
            continue
        if cmd.lower() in ["exit", "quit", "stop"]:
            speak("Goodbye!")
            break

        if not execute_command(cmd):
            reply = ask_gemini(cmd)
            speak(reply)
