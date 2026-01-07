import streamlit as st
import random
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import google.generativeai as genai

# 👉 Configure your Gemini API key (reuse your project key)
GEMINI_API_KEY = "GEMINI_API_KEY"  # replace or import from config

st.header("🎉 Fun Activity Zone", divider="rainbow")
st.write("Relax, learn, and express your creativity!")

# Tabs Layout
tabs = st.tabs(["🧠 Quiz Time", "📓 Assignments", "🎨 Whiteboard Challenge"])

# ============================================================
# 1️⃣ QUIZ TIME — 10 questions + progress + score
# ============================================================
with tabs[0]:
    st.subheader("🧠 Quiz Time")

    questions = [
        {"q": "Which planet is known as the Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "answer": "Mars"},
        {"q": "Who discovered gravity?", "options": ["Einstein", "Newton", "Tesla", "Curie"], "answer": "Newton"},
        {"q": "What is the powerhouse of the cell?", "options": ["Nucleus", "Ribosome", "Mitochondria", "Golgi"], "answer": "Mitochondria"},
        {"q": "What is H2O commonly known as?", "options": ["Hydrogen", "Water", "Oxygen", "Salt"], "answer": "Water"},
        {"q": "Which is the largest ocean?", "options": ["Atlantic", "Pacific", "Indian", "Arctic"], "answer": "Pacific"},
        {"q": "Which organ pumps blood?", "options": ["Lungs", "Heart", "Brain", "Liver"], "answer": "Heart"},
        {"q": "Which gas do plants absorb?", "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Helium"], "answer": "Carbon dioxide"},
        {"q": "Who invented the telephone?", "options": ["Edison", "Bell", "Newton", "Faraday"], "answer": "Bell"},
        {"q": "Which country is called the Land of the Rising Sun?", "options": ["China", "Japan", "Korea", "Thailand"], "answer": "Japan"},
        {"q": "How many continents are there?", "options": ["5", "6", "7", "8"], "answer": "7"},
    ]

    user_answers = []

    st.write("Answer all 10 questions:")

    for i, q in enumerate(questions):
        st.markdown(f"### {i+1}. {q['q']}")
        ans = st.radio("Choose:", q["options"], key=f"quiz_{i}")
        user_answers.append(ans)

    if st.button("Submit Quiz"):
        score = sum(1 for i, q in enumerate(questions) if user_answers[i] == q["answer"])
        st.progress(score / len(questions))
        st.success(f"🎯 Your Score: **{score}/{len(questions)}**")

        # Detailed feedback
        for i, q in enumerate(questions):
            if user_answers[i] == q["answer"]:
                st.write(f"✔ Q{i+1}: Correct")
            else:
                st.write(f"❌ Q{i+1}: Correct answer is **{q['answer']}**")


# ============================================================
# 2️⃣ ASSIGNMENTS — 5 prompts + AI positive feedback
# ============================================================
with tabs[1]:
    st.subheader("📓 Creative Assignments")

    prompts = [
        "Write a short essay on: A day that changed your life.",
        "Share an experience where you helped someone.",
        "Imagine a future city — describe it in 150 words.",
        "Describe a mistake that taught you something important.",
        "Explain a difficult topic in simple words.",
        "Write a motivational message to your future self.",
        "Describe your dream invention and why it matters.",
        "What is a skill you would like to learn and why?",
        "Describe your favorite memory from childhood.",
        "If you could have dinner with anyone, who would it be?",
        "What are three things you are grateful for today?",
        "Describe a place where you feel most relaxed.",
        "If you could travel anywhere in the world, where would you go?",
        "What is the best piece of advice you have ever received?",
    ]

    if "assignment_prompts" not in st.session_state:
        st.session_state.assignment_prompts = random.sample(prompts, 5)

    if st.button("🔄 Refresh Topics"):
        st.session_state.assignment_prompts = random.sample(prompts, 5)
        st.rerun()

    selected = st.session_state.assignment_prompts

    responses = []

    st.write("✍️ **Complete these 5 prompts:**")
    for i, p in enumerate(selected, 1):
        st.markdown(f"**{i}. {p}**")
        ans = st.text_area(f"Your Response #{i}", key=f"asg_{i}")
        responses.append(ans)

    if st.button("Get Feedback"):
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash")

            combined = "\n\n".join(responses)
            feedback = model.generate_content(
                f"""
                You are an encouraging mentor.
                Read the student's answers below and provide SHORT positive feedback only.

                Focus on:
                - effort
                - creativity
                - clarity
                - strengths you noticed

                Do NOT criticize or correct.

                Answers:
                {combined}
                """
            )

            st.success("⭐ Feedback:")
            st.write(feedback.text)
        except Exception as e:
            st.error(f"Feedback unavailable: {e}")


# ============================================================
# 3️⃣ WHITEBOARD — DRAW ON CANVAS (tools + shape overlay)
# ============================================================
with tabs[2]:
    st.subheader("🎨 Whiteboard Creativity Challenge")

    from PIL import Image, ImageDraw, ImageFont

    # -------- CONFIG --------
    shapes = ["2", "3", "S", "C", "triangle", "circle", "heart"]

    if "shape_choice" not in st.session_state:
        st.session_state.shape_choice = random.choice(shapes)

    chosen = st.session_state.shape_choice

    st.info(
        f"👉 Create something creative using **'{chosen}'** as part of the drawing!\n"
        "(Example: turning '2' into a swan 🦢)"
    )

    # --- draw the base shape image dynamically ---
    def make_shape_canvas(shape:str, w=700, h=400):
        img = Image.new("RGB", (w, h), "white")
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 180)
        except Exception:
            font = ImageFont.load_default()

        if shape in ["2", "3", "S", "C"]:
            d.text((w//2-50, h//2-90), shape, fill=(200, 200, 200), font=font)
        elif shape == "triangle":
            d.polygon([(w//2, 60), (120, h-60), (w-120, h-60)], outline=(180,180,180), width=5)
        elif shape == "circle":
            d.ellipse([(150, 60), (w-150, h-60)], outline=(180,180,180), width=5)
        elif shape == "heart":
            d.polygon([(w//2, h-70),(120,180),(w-120,180)], outline=(180,180,180), width=5)
        return img

    base_img = make_shape_canvas(chosen)

    # ---- drawing tools ----
    st.write("**🖌️ Draw directly here** — pick a pen color and start creating!")

    colA, colB, colC = st.columns(3)
    with colA:
        stroke_color = st.radio("Pen color", ["black", "red", "blue", "green"], index=0)
    with colB:
        stroke_width = st.slider("Pen width", 2, 15, 4)
    with colC:
        if st.button("🔀 New Random Shape"):
            st.session_state.shape_choice = random.choice(shapes)
            st.rerun()

    canvas = st_canvas(
        fill_color="rgba(0,0,0,0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image=None,
        update_streamlit=True,
        height=400,
        width=700,
        drawing_mode="freedraw",
        key="creative_canvas",
    )

    st.caption("Tip: The faint grey shape should become part of your drawing!")

    # ============================================================
    # Upload + Analyse drawing (Gemini Vision)
    # ============================================================
    st.write("\n📤 **Upload your saved drawing (optional) for AI analysis:**")
    uploaded = st.file_uploader("Upload drawing", type=["jpg", "jpeg", "png"])

    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="Your Drawing")

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash")

            result = model.generate_content([
                "Describe this drawing kindly. Highlight imagination and creativity without criticism.",
                img,
            ])

            st.success("✨ Dustin's thoughts:")
            st.write(result.text)
        except Exception as e:
            st.error(f"Image analysis unavailable: {e}")
