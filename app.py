import streamlit as st
import os
import streamlit_lottie as st_lottie
import google.generativeai as genai
from features.auth import authentication, get_user_details
from features.dashboard import user_dashboard
from features.contact_us import contact_us
from features.functions import load_lottie_file

# Streamlit page configuration
st.set_page_config(
    page_title="Dustin",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state keys
if 'register' not in st.session_state:
    st.session_state['register'] = False
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {}

GOOGLE_API_KEY = 'GEMINI_API_KEY'
genai.configure(api_key=GOOGLE_API_KEY)

def introduction():
    user_data = get_user_details()
    name = user_data.get('name', 'Friend')
    
    if 'intro_message' not in st.session_state:
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            prompt = f"You are Dustin, a mental health companion. Generate a short, warm, and encouraging welcome message for {name}, a healthcare professional. Keep it under 30 words and use emojis."
            response = model.generate_content(prompt)
            st.session_state['intro_message'] = response.text
        except Exception:
            st.session_state['intro_message'] = f"Welcome back, {name}! We're here to support you. ✨"

    st.markdown(f"<h3 style='text-align: center;'>{st.session_state['intro_message']}</h3>", unsafe_allow_html=True)
    st.header("🤖Dustin: Your Mental Health Companion", divider='rainbow')
    with st.container(border=False):
        left_column, right_column = st.columns(2)
        with left_column:
            st.subheader("Welcome to Dustin!", divider='rainbow')
            intro_text = '''
            **Dustin** serves as an AI-powered ally tailored to aid medical professionals through mental health support, clinical utilities, and customized care options. 
            This initiative tackles the hurdles encountered by medical staff in stressful settings, boosting their welfare and work effectiveness. 
            The platform features a conversational agent, symptom analyzer, daily schedule builder, and daily summary creator, plus more.

            **Dustin** aims to offer a secure environment for healthcare staff to voice emotions, ask for guidance, and utilize mental wellness tools. 
            The system uses AI to provide tailored answers and suggestions derived from user data. You can chat with the bot,
            assess symptoms for yourself or patients for preliminary detection, design daily agendas, and produce daily summaries to monitor health and growth. Through Dustin, medical workers get
            the necessary backing to handle professional obstacles and sustain their mental wellness.
            '''
            st.write(intro_text)
        with right_column:
            robot_file = load_lottie_file('animations/robot.json')
            st_lottie.st_lottie(robot_file, key='robot', height=450, width=450 ,loop=True)
        st.divider()
    
    with st.container(border=False):
        left_column, right_column = st.columns(2)
        with right_column:
            st.subheader("Key Features", divider='rainbow')
            features = [
                "**Share with Me (ChatBot)**: An interactive AI companion offering mental wellness backing, engaging in dialogue, and hearing your worries. Converse in the language you prefer.",
                "**Symptom Checker**: A utility to evaluate symptoms and offer preliminary identification of medical states.",
                "**Daily Plans Maker**: A function to design daily schedules and establish objectives for your day.",
                "**Daily Report**: A utility to produce a recap and guidance derived from your day's events, emotions, and encountered difficulties.",
                "**Profile**: A personal hub to check and modify your private and career details.",
                "**Contact Us**: An option to reach out for comments, questions, and assistance.",
            ]
            for feature in features:
                st.write(f"🔹 {feature}")
            st.write("*Explore the features in the sidebar to learn more about each one.*")
        
        with left_column:
            features_file = load_lottie_file('animations/features.json')
            st_lottie.st_lottie(features_file, key='features', height=450, width=450 ,loop=True)
        st.divider()

    with st.container(border=True):
        st.subheader("FAQs", divider='rainbow')
        
        with st.expander("What is Dustin?"):
            st.write("Dustin acts as an AI-based partner built to assist medical staff with mental health aid, clinical instruments, and tailored care functions.")
        
        with st.expander("What are the key features of Dustin?"):
            st.write("Dustin features a conversational bot, symptom analyzer, daily scheduler, daily summary creator, and a personal dashboard.")
        
        with st.expander("How can Dustin help healthcare workers?"):
            st.write("Dustin offers a protected environment for medical professionals to voice emotions, find guidance, and use mental wellness assets.")
        
        with st.expander("How does Dustin use artificial intelligence?"):
            st.write("Dustin utilizes AI to provide customized answers and suggestions derived from user interactions, using a model trained on medical information.")

        with st.expander("How can I get started with Dustin?"):
            st.write("To begin using Dustin, sign up with your details and browse the sidebar tools to understand each function.")

        with st.expander("Is my data secure with Dustin?"):
            st.write("Dustin prioritizes data safety and confidentiality. Your information is encrypted and kept secure to safeguard your privacy.")

        with st.expander("How can I provide feedback or contact the Dustin team?"):
            st.write("You can offer input or reach the Dustin team via the 'Contact Us' option in the sidebar.")

            
# Initialize session state for authentication
authentication()

# Page Navigation
if st.session_state["authentication_status"]:
    try:
        pg = st.navigation([
            st.Page(introduction, title='Introduction', icon='🙋🏻‍♂️'),
            st.Page("features/1-ChatBot.py", title='Share with Me (ChatBot)', icon='🤖'),
            st.Page("features/6-StudyTime.py", title='Study Time', icon='📚'),
            st.Page("features/5-Games.py", title='Mindful Games', icon='🎮'),
            st.Page("features/7-funtime.py", title='FunTime Zone', icon='🛝'),
            st.Page("features/2-SymptomChecker.py", title='Symptom Checker', icon='🩺'),
            st.Page("features/3-DailyPlans.py", title='Daily Plans Maker', icon='📅'),
            
            
            st.Page("features/4-DailyReport.py", title='Daily Report', icon='📋'),
            st.Page(user_dashboard, title='Profile', icon='🧑🏻‍⚕️'),
            st.Page(contact_us, title='Contact Us', icon='📞'),
            
        ])
        pg.run()
    except AttributeError:
        st.error("🚨 **Streamlit Update Required**\n\nThis app uses `st.navigation`, which requires Streamlit version **1.31.0** or newer.\n\nPlease run: `pip install --upgrade streamlit`")