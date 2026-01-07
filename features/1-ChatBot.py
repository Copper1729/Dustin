import streamlit as st
import google.generativeai as genai
from features.system_settings import safety_settings, generation_config, SystemPrompts
from dotenv import load_dotenv
import os
from features.functions import *
import speech_recognition as sr
import pyttsx3
import re
import subprocess
import sys



load_dotenv()

GEMINI_API_KEY = 'GEMINI_API_KEY'
genai.configure(api_key=GEMINI_API_KEY)

prompts = SystemPrompts()

model = genai.GenerativeModel('models/gemini-2.5-flash',
                safety_settings=safety_settings,
                generation_config=generation_config
        )

# Track time spent
track_time_spent('chatbot_used')

st.warning("⚠️Note: This represents a demonstration of the Dustin ChatBot. It is a prototype, not the finished product, and might not resolve every query.")
st.header('🤖Chat with Dustin', divider='rainbow')
st.subheader("🎙️ Desktop Voice Assistant")

# create storage if missing
if "voice_proc" not in st.session_state:
    st.session_state.voice_proc = None
    st.session_state.voice_logs = []

BASE = os.path.dirname(os.path.abspath(__file__))
voice_path = os.path.join(BASE, "1.2-voicebot.py")

# --- START / STOP BUTTONS ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Launch Voice Bot", disabled=st.session_state.voice_proc is not None):
        try:
            python_exec = sys.executable
            st.session_state.voice_proc = subprocess.Popen(
                [python_exec, voice_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            st.success("Voice Bot launched!")
        except Exception as e:
            st.error(f"Could not start Voice Bot: {e}")

with col2:
    if st.button("🛑 Stop Voice Bot", disabled=st.session_state.voice_proc is None):
        try:
            st.session_state.voice_proc.terminate()
            st.session_state.voice_proc = None
            st.session_state.voice_logs.append("--- Voice Bot stopped ---")
            st.success("Voice Bot stopped.")
        except Exception as e:
            st.error(f"Could not stop Voice Bot: {e}")

# --- REAL-TIME LOG OUTPUT ---
st.subheader("📟 Voice Bot Console")

log_area = st.empty()

if st.session_state.voice_proc:
    proc = st.session_state.voice_proc
    if proc.stdout:
        for line in proc.stdout:
            st.session_state.voice_logs.append(line.rstrip())
        # keep Streamlit looping
        st.rerun()

# render logs
if st.session_state.voice_logs:
    log_area.code("\n".join(st.session_state.voice_logs), language="bash")
else:
    log_area.info("Voice Bot is not running.")



# --- Controls moved from sidebar to main page ---
col1, col2 = st.columns([3, 1])
with col1:
    # This button will toggle the voice mode
    voice_mode_on = st.session_state.get('voice_mode_on', False)
    button_text = "Deactivate Voice Bot" if voice_mode_on else "Activate Voice Bot"
    if st.button(f"🎙️ {button_text}"):
        st.session_state.voice_mode_on = not voice_mode_on
        # Rerun to apply the new state
        st.rerun()

with col2:
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.chat_session.history.append({"role": "model", "content": "Hello! I am Dustin, your AI mental health companion. How are you feeling today?"})
        if 'voice_mode_on' in st.session_state:
            st.session_state.voice_mode_on = False
        st.rerun()

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.chat_session.history.append({"role": "model", "content": "Hello! I am Dustin, your AI mental health companion. How are you feeling today?"})

# Display the chat history
for msg in st.session_state.chat_session.history:
    with st.chat_message(map_role(msg["role"])):
        st.markdown(msg["content"])

# Input field for user's message
user_input = st.chat_input("Ask Dustin...")
if user_input:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_input)

    # Send user's message to Gemini and get the response
    gemini_response = fetch_gemini_response(prompts.system_instruction + "\n\n" + user_input)

    # Display Gemini's response
    with st.chat_message("assistant"):
        st.markdown(gemini_response)

    # Add user and assistant messages to the chat history
    st.session_state.chat_session.history.append({"role": "user", "content": user_input})
    st.session_state.chat_session.history.append({"role": "model", "content": gemini_response})

# Voice Chat Logic
def clean_text(text):
    return re.sub(r"[\*_`]+", "", text).strip()

def speak(text):
    try:
        # Attempt to initialize COM for Windows to prevent threading errors.
        # This is a no-op on other platforms.
        try:
            import pythoncom
            pythoncom.CoInitialize()
            engine = pyttsx3.init('sapi5')
        except ImportError:
            # If pywin32 is not installed, we'll get an ImportError.
            st.toast("For voice output on Windows, please `pip install pywin32`.", icon="⚠️")
            engine = pyttsx3.init()
        except Exception:
            # Fallback to the default driver if sapi5 is not available.
            engine = pyttsx3.init()
            
        engine.setProperty('rate', 180)
        engine.say(clean_text(text))
        engine.runAndWait()
    except Exception as e:
        st.toast(f"Could not speak: {e}", icon="❌")

# --- Voice Bot Logic ---
if st.session_state.get('voice_mode_on'):
    if st.button("🛑 Stop Voice Bot", type="primary"):
        st.session_state.voice_mode_on = False
        st.rerun()

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now.")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=15)
            user_voice_input = recognizer.recognize_google(audio)

            # Voice command to stop the mode
            if "stop voice" in user_voice_input.lower() or "exit voice" in user_voice_input.lower():
                st.session_state.voice_mode_on = False
                st.info("🗣️ **Dustin:** Deactivating voice mode. Goodbye!")
                speak("Deactivating voice mode. Goodbye!")
                st.rerun()
            
            # Display what user said
            st.success(f"👤 **You:** {user_voice_input}")

            # Display user message
            st.chat_message("user").markdown(user_voice_input)
            
            # Generate and display response
            gemini_response = fetch_gemini_response(prompts.system_instruction + "\n\n" + user_voice_input)
            with st.chat_message("assistant"):
                st.markdown(gemini_response)
            
            # Update history
            st.session_state.chat_session.history.append({"role": "user", "content": user_voice_input})
            st.session_state.chat_session.history.append({"role": "model", "content": gemini_response})
            
            # Display Subtitle
            st.info(f"🗣️ **Dustin:** {gemini_response}")

            # Speak response
            speak(gemini_response)
            st.rerun()

        except sr.WaitTimeoutError:
            # If user is silent, just listen again
            st.rerun()
        except sr.UnknownValueError:
            st.toast("Sorry, I didn't catch that.")
            st.rerun()
        except sr.RequestError:
            st.toast("Speech service unavailable.")
            st.session_state.voice_mode_on = False
            st.rerun()
        except Exception as e:
            st.toast(f"Error: {e}")
            st.session_state.voice_mode_on = False
            st.rerun()