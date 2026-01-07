import streamlit as st
import requests
from features.functions import track_time_spent
from features.auth import get_user_details


# -------------------------------
#  AGE-BASED RECOMMENDATION LOGIC
# -------------------------------
def get_recommended_videos(age: int):
    # 1–3 years
    if 1 <= age <= 3:
        return [
            "https://www.youtube.com/watch?v=1GDFa-nEzlg", # Rock 'N Learn - Learn to Talk
            "https://youtu.be/gm_jm0DcNQk?si=nvl3stWhPL7wk0Un", # Rock 'N Learn - Alphabet
            "https://www.youtube.com/watch?v=pWepfJ-8XU0", # Bob The Train - Colors (Educational)
            "https://www.youtube.com/watch?v=03XgDWozJOw", # ChuChu TV - Numbers
            "https://youtu.be/tbbKjDjMDok?si=_hXvfcUwj-MqXQVa", # ChuChu TV - Fruits & Vegetables
        ]

    # 4–7 years
    if 4 <= age <= 7:
        return [
            "https://youtu.be/SEejivHRIbE?si=2nE4s2WgwY_tbrNV", # Numberblocks - Counting
            "https://youtu.be/X_tYrnv_o6A?si=Z6eWS1n9gL9PeEMb", # Alphablocks - Phonics
            "https://youtu.be/ctQfCUY1CdA?si=eo3he27Z3B_X3Kuz", # SciShow Kids - Health
            "https://youtu.be/SGxDv7XybSo?si=ZbuwWgQ34ZXmt7dI", # Nat Geo Kids - Dinosaurs
            "https://www.youtube.com/watch?v=w77zPAtVTuI", # Peekaboo Kidz - Pollution
        ]

    # 8–15 years
    if 8 <= age <= 15:
        return [
            "https://youtu.be/1lCOgFPtaZ4?si=LKQ8dm_iY55lQuZp", # Kurzgesagt - Immune System
            "https://youtu.be/FujWaPMS-n4?si=nWT_wBeT65dnReu4", # TED-Ed - Riddles
            "https://youtu.be/ZMQbHMgK2rw?si=IwHjXztgxSzJXB70", # CrashCourse - Physics
            "https://youtu.be/H6q6pYZ9Fho?si=yFKIIPL_5q1G5jNP", # Math Antics - Percentages
            "https://www.youtube.com/watch?v=R-sVnmmw6WY", # Veritasium - Science
        ]

    # 16–20 years
    if 16 <= age <= 20:
        return [
            "https://www.youtube.com/watch?v=aircAruvnKk",
            "https://www.youtube.com/watch?v=AfswKw-Sb6M",
            "https://www.youtube.com/watch?v=rfscVS0vtbw",
            "https://www.youtube.com/watch?v=oBt53YbR9Kk",
            "https://www.youtube.com/watch?v=WUvTyaaNkzM",
        ]

    # 21–25 years
    if 21 <= age <= 25:
        return [
            "https://youtu.be/CYlon2tvywA?si=aPnPeuYpXPbneS5e", # Osmosis - Medical Education
            "https://youtu.be/HdaRV5fExnA?si=9dZfutBlUJdXweej", # Ali Abdaal - Active Recall
            "https://www.youtube.com/live/WG4nr3VwE9E?si=xF0sfFY19jANJWuu", # Med School Insiders
            "https://youtu.be/8ZrsQNpHnVY?si=ABCNnBfNkq8NOqvW", # Harvard Business Review - Professional Skills
            "https://youtu.be/wexzvClUcUk?si=sLOZdYEwzIk5a1EZ", # TED - Stress Management
        ]

    # 25+ afterwards
    return [
        "https://youtu.be/h3M00JI8Iwo?si=AN9z7G0BwYLnwnz6", # Big Think - Expert Insights
        "https://youtu.be/-h8WpERG0pc?si=djfnzy8Nhe6iU7KP", # TED - Sleep
        "https://youtu.be/IMcmRi4FAmA?si=uQtKQXQsEF82GEBD", # Kurzgesagt - Life
        "https://youtu.be/hFL6qRIJZ_Y?si=WtL2gkr2eUSCg7Hb", # Huberman Lab - Focus
        "https://youtu.be/pGsbEd6w7PI?si=d5YNx1c06XK_M2yq", # World Economic Forum - Global Issues
    ]


# -------------------------------
#  MAIN PAGE
# -------------------------------
def study_time():
    # Track time spent
    track_time_spent('study_time_used')

    GOOGLE_API_KEY = "GEMINI_API_KEY"

    st.header("📚 Study Time", divider="rainbow")
    st.write("Search for educational videos — or watch the curated playlist below.")

    # ----------- SEARCH (now 5 results only) -----------
    search_query = st.text_input(
        "Enter a topic to study:",
        placeholder="e.g., Cardiology, Medical Ethics"
    )

    if search_query:
        with st.spinner("Searching YouTube..."):
            try:
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "maxResults": 5,      # <-- FIVE videos per search
                    "q": search_query,
                    "type": "video",
                    "key": GOOGLE_API_KEY,
                }

                response = requests.get(url, params=params)

                if response.status_code == 200:
                    results = response.json().get("items", [])

                    if not results:
                        st.info("No results found.")

                    st.subheader(f"Results for: {search_query}")

                    for item in results:
                        video_id = item["id"]["videoId"]
                        title = item["snippet"]["title"]
                        description = item["snippet"]["description"]

                        with st.expander(title):
                            st.write(description)
                            st.video(f"https://www.youtube.com/watch?v={video_id}")

                else:
                    msg = response.json().get("error", {}).get("message", "Unknown error")
                    st.error(f"YouTube API Error: {msg}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

    st.divider()

    # ----------------------------------------------------
    # AGE (normally comes from registration — placeholder for now)
    # ----------------------------------------------------
    user_data = get_user_details()
    if user_data and 'age' in user_data:
        age = user_data['age']
    else:
        age = 20

    st.info(f"Recommended videos based on age: **{age}**")

    # ----------- AUTOMATIC FEED -----------
    st.subheader("✨ Recommended For You")
    for link in get_recommended_videos(age):
        st.video(link)

    st.divider()

    # ----------- DEVELOPER-ONLY CURATED PLAYLIST -----------
    
    st.subheader("Have a Break🌱")

    playlist = [
        "https://www.youtube.com/watch?v=9bZkp7q19f0", # Gangnam Style
        "https://www.youtube.com/watch?v=hRi_Xrs73yw", # Mr Bean
        "https://www.youtube.com/watch?v=kJQP7kiw5Fk", # Despacito
    ]

    if not playlist:
        st.info("Playlist coming soon…")
    else:
        for link in playlist:
            st.video(link)


if __name__ == "__main__":
    study_time()
