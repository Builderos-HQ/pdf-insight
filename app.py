import streamlit as st
import fitz
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


# ==========================================
# Configuration
# ==========================================

load_dotenv()

client = OpenAI()


# ==========================================
# AI response structures
# ==========================================

class ScoreReason(BaseModel):
    points: int
    reason: str


class SkillMatch(BaseModel):
    skill: str
    matched: bool
    comment: str


class JobAnalysis(BaseModel):
    score: int
    decision: str
    score_reasons: list[ScoreReason]
    summary: list[str]
    conditions: list[str]
    warnings: list[str]
    next_actions: list[str]
    match_score: int
    match_summary: str
    skill_matches: list[SkillMatch]
    application_message: str


# ==========================================
# Page configuration
# ==========================================

st.set_page_config(
    page_title="PDF Insight",
    page_icon="📄",
    layout="wide",
)


# ==========================================
# Header / Branding
# ==========================================

st.title("📄 PDF Insight")

st.subheader(
    "Find the right jobs. Apply with confidence."
)

st.caption(
    "AI-powered freelance job screening"
)


# ==========================================
# Sidebar
# ==========================================

with st.sidebar:

    st.header("👤 Your Profile")

    user_skills = st.text_area(
        "Your skills",
        placeholder=(
            "Python\n"
            "Streamlit\n"
            "OpenAI API\n"
            "GitHub\n"
            "Web development"
        ),
        height=180,
    )

    st.caption(
        "Your skills are used to calculate Job Fit."
    )

    st.divider()

    st.caption("PDF Insight")

    st.caption(
        "AI-assisted job screening for freelancers."
    )


# ==========================================
# Upload section
# ==========================================

st.subheader("📄 Upload a Job")

uploaded_file = st.file_uploader(
    "Upload a freelance job PDF",
    type=["pdf"],
)


# ==========================================
# No file uploaded
# ==========================================

if uploaded_file is None:

    st.info(
        "👆 Upload a job PDF to get started."
    )


# ==========================================
# File uploaded
# ==========================================

