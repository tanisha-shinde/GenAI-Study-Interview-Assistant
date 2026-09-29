import streamlit as st
from google import genai
import json
import re

# ============================================================
# GENAI STUDY & INTERVIEW ASSISTANT
# ============================================================

st.set_page_config(
    page_title="GenAI Study & Interview Assistant",
    page_icon="🤖",
    layout="wide"
)

# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GOOGLE_API_KEY = "GOOGLE_API_KEY"

MODEL_NAME = "gemini-3.5-flash-lite"

if GOOGLE_API_KEY != "PASTE_YOUR_NEW_GEMINI_API_KEY_HERE":
    client = genai.Client(api_key=GOOGLE_API_KEY)
else:
    client = None


# ============================================================
# GEMINI FUNCTION
# ============================================================

def ask_gemini(prompt):

    if client is None:
        st.error("Please add your Gemini API key in GOOGLE_API_KEY.")
        return None

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        return response.text

    except Exception as e:
        st.error(f"Gemini Error: {e}")
        return None


# ============================================================
# SESSION STATE
# ============================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0


# ============================================================
# HEADER
# ============================================================

st.title("🤖 GenAI Study & Interview Assistant")

st.write(
    "An AI-powered learning and interview preparation platform "
    "built completely with Python and Streamlit."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Settings")

    mode = st.selectbox(
        "Choose Mode",
        [
            "📚 Learn Topic",
            "💼 Interview Questions",
            "🧠 MCQ Quiz",
            "📝 Evaluate My Answer",
            "🗺️ Study Roadmap",
            "🤖 AI Tutor Chat"
        ]
    )

    st.divider()

    st.info(
        "Tip: You can use topics such as Java, SQL, "
        "Spring Boot, DBMS, Embedded C, Electronics, "
        "VLSI, EV, Networking, Python or AI/ML."
    )


# ============================================================
# 1. LEARN TOPIC
# ============================================================

if mode == "📚 Learn Topic":

    st.header("📚 Learn Any Technical Topic")

    topic = st.text_input(
        "Enter Topic",
        placeholder="e.g., Java Exception Handling"
    )

    level = st.selectbox(
        "Your Level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    if st.button("🚀 Explain Topic", type="primary"):

        if not topic:
            st.warning("Please enter a topic.")
        else:

            prompt = f"""
You are a professional technical teacher.

Explain the following topic to a {level} student.

Topic:
{topic}

Follow this structure:

1. Simple Definition
2. Why It Is Used
3. Basic Concept
4. How It Works
5. Important Components
6. Simple Example
7. Real-World Application
8. Common Mistakes
9. Interview Questions
10. Quick Revision Points

Requirements:
- Use beginner-friendly language.
- Explain technical terms.
- Use examples wherever useful.
- Do not assume advanced knowledge.
- Keep the explanation organized.
"""

            with st.spinner("🤖 Generating explanation..."):

                result = ask_gemini(prompt)

            if result:
                st.markdown(result)


# ============================================================
# 2. INTERVIEW QUESTIONS
# ============================================================

elif mode == "💼 Interview Questions":

    st.header("💼 AI Interview Question Generator")

    col1, col2 = st.columns(2)

    with col1:

        role = st.text_input(
            "Job Role",
            placeholder="e.g., Java Backend Developer"
        )

    with col2:

        difficulty = st.selectbox(
            "Difficulty",
            ["Beginner", "Intermediate", "Advanced"]
        )

    topic = st.text_input(
        "Interview Topic",
        placeholder="e.g., Core Java / Spring Boot / SQL"
    )

    number = st.slider(
        "Number of Questions",
        5,
        20,
        10
    )

    if st.button("🎯 Generate Questions", type="primary"):

        if not role or not topic:
            st.warning("Please enter the job role and topic.")

        else:

            prompt = f"""
You are an experienced technical interviewer.

Generate {number} interview questions for:

Job Role:
{role}

Topic:
{topic}

Difficulty:
{difficulty}

For every question provide:

Question:
Answer:
Interview Tip:

Make the questions realistic for an actual technical interview.

Focus on understanding rather than memorization.
"""

            with st.spinner("🤖 Preparing interview questions..."):

                result = ask_gemini(prompt)

            if result:
                st.markdown(result)


# ============================================================
# 3. MCQ QUIZ
# ============================================================

elif mode == "🧠 MCQ Quiz":

    st.header("🧠 AI MCQ Quiz")

    topic = st.text_input(
        "Quiz Topic",
        placeholder="e.g., Java OOP"
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Beginner", "Intermediate", "Advanced"],
        key="quiz_difficulty"
    )

    number = st.slider(
        "Number of Questions",
        5,
        15,
        5,
        key="quiz_number"
    )

    if st.button("🎲 Generate Quiz", type="primary"):

        if not topic:
            st.warning("Please enter a topic.")

        else:

            prompt = f"""
Create a multiple-choice technical quiz.

Topic:
{topic}

Difficulty:
{difficulty}

Number of Questions:
{number}

Return ONLY valid JSON.

Use exactly this format:

[
  {{
    "question": "Question text",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": "Option A",
    "explanation": "Short explanation"
  }}
]

Rules:
- Exactly four options.
- Only one correct answer.
- Do not include markdown.
"""

            with st.spinner("🤖 Creating your quiz..."):

                result = ask_gemini(prompt)

            if result:

                try:

                    clean_result = result.strip()

                    clean_result = re.sub(
                        r"^```json\s*",
                        "",
                        clean_result,
                        flags=re.IGNORECASE
                    )

                    clean_result = re.sub(
                        r"^```\s*",
                        "",
                        clean_result
                    )

                    clean_result = re.sub(
                        r"\s*```$",
                        "",
                        clean_result
                    )

                    questions = json.loads(clean_result)

                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_score = 0

                    st.success("Quiz generated successfully!")

                except Exception as e:

                    st.error(
                        "The AI response could not be converted "
                        f"into a quiz. Error: {e}"
                    )


    # --------------------------------------------------------
    # DISPLAY QUIZ
    # --------------------------------------------------------

    if st.session_state.quiz_questions:

        st.divider()

        st.subheader("📝 Answer the Questions")

        for i, question in enumerate(
            st.session_state.quiz_questions
        ):

            st.markdown(
                f"### Question {i + 1}"
            )

            st.write(question["question"])

            selected = st.radio(
                "Choose your answer:",
                question["options"],
                key=f"question_{i}",
                index=None
            )

            st.session_state.quiz_answers[i] = selected

        if st.button(
            "✅ Submit Quiz",
            type="primary"
        ):

            score = 0

            for i, question in enumerate(
                st.session_state.quiz_questions
            ):

                user_answer = st.session_state.quiz_answers.get(i)

                if user_answer == question["answer"]:
                    score += 1

            st.session_state.quiz_score = score
            st.session_state.quiz_submitted = True

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        if st.session_state.quiz_submitted:

            total = len(
                st.session_state.quiz_questions
            )

            score = st.session_state.quiz_score

            percentage = (score / total) * 100

            st.divider()

            st.subheader("🎯 Quiz Result")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Score",
                    f"{score}/{total}"
                )

            with col2:
                st.metric(
                    "Accuracy",
                    f"{percentage:.0f}%"
                )

            with col3:

                if percentage >= 80:
                    level_result = "Excellent"
                elif percentage >= 60:
                    level_result = "Good"
                else:
                    level_result = "Needs Practice"

                st.metric(
                    "Result",
                    level_result
                )

            st.divider()

            st.subheader("📖 Answer Review")

            for i, question in enumerate(
                st.session_state.quiz_questions
            ):

                user_answer = st.session_state.quiz_answers.get(i)

                st.markdown(
                    f"**Question {i + 1}:** "
                    f"{question['question']}"
                )

                if user_answer == question["answer"]:

                    st.success(
                        f"Correct: {user_answer}"
                    )

                else:

                    st.error(
                        f"Your answer: {user_answer}"
                    )

                    st.info(
                        f"Correct answer: "
                        f"{question['answer']}"
                    )

                st.write(
                    f"Explanation: "
                    f"{question['explanation']}"
                )


# ============================================================
# 4. EVALUATE MY ANSWER
# ============================================================

elif mode == "📝 Evaluate My Answer":

    st.header("📝 AI Interview Answer Evaluator")

    question = st.text_area(
        "Interview Question",
        placeholder="e.g., What is polymorphism in Java?"
    )

    answer = st.text_area(
        "Your Answer",
        placeholder="Write your answer here..."
    )

    if st.button(
        "🔍 Evaluate Answer",
        type="primary"
    ):

        if not question or not answer:

            st.warning(
                "Please enter both the question and your answer."
            )

        else:

            prompt = f"""
You are a technical interview evaluator.

Evaluate the candidate's answer.

Interview Question:
{question}

Candidate Answer:
{answer}

Provide:

1. Score out of 10
2. What was correct
3. What was missing
4. Technical mistakes
5. Improved interview answer
6. One follow-up question

Be constructive and beginner-friendly.
"""

            with st.spinner("🤖 Evaluating your answer..."):

                result = ask_gemini(prompt)

            if result:
                st.markdown(result)


# ============================================================
# 5. STUDY ROADMAP
# ============================================================

elif mode == "🗺️ Study Roadmap":

    st.header("🗺️ Personalized Study Roadmap")

    goal = st.text_input(
        "Your Career Goal",
        placeholder="e.g., Java Backend Developer"
    )

    current_level = st.selectbox(
        "Current Level",
        [
            "Complete Beginner",
            "Beginner",
            "Intermediate"
        ]
    )

    study_time = st.selectbox(
        "Study Time Per Day",
        [
            "1 hour",
            "2 hours",
            "3 hours",
            "4+ hours"
        ]
    )

    duration = st.selectbox(
        "Roadmap Duration",
        [
            "15 days",
            "30 days",
            "60 days",
            "90 days"
        ]
    )

    if st.button(
        "🗺️ Generate Roadmap",
        type="primary"
    ):

        if not goal:

            st.warning("Please enter your career goal.")

        else:

            prompt = f"""
Create a personalized technical learning roadmap.

Career Goal:
{goal}

Current Level:
{current_level}

Study Time:
{study_time} per day

Duration:
{duration}

Create a practical roadmap containing:

1. Prerequisites
2. Topics in learning order
3. Daily/weekly plan
4. Practice tasks
5. Mini projects
6. Interview preparation
7. Revision strategy
8. Final project suggestion

Make it realistic for a student.

Explain why each major topic is required.
"""

            with st.spinner("🤖 Creating your roadmap..."):

                result = ask_gemini(prompt)

            if result:
                st.markdown(result)


# ============================================================
# 6. AI TUTOR CHAT
# ============================================================

elif mode == "🤖 AI Tutor Chat":

    st.header("🤖 AI Tutor")

    st.write(
        "Ask questions about programming, electronics, "
        "AI, databases, networking, interviews and more."
    )

    # Display previous messages

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    user_message = st.chat_input(
        "Ask your technical question..."
    )

    if user_message:

        # Display user message

        with st.chat_message("user"):

            st.markdown(user_message)

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        # Build conversation context

        conversation = ""

        for message in st.session_state.chat_history:

            conversation += (
                f"{message['role'].upper()}: "
                f"{message['content']}\n"
            )

        prompt = f"""
You are an AI technical tutor.

The student is learning technical subjects
and prefers simple, beginner-friendly explanations.

Conversation:

{conversation}

Answer the student's latest question.

Rules:
- Explain from basics.
- Use examples.
- Avoid unnecessary complexity.
- If the topic is programming, include simple code when useful.
- If the student asks an interview question, provide an interview-ready answer.
- Correct misunderstandings politely.
"""

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                response = ask_gemini(prompt)

            if response:

                st.markdown(response)

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "GenAI Study & Interview Assistant | "
    "Python + Streamlit + Gemini"
)