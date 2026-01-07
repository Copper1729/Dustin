import google.generativeai as genai
import streamlit as st
import time
import os
from dotenv import load_dotenv
from features.system_settings import safety_settings, generation_config_symptom_checker, SystemPrompts
from features.functions import track_time_spent

load_dotenv()
GOOGLE_API_KEY='GEMINI_API_KEY'
genai.configure(api_key=GOOGLE_API_KEY)

prompts = SystemPrompts()

model = genai.GenerativeModel('models/gemini-2.5-flash',
                safety_settings=safety_settings,
                generation_config=generation_config_symptom_checker)

# Track time spent
track_time_spent('symptom_checker_used')

st.warning('⚠️Note: Dustin Symptom Checker is currently an AI-based prototype feature. Please exercise caution and see a physician for professional medical counsel.')

st.header('🩺Symptom Checker', anchor='symptom-checker', divider='rainbow')
with st.expander('What is Symptom Checker?'):
    st.write('The Symptom Checker utilizes Google\'s AI to assist in recognizing potential medical issues from your symptoms. It aids healthcare staff in preliminary diagnosis for themselves or patients to facilitate early care. Note that this utility does not replace expert medical counsel and is for informational use only.')
st.divider()

st.subheader('Enter your details to check your symptoms:')
with st.form(key='symptom-checker-form'):
    gender = st.selectbox('Select your gender*', ['Male', 'Female', 'Other', 'Prefer not to say'])
    age = st.number_input('Enter your age*', min_value=1, max_value=100)
    body_temperature = st.number_input('Enter your body temperature in Fahrenheit*', min_value=95.0, max_value=110.0, step=0.1)
    symptoms = st.text_area('Enter your symptoms*', height=100, placeholder='Example: headache, fever, cough etc. from last 2 days or other relevant information')
    st.markdown('*Required**')
    submit_button = st.form_submit_button(label='Check Symptoms')

    if submit_button:
        if not gender or not age or not symptoms or not body_temperature:
            st.error('Please fill all the required fields.')
            st.stop()
        else:
            st.success('Please wait while Dustin is processing your request...')
st.divider()

with st.spinner('Processing your request...'):
    if gender and age and symptoms and body_temperature is not None:
        st.subheader('Symptom Checker Results:')
        prompt = f"""{prompts.system_instruction_symptom_checker}\n\n I am a {age} year's old {gender} with body temperature {body_temperature} and symptoms like {symptoms}. Can you help me to identify the possible health conditions and what to do next?"""
        response = model.generate_content(prompt)
        st.write(response.text)
    else:
        st.warning('Please fill all the required fields to check your symptoms.')