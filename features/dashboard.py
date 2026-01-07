import streamlit as st
from features.auth import get_user_details
from features.functions import load_lottie_file
import streamlit_lottie as st_lottie
import yaml

def user_dashboard():
    user_data = get_user_details()
    name = user_data.get('name', 'N/A')

    if not user_data:
        st.warning("You need to log in to view your dashboard.")
        return

    st.header("🧑🏻‍⚕️User Dashboard", divider="rainbow")
    st.subheader(f"Welcome {name}, Here is your information:")

    # --- Progress Tracker Logic ---
    features_status = {
        "ChatBot": st.session_state.get("chatbot_used", False),
        "Symptom Checker": st.session_state.get("symptom_checker_used", False),
        "Daily Plans": st.session_state.get("daily_plans_used", False),
        "Daily Report": st.session_state.get("daily_report_used", False),
        "Mindful Games": st.session_state.get("games_used", False),
        "Study Time": st.session_state.get("study_time_used", False),
        "Contact Us": st.session_state.get("contact_us_used", False),
    }
    
    total_features = len(features_status)
    used_features = sum(features_status.values())
    progress = used_features / total_features

    with st.container(border=True):
        st.subheader("📊 Usage Progress", divider="rainbow")
        st.write("Track your journey through Dustin's features.")
        st.progress(progress, text=f"{int(progress * 100)}% Completed")
        
        if progress == 1.0:
            st.success("🎉 Amazing! You've explored all of Dustin's features!")
            st.balloons()
        else:
            cols = st.columns(4)
            for i, (feature, used) in enumerate(features_status.items()):
                with cols[i % 4]:
                    if used:
                        st.markdown(f"✅ **{feature}**")
                    else:
                        st.markdown(f"⬜ {feature}")

    with st.container(border=True):
        left_column, right_column = st.columns(2)
        with left_column:
            st.subheader("Personal Information", divider="rainbow")
            st.write(f"**Name:** {user_data.get('name', 'N/A')}")
            st.write(f"**Email:** {user_data.get('email', 'N/A')}")
            st.write(f"**Age:** {user_data.get('age', 'N/A')}")
            
            with st.expander("Edit Age"):
                current_age = user_data.get('age', 18)
                if not isinstance(current_age, int):
                    current_age = 18
                new_age = st.number_input("New Age", min_value=1, max_value=100, value=current_age)
                if st.button("Update Age"):
                    username = st.session_state.get("username")
                    if username:
                        with open('config.yaml', 'r', encoding='utf-8') as file:
                            config = yaml.safe_load(file)
                        config['credentials']['usernames'][username]['age'] = new_age
                        with open('config.yaml', 'w', encoding='utf-8') as file:
                            yaml.dump(config, file)
                        st.session_state['user_data']['age'] = new_age
                        st.success("Age updated successfully!")
                        st.rerun()

            st.write(f"**Gender:** {user_data.get('gender', 'N/A')}")
            st.write(f"**Preferred Language:** {user_data.get('preferred_lang', 'N/A')}")
        with right_column:
            if user_data.get('gender') == 'Male':
                male_profile = load_lottie_file('animations/male_profile.json')
                st_lottie.st_lottie(male_profile, key='male_profile', height=250, width=250, loop=True)
            else:
                female_profile = load_lottie_file('animations/female_profile.json')
                st_lottie.st_lottie(female_profile, key='female_profile', height=250, width=250, loop=True)

    with st.container(border=True):
        st.subheader("Professional Information", divider="rainbow")
        st.write(f"**Challenges Navigating:** {user_data.get('prob_facing', 'N/A')}")
    
    with st.container(border=True):
        st.subheader("🎮 Relaxation Zone", divider="rainbow")
        st.write("Feeling stressed? Take a break and play some mindful games.")
        st.page_link("features/5-Games.py", label="Go to Mindful Games", icon="🎮")

    with st.container(border=True):
        st.subheader("📚 Learning Zone", divider="rainbow")
        st.write("Want to learn something new? Check out our study resources.")
        st.page_link("features/6-StudyTime.py", label="Go to Study Time", icon="📚")

    with st.container(border=True):
        st.subheader("🎨 Creative Zone", divider="rainbow")
        st.write("Express yourself with quizzes, assignments, and a whiteboard.")
        st.page_link("features/7-funtime.py", label="Go to FunTime Zone", icon="🛝")

if __name__ == "__main__":
    user_dashboard()