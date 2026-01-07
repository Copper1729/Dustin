import streamlit as st
from features.auth import get_user_details
import csv
import os
from datetime import datetime
import json
import streamlit.components.v1 as components
from features.functions import track_time_spent
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def contact_us():

    track_time_spent('contact_us_used')

    user_data = get_user_details()

    if not user_data:
        st.warning("You need to log in to view your dashboard.")
        return

    # defaults for form
    name = user_data.get('name', 'N/A')
    email = user_data.get('email', 'N/A')

    # safe fallback values for booking system
    patient_name = user_data.get("name") or "Unknown User"
    patient_email = user_data.get("email") or "Not Provided"

    st.header("📞 Contact Us", divider="rainbow")
    st.write("Your input and questions are important to us. Complete the form below to contact us.")

    # ------------------- FEEDBACK FORM -------------------
    with st.form("contact_form"):
        name = st.text_input("Your Name*", value=name)
        email = st.text_input("Your Email*", value=email)
        rate_us = st.selectbox("Rate Us*", ["Excellent", "Good", "Average", "Poor"])
        subject = st.text_input("Subject*", placeholder="Enter the subject of your message")
        message = st.text_area("Message*", placeholder="Enter your message here", height=200)

        st.markdown("*Required**")
        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if not name or not email or not subject or not message or not rate_us:
            st.error("Please fill out all fields.")
        else:
            file_exists = os.path.isfile('feedback.csv')

            with open('feedback.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Timestamp', 'Name', 'Email', 'Rating', 'Subject', 'Message'])

                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    name,
                    email,
                    rate_us,
                    subject,
                    message
                ])

            payload = {
                "access_key": "481708d1-d17b-455a-a567-34ddf76a5fed",
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
                "rating": rate_us
            }

            components.html(f"""
                <script>
                    const data = {json.dumps(payload)};
                    fetch("https://api.web3forms.com/submit", {{
                        method: "POST",
                        headers: {{
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        }},
                        body: JSON.stringify(data)
                    }})
                    .then(async (response) => {{
                        const result = await response.json();
                        if (response.status == 200) {{
                            document.getElementById("status").innerHTML =
                                "Thank you for your feedback! We will get back to you soon.";
                            document.getElementById("status").style.color = "green";
                        }} else {{
                            document.getElementById("status").innerHTML = "Error: " + result.message;
                            document.getElementById("status").style.color = "red";
                        }}
                    }})
                    .catch(error => {{
                        document.getElementById("status").innerHTML = "Something went wrong!";
                        document.getElementById("status").style.color = "red";
                    }});
                </script>
                <div id="status" style="font-family: sans-serif; font-weight: bold;">
                    Sending feedback...
                </div>
            """, height=60)

    # ------------------- COUNSELOR APPOINTMENTS -------------------
    st.divider()
    st.subheader("🩺 Talk to a Counselor or Doctor")

    counselors = [
        {"name": "Dr. Ayush Karnewar", "role": "Psychologist",
         "desc": "Specializes in stress, anxiety and student well-being.",
         "image": "https://cdn-icons-png.flaticon.com/512/387/387561.png",
         "email": "ayushkarnewar1729@gmail.com"}, # Replace with actual email

        {"name": "Dr. Ritwik Kanojia", "role": "General Physician",
         "desc": "Helps with lifestyle, sleep, fatigue and health advice.",
         "image": "https://cdn-icons-png.flaticon.com/512/2922/2922510.png",
         "email": "ritwik1507@gmail.com"}, # Replace with actual email

        {"name": "Dr. Saniya Sayyad", "role": "Mental Health Counselor",
         "desc": "Friendly therapy talk sessions and emotional support.",
         "image": "https://cdn-icons-png.flaticon.com/512/2922/2922565.png",
         "email": "saniyasayyad788@gmail.com"}, # Replace with actual email

        {
    "name": "Dr. Sonali Patil",
    "role": "Child & Adolescent Counselor",
    "desc": "Supports emotional well-being, exam stress, and confidence building.",
    "image": "https://cdn-icons-png.flaticon.com/512/2922/2922561.png",
    "email": "patilsonali5161@gmail.com" # Replace with actual email

},
    ]

    cols = st.columns(4)

    for i, doc in enumerate(counselors):
        with cols[i]:
            st.image(doc["image"], width=120)
            st.markdown(f"### {doc['name']}")
            st.write(f"**{doc['role']}**")
            st.write(doc["desc"])

            with st.expander("📅 Book Appointment"):
                date = st.date_input("Select Date", key=f"date_{i}")
                time = st.time_input("Select Time", key=f"time_{i}")
                reason = st.text_area("Reason for visit", key=f"reason_{i}")

                if st.button(f"Book with {doc['name']}", key=f"book_{i}"):
                    if not reason:
                        st.warning("Please briefly describe your reason.")
                    else:
                        file_exists = os.path.isfile("appointments.csv")

                        with open("appointments.csv", "a", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)

                            if not file_exists:
                                writer.writerow([
                                    "Timestamp", "Patient", "Email",
                                    "Doctor", "Role", "Date", "Time", "Reason"
                                ])

                            writer.writerow([
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                patient_name,
                                patient_email,
                                doc["name"],
                                doc["role"],
                                date,
                                time.strftime("%H:%M"),
                                reason
                            ])

                        # Send email notification via SMTP
                        sender_email = os.getenv("SENDER_EMAIL")
                        sender_password = os.getenv("SENDER_PASSWORD")
                        
                        if not sender_email or not sender_password:
                            st.error("⚠️ Email credentials missing. Please set SENDER_EMAIL and SENDER_PASSWORD in your .env file.")
                        else:
                            try:
                                msg = MIMEMultipart()
                                msg['From'] = sender_email
                                msg['To'] = doc['email']
                                msg['Subject'] = f"New Appointment Request: {doc['name']}"
                                
                                body = f"Patient: {patient_name}\nEmail: {patient_email}\nDoctor: {doc['name']}\nRole: {doc['role']}\nDate: {date}\nTime: {time}\nReason: {reason}"
                                msg.attach(MIMEText(body, 'plain'))
                                
                                # Using Gmail's SMTP server by default
                                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                                    server.starttls()
                                    server.login(sender_email, sender_password)
                                    server.send_message(msg)
                            except smtplib.SMTPAuthenticationError:
                                st.error("⚠️ Authentication failed. Please ensure you are using a Google **App Password**, not your regular login password.")
                            except Exception as e:
                                st.error(f"Could not send email: {e}")

                        st.success(f"✅ Appointment booked with **{doc['name']}**")
                        st.balloons()


if __name__ == "__main__":
    contact_us()