else:

    st.success(
        f"✓ {uploaded_file.name}"
    )


    # --------------------------------------
    # Read PDF
    # --------------------------------------

    pdf = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf",
    )

    text = ""

    for page in pdf:
        text += page.get_text()


    st.caption(
        f"{len(pdf)} page(s) loaded"
    )


    # --------------------------------------
    # Analyze button
    # --------------------------------------

    analyze_button = st.button(
        "🤖 Analyze Job",
        type="primary",
        use_container_width=True,
    )


    # ======================================
    # AI analysis
    # ======================================

    if analyze_button:

        if not user_skills.strip():

            st.warning(
                "Please enter your skills in "
                "the sidebar first."
            )

            st.stop()


        with st.spinner(
            "Analyzing the job..."
        ):

            response = client.responses.parse(

                model="gpt-5",

                input=f"""
You are an AI freelance job screening assistant.

Analyze the following freelance job PDF.

Respond in Japanese because the user prefers
Japanese explanations.


========================================
JOB FIT SCORE
========================================

score:

Rate how attractive this job is for the user
from 1 to 10.

10 = excellent opportunity
1 = poor opportunity


========================================
DECISION
========================================

decision:

Choose exactly one:

- 応募する
- 検討する
- 応募しない


========================================
REASONS
========================================

score_reasons:

Provide reasons for the score.

Positive factors should have positive points.
Negative factors should have negative points.


========================================
IMPORTANT POINTS
========================================

summary:

Summarize the most important job information
in 3 to 5 points.


========================================
JOB CONDITIONS
========================================

conditions:

Extract useful information such as:

- compensation
- deadline
- required skills
- responsibilities
- working hours
- application requirements


========================================
WARNINGS
========================================

warnings:

Identify risks, unclear requirements,
or potential problems.


========================================
NEXT ACTIONS
========================================

next_actions:

Give up to 3 practical next steps.


========================================
SKILL MATCH
========================================

User skills:

{user_skills}


match_score:

Rate how well the user's skills match
the job from 0 to 100.


match_summary:

Explain the skill match.


skill_matches:

For important job skills provide:

skill:
skill name

matched:
true if the user has the skill,
false otherwise

comment:
short explanation


========================================
APPLICATION MESSAGE
========================================

application_message:

Write a concise and professional
application message for this job.

Use the user's actual skills.

Do not invent experience.

Do not claim skills the user did not provide.

Write in natural Japanese.


========================================
JOB PDF
========================================

{text}
""",

                text_format=JobAnalysis,
            )


            analysis = response.output_parsed


        # ==================================
        # Results
        # ==================================

        st.divider()

        st.header("🎯 Your Result")


        # ----------------------------------
        # Decision
        # ----------------------------------

        if analysis.decision == "応募する":

            st.success(
                "🟢 APPLY — This job looks "
                "worth applying to."
            )

        elif analysis.decision == "検討する":

            st.warning(
                "🟡 CONSIDER — Review the details "
                "before applying."
            )

        else:

            st.error(
                "🔴 SKIP — This job may not be "
                "a good fit."
            )


        # ==================================
        # Main scores
        # ==================================

        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "⭐ Job Fit",
                f"{analysis.score} / 10",
            )

            st.progress(
                analysis.score / 10
            )


        with col2:

            st.metric(
                "🎯 Skill Match",
                f"{analysis.match_score}%",
            )

            st.progress(
                analysis.match_score / 100
            )


        # ==================================
        # Why this score?
        # ==================================

        st.divider()

        st.subheader("💡 Why this score?")


        for item in analysis.score_reasons:

            if item.points > 0:

                st.write(
                    f"🟢 +{item.points}  "
                    f"{item.reason}"
                )

            else:

                st.write(
                    f"🔴 {item.points}  "
                    f"{item.reason}"
                )


        # ==================================
        # Skill match
        # ==================================

        st.divider()

        st.subheader("🧩 Skill Match")

        st.write(
            analysis.match_summary
        )


        for item in analysis.skill_matches:

            if item.matched:

                st.success(
                    f"✓ {item.skill} — "
                    f"{item.comment}"
                )

            else:

                st.warning(
                    f"⚠️ {item.skill} — "
                    f"{item.comment}"
                )


        # ==================================
        # Job summary
        # ==================================

        st.divider()

        st.subheader("📌 Key Points")


        for item in analysis.summary:

            st.write(
                f"• {item}"
            )


        # ==================================
        # Conditions / Warnings
        # ==================================

        st.divider()

        col1, col2 = st.columns(2)


        with col1:

            st.subheader("💼 Job Conditions")

            for item in analysis.conditions:

                st.write(
                    f"• {item}"
                )


        with col2:

            st.subheader("⚠️ Watch Out")

            for item in analysis.warnings:

                st.write(
                    f"• {item}"
                )


        # ==================================
        # Next steps
        # ==================================

        st.divider()

        st.subheader("🚀 Next Steps")


        for i, item in enumerate(
            analysis.next_actions,
            start=1,
        ):

            st.write(
                f"**{i}.** {item}"
            )


        # ==================================
        # AI Application
        # ==================================

        st.divider()

        st.header("✍️ AI Application")


        application = st.text_area(
            "Review and edit before sending",
            value=analysis.application_message,
            height=300,
        )


        st.info(
            "💡 Always review the application "
            "and make sure it accurately represents "
            "your experience."
        )


        # ==================================
        # Download application
        # ==================================

        st.download_button(
            label="📥 Download Application",
            data=application,
            file_name="application.txt",
            mime="text/plain",
            use_container_width=True,
        )


# ==========================================
# Footer
# ==========================================

st.divider()

st.caption(
    "PDF Insight • AI-powered freelance job screening"
)
