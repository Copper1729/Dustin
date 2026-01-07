import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import json
import os
import requests

# Fix for AttributeError: module 'streamlit' has no attribute 'context'
# This ensures compatibility if Streamlit version is < 1.38.0
if not hasattr(st, 'context'):
    class MockContext:
        cookies = {}
    st.context = MockContext()

# 🔑 PASTE YOUR WEB API KEY HERE (From Firebase Console > Project Settings > General)
FIREBASE_WEB_API_KEY = "GEMINI_API_KEY"

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('firebase_api.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")

# Initialize session state for register page
def init_session_state():
    if 'register' not in st.session_state:
        st.session_state['register'] = False
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'user_data' not in st.session_state:
        st.session_state['user_data'] = {}

def show_login_form():
    st.subheader("Login")

    if st.session_state.get('registration_success'):
        st.success("User registered successfully! You can now log in.")
        st.session_state['registration_success'] = False

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            # 1. Lookup email from username using Admin SDK
            db = firestore.client()
            # Query users collection for the username
            docs = db.collection('users').where('username', '==', username).limit(1).stream()
            
            email = None
            for doc in docs:
                email = doc.to_dict().get('email')
            
            if not email:
                st.error("Login failed: Username not found.")
                return

            # Use Firebase REST API for Client-Side Login
            request_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
            payload = {"email": email, "password": password, "returnSecureToken": True}
            response = requests.post(request_url, json=payload)
            response.raise_for_status() # Raise error if login fails
            
            auth_data = response.json()
            st.session_state["authentication_status"] = True
            st.session_state["username"] = auth_data['email']
            st.session_state["user_data"] = get_user_data_from_firestore(auth_data['localId']) # Fetch user data from Firestore
            st.success("Logged in successfully!")
            st.rerun()
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('error', {}).get('message', 'Unknown error')
            
            if error_msg == "INVALID_EMAIL":
                st.error("Login failed: The email address is invalid. Please check for typos or spaces.")
            elif error_msg == "EMAIL_NOT_FOUND":
                st.error("Login failed: No account found with this email.")
            elif error_msg == "INVALID_PASSWORD":
                st.error("Login failed: Incorrect password.")
            elif error_msg == "CONFIGURATION_NOT_FOUND":
                st.error("Configuration Error: Email/Password Sign-in is disabled. Please go to Firebase Console > Authentication > Sign-in method and enable 'Email/Password'.")
            else:
                st.error(f"Login failed: {error_msg}")

        except Exception as e:
            if "Cloud Firestore API" in str(e) or "SERVICE_DISABLED" in str(e):
                st.error("Configuration Error: Firestore Database is not enabled. Please go to Firebase Console > Build > Firestore Database and click 'Create Database'.")
            else:
                st.error(f"Login failed: {e}")

    if st.session_state.get("authentication_status"):
        st.sidebar.write(f'Welcome **{st.session_state["user_data"].get("name", st.session_state["username"])}**👋')
        if st.sidebar.button("Logout"):
            st.session_state["authentication_status"] = False
            st.session_state["username"] = None
            st.session_state["user_data"] = {}
            st.success("Logged out successfully!")
            st.rerun()

    elif st.session_state.get("authentication_status") is False:
        st.error('Invalid email/password')
    elif st.session_state.get("authentication_status") is None:
        st.warning('Please login or register')

    # Only show the "Register" button if the user is NOT logged in
    if st.session_state["authentication_status"] is None or st.session_state["authentication_status"] == False:
        st.write("---")
        if st.button("Register"):
            st.session_state['register'] = True  # Switch to register page

# Define function to show the register form
def show_register_form():
    with st.container():
        st.subheader("Register")

        new_username = st.text_input("Enter Username")
        new_name = st.text_input("Enter Your Full Name")
        new_password = st.text_input("Enter Password", type="password")
        new_email = st.text_input("Enter your email")
        preferred_lang = st.selectbox("Preferred Language",  ["English","Japanese","Korean","Arabic","Bahasa Indonesia","Bengali","Bulgarian","Chinese (Simplified)","Chinese (Traditional)",
                                                            "Croatian","Czech","Danish","Dutch","Estonian","Farsi","Finnish","French","German","Gujarati","Greek","Hebrew","Hindi","Hungarian","Italian","Kannada","Latvian",
                                                            "Lithuanian","Malayalam","Marathi","Norwegian","Polish","Portuguese","Romanian","Russian","Serbian","Slovak","Slovenian","Spanish","Swahili","Swedish","Tamil",
                                                            "Telugu","Thai","Turkish","Ukrainian","Urdu","Vietnamese"])
        gender = st.selectbox("Enter Your Gender", ["Male", "Female", "Prefer not to say"])
        age = st.number_input("Enter Your Age", min_value=1, max_value=100)
        prob_facing = st.selectbox("Challenges you are navigating", [
            "Neurodiverse & Unique Minds", 
            "Visual Communicator (Hearing Differences)", 
            "Finding My Voice (Speech Differences)", 
            "Emotional Wellness Journey", 
            "Physical Strength Journey", 
            "None"
        ])
        chatbot_nickname = st.text_input("Enter Chatbot Nickname", placeholder="Ex: Dustin, HealthBot or Your Friend Name")

        if st.button("Submit Registration"):
            if new_username and new_password and new_email:
                try:
                    # 1. Create User in Firebase Authentication
                    user = auth.create_user(
                        email=new_email,
                        password=new_password,
                        display_name=new_name
                    )
                    
                    # 2. Save Additional Details to Firestore
                    db = firestore.client()
                    db.collection('users').document(user.uid).set({
                        'name': new_name,
                        'email': new_email,
                        'username': new_username,
                        'preferred_lang': preferred_lang,
                        'gender': gender,
                        'age': age,
                        'prob_facing': prob_facing,
                        'chatbot_nickname': chatbot_nickname,
                    })
                    
                    st.session_state['registration_success'] = True
                    st.session_state['register'] = False # Go back to login
                    st.rerun()
                    
                except Exception as e:
                    if "Cloud Firestore API" in str(e) or "SERVICE_DISABLED" in str(e):
                        st.error("Configuration Error: Firestore Database is not enabled. Please go to Firebase Console > Build > Firestore Database and click 'Create Database'.")
                    elif "CONFIGURATION_NOT_FOUND" in str(e):
                        st.error("Configuration Error: Email/Password Sign-in is disabled. Please go to Firebase Console > Authentication > Sign-in method and enable 'Email/Password'.")
                    else:
                        st.error(f"Registration failed: {e}")
            else:
                st.warning("Please fill in all required fields (Username, Password, Email).")
            
            # Add a "Back to Login" button to return to the login page
    if st.button("Back to Login"):
        st.session_state['register'] = False  # Return to login page

# Main section: Show either login or register form based on state
def authentication():
    init_session_state()
    if not st.session_state['authentication_status']:
        st.markdown("<h3 style='text-align: center;'>Hey Buddy! Say the magical words ✨</h3>", unsafe_allow_html=True)
    if st.session_state['register']:
        show_register_form()  # Show register form
    else:
        show_login_form()  # Show login form

# Get user details
def get_user_details():
    if st.session_state.get("authentication_status") and st.session_state.get("username"):
        # Assuming user_data is already fetched and stored in session_state upon login
        return st.session_state.get("user_data", {})
    return {}

def get_user_data_from_firestore(uid):
    db = firestore.client()
    return db.collection('users').document(uid).get().to_dict()