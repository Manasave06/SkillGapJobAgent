import os

import streamlit as st
import pandas as pd

from utils.pdf_reader import (
    extract_text_from_pdf
)

from agents.profile_agent import (
    extract_profile
)

from agents.matching_agent import (
    match_jobs
)

from agents.gap_agent import (
    explain_gap
)

from agents.training_agent import (
    recommend_courses,
    calculate_time_and_cost
)

from utils.scoring import (
    opportunity_unlock
)


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="SkillGap AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f7f8fc;
    }

    .hero {
        background: white;
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid #e5e7eb;
    }

    .hero-title {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .hero-text {
        color: #667085;
        font-size: 18px;
    }

    .card {
        background: white;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }

    .small-text {
        color: #667085;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "candidates" not in st.session_state:

    st.session_state.candidates = []


if "results" not in st.session_state:

    st.session_state.results = {}


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            🎯 SkillGap AI
        </div>

        <div class="hero-text">
            Transform resumes into actionable career intelligence.
            Discover skills, identify job gaps and build a
            personalized path to job readiness.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FEATURES
# =========================================================

st.subheader(
    "✨ What SkillGap AI does"
)

st.write(
    "One intelligent workflow from resume understanding "
    "to personalized career planning."
)

f1, f2, f3, f4 = st.columns(4)

with f1:

    st.markdown("### 📄 Resume Intelligence")

    st.write(
        "Extract education, skills, projects, "
        "certifications and experience."
    )


with f2:

    st.markdown("### 🎯 Job Matching")

    st.write(
        "Compare candidate skills with job "
        "requirements."
    )


with f3:

    st.markdown("### 🔍 Skill Gap Analysis")

    st.write(
        "Identify exactly which skills are "
        "missing for a job."
    )


with f4:

    st.markdown("### 🚀 Career Roadmap")

    st.write(
        "Get training, time, cost and a "
        "learning roadmap."
    )


st.divider()


# =========================================================
# UPLOAD
# =========================================================

st.subheader(
    "📄 Analyze Candidate Resumes"
)

st.write(
    "Upload multiple PDF resumes. "
    "All candidates will be analyzed."
)

uploaded_files = st.file_uploader(
    "Choose PDF resumes",
    type=["pdf"],
    accept_multiple_files=True
)


# =========================================================
# MANUAL PROFILE
# =========================================================

with st.expander(
    "✍️ Add a candidate manually"
):

    manual_name = st.text_input(
        "Candidate Name"
    )

    manual_skills = st.text_input(
        "Skills",
        placeholder="Python, SQL, HTML, CSS"
    )

    manual_location = st.text_input(
        "Location",
        placeholder="Bengaluru"
    )

    manual_education = st.text_input(
        "Education"
    )


# =========================================================
# ANALYZE ALL
# =========================================================

if st.button(
    "🚀 Analyze ALL Candidates",
    type="primary",
    use_container_width=True
):

    candidates = []

    results = {}

    # -----------------------------------------------------
    # PDF FILES
    # -----------------------------------------------------

    if uploaded_files:

        progress = st.progress(
            0,
            text="Starting analysis..."
        )

        total = len(
            uploaded_files
        )

        for number, file in enumerate(
            uploaded_files,
            start=1
        ):

            try:

                progress.progress(
                    (number - 1) / total,
                    text=(
                        f"Reading {file.name}..."
                    )
                )

                resume_text = (
                    extract_text_from_pdf(
                        file
                    )
                )

                if not resume_text.strip():

                    st.warning(
                        f"{file.name} has no readable text."
                    )

                    continue

                progress.progress(
                    (number - 0.5) / total,
                    text=(
                        f"Understanding "
                        f"{file.name}..."
                    )
                )

                profile = extract_profile(
                    resume_text
                )

                candidate_name = (
                    profile.get(
                        "name"
                    )
                    or file.name
                )

                candidate = {

                    "name":
                        candidate_name,

                    "location":
                        profile.get(
                            "location",
                            ""
                        ),

                    "education":
                        profile.get(
                            "education",
                            []
                        ),

                    "skills":
                        profile.get(
                            "skills",
                            []
                        ),

                    "projects":
                        profile.get(
                            "projects",
                            []
                        ),

                    "certifications":
                        profile.get(
                            "certifications",
                            []
                        ),

                    "interests":
                        profile.get(
                            "interests",
                            []
                        ),

                    "experience":
                        profile.get(
                            "experience",
                            []
                        ),

                    "source":
                        file.name
                }

                candidates.append(
                    candidate
                )

                progress.progress(
                    number / total,
                    text=(
                        f"Matching "
                        f"{candidate_name} "
                        f"with jobs..."
                    )
                )

                job_results = match_jobs(
                    candidate["skills"],
                    candidate["location"]
                )

                results[
                    candidate_name
                ] = job_results

            except Exception as error:

                st.error(
                    f"Error processing {file.name}"
                )

                st.exception(
                    error
                )

        progress.empty()


    # -----------------------------------------------------
    # MANUAL PROFILE
    # -----------------------------------------------------

    if (
        manual_name
        and manual_skills
    ):

        skills = [
            skill.strip()
            for skill in
            manual_skills.split(",")
            if skill.strip()
        ]

        candidate = {

            "name":
                manual_name,

            "location":
                manual_location,

            "education":
                [manual_education]
                if manual_education
                else [],

            "skills":
                skills,

            "projects": [],

            "certifications": [],

            "interests": [],

            "experience": [],

            "source":
                "Manual Profile"
        }

        candidates.append(
            candidate
        )

        results[
            manual_name
        ] = match_jobs(
            skills,
            manual_location
        )


    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    st.session_state.candidates = (
        candidates
    )

    st.session_state.results = (
        results
    )

    if candidates:

        st.success(
            f"✅ {len(candidates)} candidate(s) "
            "analyzed successfully."
        )

    else:

        st.warning(
            "No candidates were analyzed."
        )


# =========================================================
# DASHBOARD
# =========================================================

st.divider()

st.subheader(
    "📊 Career Intelligence Dashboard"
)

candidate_count = len(
    st.session_state.candidates
)

skill_count = len(
    set(
        skill
        for candidate
        in st.session_state.candidates
        for skill
        in candidate.get(
            "skills",
            []
        )
    )
)


try:

    jobs_count = len(
        pd.read_csv(
            "data/jobs.csv"
        )
    )

except Exception:

    jobs_count = 0


try:

    courses_count = len(
        pd.read_csv(
            "data/courses.csv"
        )
    )

except Exception:

    courses_count = 0


m1, m2, m3, m4 = st.columns(4)

with m1:

    st.metric(
        "Candidates Analyzed",
        candidate_count
    )

with m2:

    st.metric(
        "Unique Skills Detected",
        skill_count
    )

with m3:

    st.metric(
        "Job Opportunities",
        jobs_count
    )

with m4:

    st.metric(
        "Learning Resources",
        courses_count
    )


# =========================================================
# NO RESULTS
# =========================================================

if not st.session_state.candidates:

    st.info(
        "Upload multiple PDF resumes above "
        "and click Analyze ALL Candidates."
    )

    st.stop()


# =========================================================
# ALL CANDIDATES
# =========================================================

st.divider()

st.subheader(
    "👥 All Analyzed Candidates"
)

st.write(
    "Every uploaded resume is shown below."
)


candidate_tabs = st.tabs(
    [
        candidate["name"]
        for candidate
        in st.session_state.candidates
    ]
)


# =========================================================
# EACH CANDIDATE
# =========================================================

for tab, candidate in zip(
    candidate_tabs,
    st.session_state.candidates
):

    with tab:

        candidate_name = (
            candidate["name"]
        )

        jobs = (
            st.session_state.results.get(
                candidate_name,
                []
            )
        )

        # -------------------------------------------------
        # PROFILE
        # -------------------------------------------------

        st.markdown(
            "## 👤 Candidate Profile"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.write(
                "**Name:**",
                candidate["name"]
            )

            st.write(
                "**Location:**",
                candidate["location"]
                or
                "Not specified"
            )

            st.write(
                "**Education:**"
            )

            for education in candidate[
                "education"
            ]:

                st.write(
                    f"• {education}"
                )

        with c2:

            st.write(
                "**Skills:**"
            )

            if candidate["skills"]:

                st.write(
                    ", ".join(
                        candidate["skills"]
                    )
                )

            else:

                st.warning(
                    "No skills detected."
                )

        # -------------------------------------------------
        # PROJECTS
        # -------------------------------------------------

        if candidate["projects"]:

            with st.expander(
                "📁 Projects"
            ):

                for project in candidate[
                    "projects"
                ]:

                    if isinstance(
                        project,
                        dict
                    ):

                        title = project.get(
                            "title",
                            "Project"
                        )

                        description = (
                            project.get(
                                "description",
                                ""
                            )
                        )

                        st.markdown(
                            f"**{title}**"
                        )

                        if description:

                            st.write(
                                description
                            )

                    else:

                        st.write(
                            f"• {project}"
                        )

        # -------------------------------------------------
        # CERTIFICATIONS
        # -------------------------------------------------

        if candidate[
            "certifications"
        ]:

            with st.expander(
                "🏆 Certifications"
            ):

                for certification in (
                    candidate[
                        "certifications"
                    ]
                ):

                    st.write(
                        f"• {certification}"
                    )

        # -------------------------------------------------
        # JOB MATCHING
        # -------------------------------------------------

        st.markdown(
            "## 🎯 Job Matching"
        )

        if not jobs:

            st.warning(
                "No jobs found."
            )

            continue

        st.write(
            f"{len(jobs)} job opportunities "
            "were evaluated."
        )

        # -------------------------------------------------
        # JOB TABLE
        # -------------------------------------------------

        table_data = []

        for job in jobs:

            table_data.append(
                {
                    "Job":
                        job["title"],

                    "Company":
                        job["company"],

                    "Location":
                        job["location"],

                    "Match %":
                        f'{job["match_score"]:.1f}%',

                    "Skills Matched":
                        f'{len(job["matched_skills"])} / '
                        f'{len(job["required_skills"])}',

                    "Missing":
                        len(
                            job[
                                "missing_skills"
                            ]
                        )
                }
            )

        job_table = pd.DataFrame(
            table_data
        )

        st.dataframe(
            job_table,
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------------
        # TOP MATCHES
        # -------------------------------------------------

        st.markdown(
            "### 🎯 Job Match Details"
        )

        for position, job in enumerate(
            jobs[:5],
            start=1
        ):

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {position}. "
                    f"{job['title']}"
                )

                st.write(
                    f"🏢 {job['company']}  "
                    f"• 📍 {job['location']}"
                )

                st.progress(
                    int(
                        min(
                            job[
                                "match_score"
                            ],
                            100
                        )
                    )
                )

                st.metric(
                    "Job Match",
                    f'{job["match_score"]:.1f}%'
                )

                d1, d2 = st.columns(2)

                with d1:

                    st.write(
                        "### ✅ Matched Skills"
                    )

                    if job[
                        "matched_skills"
                    ]:

                        for skill in job[
                            "matched_skills"
                        ]:

                            st.write(
                                f"✓ {skill}"
                            )

                    else:

                        st.write(
                            "No required skills matched."
                        )

                with d2:

                    st.write(
                        "### ❌ Missing Skills"
                    )

                    if job[
                        "missing_skills"
                    ]:

                        for skill in job[
                            "missing_skills"
                        ]:

                            st.write(
                                f"• {skill}"
                            )

                    else:

                        st.success(
                            "No major skill gaps."
                        )


        # -------------------------------------------------
        # TARGET JOB
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "## 🔍 Detailed Skill Gap Analysis"
        )

        job_options = [
            job["title"]
            for job in jobs
        ]

        selected_title = st.selectbox(
            "Choose a target job",
            job_options,
            key=f"job_{candidate_name}"
        )

        selected_job = next(
            job
            for job in jobs
            if job["title"]
            == selected_title
        )

        st.metric(
            "Current Job Match",
            f'{selected_job["match_score"]:.1f}%'
        )

        # -------------------------------------------------
        # BREAKDOWN
        # -------------------------------------------------

        b1, b2, b3 = st.columns(3)

        with b1:

            st.metric(
                "Skill Coverage",
                f'{selected_job["skill_coverage"]:.1f}%'
            )

        with b2:

            st.metric(
                "Skills Matched",
                f'{len(selected_job["matched_skills"])} / '
                f'{len(selected_job["required_skills"])}'
            )

        with b3:

            st.metric(
                "Location Fit",
                f'{selected_job["location_fit"]:.0f}%'
            )

        # -------------------------------------------------
        # AI GAP ONLY WHEN REQUESTED
        # -------------------------------------------------

        if st.button(
            "🤖 Generate AI Gap Explanation",
            key=f"gap_{candidate_name}"
        ):

            with st.spinner(
                "Generating explanation..."
            ):

                explanation = explain_gap(
                    selected_job[
                        "title"
                    ],
                    selected_job[
                        "matched_skills"
                    ],
                    selected_job[
                        "missing_skills"
                    ]
                )

            st.markdown(
                explanation
            )

        # -------------------------------------------------
        # TRAINING
        # -------------------------------------------------

        st.markdown(
            "## 🎓 Training Path"
        )

        free_only = st.checkbox(
            "Only show free courses",
            key=f"free_{candidate_name}"
        )

        courses = recommend_courses(
            selected_job[
                "missing_skills"
            ],
            free_only
        )

        if courses:

            total_weeks, total_cost = (
                calculate_time_and_cost(
                    courses
                )
            )

            course_table = []

            for course in courses:

                course_table.append(
                    {
                        "Missing Skill":
                            course["skill"],

                        "Course":
                            course["course"],

                        "Provider":
                            course["provider"],

                        "Duration":
                            f'{course["duration_weeks"]} weeks',

                        "Cost":
                            f'₹{course["cost"]:,.0f}',

                        "Level":
                            course["level"]
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    course_table
                ),
                use_container_width=True,
                hide_index=True
            )

            tc1, tc2 = st.columns(2)

            with tc1:

                st.metric(
                    "Time to Ready",
                    f"{total_weeks} weeks"
                )

            with tc2:

                st.metric(
                    "Estimated Cost",
                    f"₹{total_cost:,.0f}"
                )

        else:

            st.info(
                "No course found for the identified skill gaps."
            )

        # -------------------------------------------------
        # ROADMAP
        # -------------------------------------------------

        st.markdown(
            "## 🗺️ 30 / 60 / 90 Day Roadmap"
        )

        r1, r2, r3 = st.columns(3)

        with r1:

            st.markdown(
                "### 📅 0–30 Days"
            )

            st.write(
                "Focus on the first priority "
                "missing skill."
            )

            st.write(
                "Build one small practical project."
            )

        with r2:

            st.markdown(
                "### 📅 31–60 Days"
            )

            st.write(
                "Learn the next required skill."
            )

            st.write(
                "Improve the project and GitHub portfolio."
            )

        with r3:

            st.markdown(
                "### 📅 61–90 Days"
            )

            st.write(
                "Close remaining skill gaps."
            )

            st.write(
                "Prepare resume and interview projects."
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🎯 SkillGap AI • Agentic AI Career Intelligence"
)