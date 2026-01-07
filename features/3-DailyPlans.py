import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import datetime
from features.system_settings import safety_settings, generation_config_daily_plans, SystemPrompts
from features.functions import track_time_spent

load_dotenv()
GOOGLE_API_KEY = "GEMINI_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

prompts = SystemPrompts()

model = genai.GenerativeModel(model_name="models/gemini-2.5-flash",
                safety_settings=safety_settings,
                generation_config=generation_config_daily_plans)

# Track time spent
track_time_spent('daily_plans_used')

st.warning("⚠️Note: Dustin Daily Plans is currently an experimental AI prototype. Use with discretion and adjust the suggested schedules to fit your requirements.")

st.header("📅Daily Plans Maker", anchor="daily-plans", divider="rainbow")
with st.expander("What is Daily Plans Maker?"):
    st.write("The Daily Plans Maker leverages Google's AI technology to craft personalized daily schedules tailored to your liking. Dustin assists in structuring a routine for you to adhere to.")
st.divider()

st.subheader("Enter your details to create your daily plans:")
with st.form(key="daily-plans-form"):
    schedule_type = st.selectbox("What is your schedule for today?*", ["Holiday", "Workday", "Weekend"])
    shift_start_time = st.time_input("When your shift starts (on Workdays)?*", datetime.time(9, 0))
    shift_end_time = st.time_input("When your shift ends (on Workdays)?*", datetime.time(17, 0))
    plan_type = st.multiselect("What type of plans would you like to create?*", ["Health Exercise", "Diet Plan", "Trip Plan"])
    any_other = st.text_area("Any other preferences or details you would like to add or Preplanned work?*", height=100, placeholder="Example: I want to go for a walk in the evening.")
    st.markdown("*Required**")
    submit_button = st.form_submit_button(label="Create Plans")

    if submit_button:
        if not schedule_type or not shift_start_time or not shift_end_time or not plan_type or not any_other:
            st.error("Please fill all the required fields.")
            st.stop()
        else:
            st.success("Please wait while Dustin is processing your request...")
st.divider()

with st.spinner("Processing your request..."):
    if schedule_type and shift_start_time and shift_end_time and plan_type and any_other is not None:
        st.subheader("Daily Plans:")
        prompt = f"""{prompts.system_instruction_daily_plans}\n\nToday is {schedule_type} (if schedule type is Holiday or Weekend, then ignore shift start and end) and my shift is from {shift_start_time} to {shift_end_time}. I would like to create a plan for {plan_type} and {any_other}."""
        response = model.generate_content(prompt)
        st.write(response.text)
    else:
        st.warning("Please fill all the required fields to create your daily plans.")
