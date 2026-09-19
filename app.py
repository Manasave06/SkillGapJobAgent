import streamlit as st
import pandas as pd

from utils.pdf_reader import extract_text_from_pdf
from agents.profile_agent import extract_profile
from agents.matching_agent import match_jobs
from agents.gap_agent import explain_gap
from agents.training_agent import (
    recommend_courses,
    calculate_time_and_cost
)
from utils.scoring import opportunity_unlock


st.set_page_config(
    page_title="SkillGap AI",
    page_icon="🎯",
    layout="wide"
)


st.title("🎯 Skill-Gap-to-Job Matching Agent")

st.write(
    "AI-powered career assistant that analyzes your "
    "skills, finds suitable jobs, identifies skill gaps "
    "and creates a time-to-ready learning path."
)


# --------------------------------------------------
# INPUT
# --------------------------------------------------

st.header("1️⃣ Profile Input")

uploaded_file = st.file_uploader(
    "Upload your Resume PDF",
    type=["pdf"]
)

manual_text = st.text_area(
    "Or paste your profile/resume text here",
    height=200
)


if st.button("🚀 Analyze My Profile"):

    resume_text = ""

    if uploaded_file:

        with st.spinner("Reading resume..."):

            resume_text = extract_text_from_pdf(
                uploaded_file
            )

    elif manual_text.strip():

        resume_text = manual_text

    else:

        st.error(
            "Please upload a resume or paste your profile."
        )

        st.stop()


    # --------------------------------------------------
    # PROFILE
    # --------------------------------------------------

    with st.spinner(
        "AI is extracting your profile..."
    ):

        profile = extract_profile(
            resume_text
        )


    st.session_state["profile"] = profile


    st.success("Profile extracted successfully!")


# --------------------------------------------------
# DISPLAY PROFILE
# --------------------------------------------------

if "profile" in st.session_state:

    profile = st.session_state["profile"]

    st.header("👤 Your Profile")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            profile.get("name", "Candidate")
        )

        st.write("### Education")

        for item in profile.get(
            "education", []
        ):
            st.write("•", item)

    with col2:

        st.write("### Skills")

        st.write(
            ", ".join(
                profile.get("skills", [])
            )
        )


    # --------------------------------------------------
    # JOB MATCHING
    # --------------------------------------------------

    st.header("2️⃣ Job Matching")

    with st.spinner(
        "Matching your skills with jobs..."
    ):

        jobs = match_jobs(
            profile.get("skills", [])
        )


    for job in jobs:

        st.subheader(
            f"💼 {job['title']}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Match",
                f"{job['match_score']}%"
            )

        with col2:

            st.write("### Matched")

            st.write(
                ", ".join(
                    job["matched_skills"]
                )
            )

        with col3:

            st.write("### Missing")

            st.write(
                ", ".join(
                    job["missing_skills"]
                )
            )


    # --------------------------------------------------
    # SELECT JOB
    # --------------------------------------------------

    st.header("3️⃣ Target Job")

    job_names = [
        job["title"]
        for job in jobs
    ]

    selected_name = st.selectbox(
        "Choose a target job",
        job_names
    )

    selected_job = next(
        job for job in jobs
        if job["title"] == selected_name
    )


    # --------------------------------------------------
    # GAP ANALYSIS
    # --------------------------------------------------

    st.header("4️⃣ Skill Gap Analysis")

    explanation = explain_gap(
        selected_job["title"],
        selected_job["matched_skills"],
        selected_job["missing_skills"]
    )

    st.write(explanation)


    # --------------------------------------------------
    # OPPORTUNITY UNLOCK
    # --------------------------------------------------

    st.header(
        "5️⃣ 🚀 Opportunity Unlock Engine"
    )

    unlocks = opportunity_unlock(
        jobs,
        profile.get("skills", [])
    )

    if unlocks:

        unlock_df = pd.DataFrame(
            unlocks
        )

        st.dataframe(
            unlock_df,
            use_container_width=True
        )


    # --------------------------------------------------
    # TRAINING
    # --------------------------------------------------

    st.header(
        "6️⃣ 📚 Training Path"
    )

    free_only = st.checkbox(
        "🟢 Free courses only"
    )

    courses = recommend_courses(
        selected_job["missing_skills"],
        free_only=free_only
    )

    if courses:

        course_df = pd.DataFrame(
            courses
        )

        st.dataframe(
            course_df,
            use_container_width=True
        )

        total_weeks, total_cost = (
            calculate_time_and_cost(
                courses
            )
        )

        # --------------------------------------------------
        # TIME TO READY
        # --------------------------------------------------

        st.header(
            "7️⃣ ⏱️ Time-to-Ready"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Total Learning Time",
                f"{total_weeks} weeks"
            )

        with col2:

            st.metric(
                "Total Cost",
                f"₹{total_cost:,.0f}"
            )

        if total_cost == 0:

            st.success(
                "🟢 A free learning path is available!"
            )

    else:

        st.info(
            "No matching courses found for the "
            "selected skill gaps."
        )


    # --------------------------------------------------
    # PROJECT ACTION PLAN
    # --------------------------------------------------

    st.header(
        "8️⃣ 🗓️ Personalized Action Plan"
    )

    for i, course in enumerate(
        courses,
        start=1
    ):

        st.write(
            f"**Step {i}:** Learn "
            f"{course['skill']} — "
            f"{course['duration_weeks']} week(s)"
        )

    st.success(
        "Complete the missing skills, build a project "
        "using them, then re-run the assessment."
    )