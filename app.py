import os
import streamlit as st
import pandas as pd

from dotenv import load_dotenv

from utils.pdf_reader import extract_text_from_pdf
from agents.profile_agent import extract_profile
from agents.matching_agent import match_jobs
from agents.gap_agent import explain_gap
from agents.training_agent import (
    recommend_courses,
    calculate_time_and_cost
)
from utils.scoring import opportunity_unlock


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="SkillGap AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background: #f6f8fc;
}

.block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}


/* ================= HERO ================= */

.hero {
    padding: 38px 42px;
    border-radius: 24px;
    margin-bottom: 30px;

    background: linear-gradient(
        135deg,
        #111827 0%,
        #1e3a8a 50%,
        #4f46e5 100%
    );

    color: white;

    box-shadow:
        0 12px 35px rgba(30, 58, 138, 0.18);
}

.hero-badge {
    display: inline-block;

    padding: 6px 14px;

    border-radius: 20px;

    background: rgba(255,255,255,0.15);

    font-size: 13px;

    margin-bottom: 15px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;

    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 18px;

    opacity: 0.92;

    max-width: 760px;

    line-height: 1.6;
}


/* ================= SECTION ================= */

.section-title {
    font-size: 26px;

    font-weight: 750;

    color: #111827;

    margin-top: 25px;

    margin-bottom: 8px;
}

.section-subtitle {
    color: #6b7280;

    font-size: 15px;

    margin-bottom: 20px;
}


/* ================= FEATURE CARDS ================= */

.feature-card {
    background: white;

    border-radius: 18px;

    padding: 22px;

    border: 1px solid #e5e7eb;

    box-shadow:
        0 5px 18px rgba(0,0,0,0.05);

    min-height: 155px;
}

.feature-icon {
    font-size: 28px;

    margin-bottom: 8px;
}

.feature-title {
    font-weight: 700;

    font-size: 17px;

    color: #111827;

    margin-bottom: 7px;
}

.feature-text {
    color: #6b7280;

    font-size: 14px;

    line-height: 1.5;
}


/* ================= METRIC CARDS ================= */

.metric-card {
    background: white;

    border-radius: 18px;

    padding: 20px;

    border: 1px solid #e5e7eb;

    text-align: center;

    box-shadow:
        0 5px 18px rgba(0,0,0,0.04);
}

.metric-number {
    font-size: 32px;

    font-weight: 800;

    color: #4f46e5;
}

.metric-label {
    color: #6b7280;

    font-size: 14px;
}


/* ================= CANDIDATE CARD ================= */

.candidate-card {
    background: white;

    padding: 22px;

    border-radius: 18px;

    border: 1px solid #e5e7eb;

    box-shadow:
        0 5px 18px rgba(0,0,0,0.04);

    margin-bottom: 15px;
}

.candidate-name {
    font-size: 20px;

    font-weight: 750;

    color: #111827;
}

.candidate-file {
    color: #6b7280;

    font-size: 13px;
}

.match-score {
    font-size: 30px;

    font-weight: 800;

    color: #4f46e5;
}


/* ================= JOB CARD ================= */

.job-card {
    background: white;

    border-radius: 18px;

    padding: 20px;

    border: 1px solid #e5e7eb;

    margin-bottom: 15px;

    box-shadow:
        0 5px 15px rgba(0,0,0,0.04);
}


/* ================= SKILL TAGS ================= */

.skill-tag {
    display: inline-block;

    padding: 6px 10px;

    margin: 4px;

    border-radius: 15px;

    background: #eef2ff;

    color: #3730a3;

    font-size: 13px;
}

.missing-tag {
    display: inline-block;

    padding: 6px 10px;

    margin: 4px;

    border-radius: 15px;

    background: #fff1f2;

    color: #be123c;

    font-size: 13px;
}


/* ================= BUTTONS ================= */

.stButton > button {
    border-radius: 10px;

    font-weight: 650;
}


/* ================= DIVIDERS ================= */

hr {
    margin-top: 25px;

    margin-bottom: 25px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "candidates" not in st.session_state:
    st.session_state.candidates = []

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "upload_version" not in st.session_state:
    st.session_state.upload_version = 0


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🎯 SkillGap AI")

    st.markdown(
        "### Career Intelligence Agent"
    )

    st.markdown("---")

    st.markdown("""
    **Pipeline**

    📄 Resume Understanding

    ↓

    🧠 Skill Extraction

    ↓

    🎯 Job Matching

    ↓

    🔍 Skill Gap Analysis

    ↓

    🚀 Opportunity Unlock

    ↓

    📚 Training Path

    ↓

    ⏱️ Time-to-Ready
    """)

    st.markdown("---")

    if st.button(
        "🔄 Start New Analysis",
        use_container_width=True
    ):

        st.session_state.candidates = []
        st.session_state.analysis_done = False
        st.session_state.upload_version += 1

        st.rerun()


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

    <div class="hero-badge">
        🤖 AGENTIC AI • CAREER INTELLIGENCE
    </div>

    <div class="hero-title">
        🎯 SkillGap AI
    </div>

    <div class="hero-subtitle">
        Transform resumes into actionable career intelligence.
        Discover candidate skills, identify job-specific gaps,
        and build a personalized path to job readiness.
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# FEATURES
# ============================================================

st.markdown("""
<div class="section-title">
    ✨ What SkillGap AI does
</div>

<div class="section-subtitle">
    One intelligent workflow from resume understanding to personalized career planning.
</div>
""", unsafe_allow_html=True)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown("""
    <div class="feature-card">

        <div class="feature-icon">📄</div>

        <div class="feature-title">
            Resume Intelligence
        </div>

        <div class="feature-text">
            Extract education, skills, projects,
            certifications and experience automatically.
        </div>

    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown("""
    <div class="feature-card">

        <div class="feature-icon">🎯</div>

        <div class="feature-title">
            Job Matching
        </div>

        <div class="feature-text">
            Compare candidate skills with
            relevant job requirements.
        </div>

    </div>
    """, unsafe_allow_html=True)


with col3:

    st.markdown("""
    <div class="feature-card">

        <div class="feature-icon">🔍</div>

        <div class="feature-title">
            Skill Gap Analysis
        </div>

        <div class="feature-text">
            Identify the exact skills missing
            for target job opportunities.
        </div>

    </div>
    """, unsafe_allow_html=True)


with col4:

    st.markdown("""
    <div class="feature-card">

        <div class="feature-icon">🚀</div>

        <div class="feature-title">
            Career Roadmap
        </div>

        <div class="feature-text">
            Get courses, learning time,
            cost and an actionable career path.
        </div>

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# RESUME UPLOAD
# ============================================================

st.markdown("""
<div class="section-title">
    📄 Analyze Candidate Resumes
</div>

<div class="section-subtitle">
    Upload one or more PDF resumes. Each candidate is analyzed independently
    against the same job intelligence.
</div>
""", unsafe_allow_html=True)


uploaded_files = st.file_uploader(
    "Choose PDF resumes",
    type=["pdf"],
    accept_multiple_files=True,
    key=f"resume_uploader_{st.session_state.upload_version}",
    help="Upload one or multiple candidate resumes."
)


# ============================================================
# MANUAL PROFILE
# ============================================================

with st.expander(
    "✍️ Or enter a candidate profile manually"
):

    manual_name = st.text_input(
        "Candidate name"
    )

    manual_location = st.text_input(
        "Location"
    )

    manual_skills = st.text_area(
        "Skills",
        placeholder="Python, SQL, HTML, CSS, Git..."
    )

    manual_education = st.text_input(
        "Education"
    )

    manual_interests = st.text_input(
        "Interests"
    )

    if st.button(
        "➕ Add Manual Candidate"
    ):

        if manual_name and manual_skills:

            skills = [
                x.strip()
                for x in manual_skills.split(",")
                if x.strip()
            ]

            candidate = {
                "name": manual_name,
                "filename": "Manual Profile",
                "profile": {
                    "name": manual_name,
                    "location": manual_location,
                    "education": [manual_education]
                    if manual_education else [],
                    "skills": skills,
                    "projects": [],
                    "certifications": [],
                    "interests": [manual_interests]
                    if manual_interests else [],
                    "experience": []
                }
            }

            candidate["jobs"] = match_jobs(
                skills,
                manual_location
            )

            st.session_state.candidates.append(
                candidate
            )

            st.session_state.analysis_done = True

            st.success(
                "Candidate added successfully!"
            )

            st.rerun()


# ============================================================
# PROCESS RESUMES
# ============================================================

if uploaded_files:

    already_processed = {
        candidate["filename"]
        for candidate in st.session_state.candidates
    }

    new_files = [
        file
        for file in uploaded_files
        if file.name not in already_processed
    ]

    if new_files:

        progress = st.progress(0)

        status = st.empty()

        total_files = len(new_files)

        for index, uploaded_file in enumerate(new_files):

            try:

                status.info(
                    f"Analyzing {uploaded_file.name}..."
                )

                resume_text = extract_text_from_pdf(
                    uploaded_file
                )

                if not resume_text.strip():

                    st.warning(
                        f"No readable text found in {uploaded_file.name}."
                    )

                    continue

                profile = extract_profile(
                    resume_text
                )

                location = profile.get(
                    "location",
                    ""
                )

                skills = profile.get(
                    "skills",
                    []
                )

                jobs = match_jobs(
                    skills,
                    location
                )

                candidate = {
                    "name": profile.get(
                        "name",
                        "Unknown Candidate"
                    ),
                    "filename": uploaded_file.name,
                    "profile": profile,
                    "jobs": jobs
                }

                st.session_state.candidates.append(
                    candidate
                )

            except Exception as e:

                st.error(
                    f"Error processing {uploaded_file.name}: {e}"
                )

            progress.progress(
                (index + 1) / total_files
            )

        status.success(
            f"Finished analyzing {len(new_files)} resume(s)."
        )

        st.session_state.analysis_done = True


# ============================================================
# DASHBOARD
# ============================================================

st.markdown("---")

st.markdown("""
<div class="section-title">
    📊 Career Intelligence Dashboard
</div>
""", unsafe_allow_html=True)


candidate_count = len(
    st.session_state.candidates
)

all_skills = set()

for candidate in st.session_state.candidates:

    for skill in candidate["profile"].get(
        "skills",
        []
    ):

        all_skills.add(
            skill.lower()
        )


try:

    jobs_df = pd.read_csv(
        "data/jobs.csv"
    )

    job_count = len(jobs_df)

except:

    job_count = 0


try:

    courses_df = pd.read_csv(
        "data/courses.csv"
    )

    course_count = len(courses_df)

except:

    course_count = 0


c1, c2, c3, c4 = st.columns(4)


with c1:

    st.markdown(f"""
    <div class="metric-card">

        <div class="metric-number">
            {candidate_count}
        </div>

        <div class="metric-label">
            Candidates Analyzed
        </div>

    </div>
    """, unsafe_allow_html=True)


with c2:

    st.markdown(f"""
    <div class="metric-card">

        <div class="metric-number">
            {len(all_skills)}
        </div>

        <div class="metric-label">
            Skills Detected
        </div>

    </div>
    """, unsafe_allow_html=True)


with c3:

    st.markdown(f"""
    <div class="metric-card">

        <div class="metric-number">
            {job_count}
        </div>

        <div class="metric-label">
            Job Opportunities
        </div>

    </div>
    """, unsafe_allow_html=True)


with c4:

    st.markdown(f"""
    <div class="metric-card">

        <div class="metric-number">
            {course_count}
        </div>

        <div class="metric-label">
            Learning Resources
        </div>

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# NO CANDIDATES
# ============================================================

if not st.session_state.candidates:

    st.info(
        "Upload a PDF resume above to start the career analysis."
    )

    st.stop()


# ============================================================
# CANDIDATE SELECTOR
# ============================================================

st.markdown("---")

st.markdown("""
<div class="section-title">
    👥 Candidate Analysis
</div>

<div class="section-subtitle">
    Select a candidate to explore their career intelligence.
</div>
""", unsafe_allow_html=True)


candidate_names = []

for i, candidate in enumerate(
    st.session_state.candidates
):

    display_name = candidate["name"]

    if not display_name:

        display_name = f"Candidate {i + 1}"

    candidate_names.append(
        f"{i + 1}. {display_name}"
    )


selected_candidate_label = st.selectbox(
    "Select candidate",
    candidate_names
)


selected_index = candidate_names.index(
    selected_candidate_label
)

candidate = st.session_state.candidates[
    selected_index
]

profile = candidate["profile"]

jobs = candidate["jobs"]


# ============================================================
# CANDIDATE SUMMARY
# ============================================================

st.markdown("""
<div class="candidate-card">
""", unsafe_allow_html=True)

left, middle, right = st.columns(
    [2, 2, 1]
)


with left:

    st.markdown(
        f"""
        <div class="candidate-name">
            👤 {candidate["name"]}
        </div>

        <div class="candidate-file">
            📄 {candidate["filename"]}
        </div>
        """,
        unsafe_allow_html=True
    )


with middle:

    location = profile.get(
        "location",
        ""
    )

    if location:

        st.write(
            f"📍 **Location:** {location}"
        )

    education = profile.get(
        "education",
        []
    )

    if education:

        st.write(
            f"🎓 **Education:** {education[0]}"
        )


with right:

    if jobs:

        top_score = jobs[0]["match_score"]

    else:

        top_score = 0

    st.markdown(
        f"""
        <div class="match-score">
            {top_score:.1f}%
        </div>

        <div>
            Top Skill Match
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# DETECTED SKILLS
# ============================================================

st.markdown("""
<div class="section-title">
    🧠 Detected Skills
</div>
""", unsafe_allow_html=True)


skills = profile.get(
    "skills",
    []
)


if skills:

    skill_html = ""

    for skill in skills:

        skill_html += (
            f'<span class="skill-tag">'
            f'{skill}'
            f'</span>'
        )

    st.markdown(
        skill_html,
        unsafe_allow_html=True
    )

else:

    st.info(
        "No technical skills were detected."
    )


# ============================================================
# JOB MATCHING
# ============================================================

st.markdown("---")

st.markdown("""
<div class="section-title">
    🎯 Job Opportunity Matching
</div>

<div class="section-subtitle">
    Jobs are matched using normalized skills and semantic similarity.
</div>
""", unsafe_allow_html=True)


if jobs:

    top_jobs = jobs[:5]

    for job in top_jobs:

        score = job["match_score"]

        st.markdown(
            f"""
            <div class="job-card">

                <h3>
                    {job["title"]}
                </h3>

                <p>
                    🏢 {job["company"]}
                    &nbsp;&nbsp;
                    📍 {job["location"]}
                </p>

                <h2>
                    {score:.1f}% Match
                </h2>

            </div>
            """,
            unsafe_allow_html=True
        )

        col_a, col_b = st.columns(2)

        with col_a:

            st.write("**Matched Skills**")

            if job["matched_skills"]:

                for skill in job["matched_skills"]:

                    st.markdown(
                        f"""
                        <span class="skill-tag">
                            ✓ {skill}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.write("None")

        with col_b:

            st.write("**Missing Skills**")

            if job["missing_skills"]:

                for skill in job["missing_skills"]:

                    st.markdown(
                        f"""
                        <span class="missing-tag">
                            ✕ {skill}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.success(
                    "No major skill gaps detected."
                )

        st.markdown("---")


else:

    st.warning(
        "No job matches were found."
    )


# ============================================================
# TARGET JOB
# ============================================================

if jobs:

    st.markdown("""
    <div class="section-title">
        🔍 Deep Skill-Gap Analysis
    </div>
    """, unsafe_allow_html=True)

    job_options = [
        f'{job["title"]} — {job["company"]}'
        for job in jobs
    ]

    selected_job_label = st.selectbox(
        "Choose a target job",
        job_options
    )

    selected_job_index = job_options.index(
        selected_job_label
    )

    selected_job = jobs[
        selected_job_index
    ]

    matched_skills = selected_job[
        "matched_skills"
    ]

    missing_skills = selected_job[
        "missing_skills"
    ]


    # ========================================================
    # MATCH BREAKDOWN
    # ========================================================

    b1, b2, b3 = st.columns(3)

    with b1:

        st.metric(
            "Overall Match",
            f'{selected_job["match_score"]:.1f}%'
        )

    with b2:

        st.metric(
            "Skill Coverage",
            f'{selected_job["skill_coverage"]:.1f}%'
        )

    with b3:

        st.metric(
            "Semantic Similarity",
            f'{selected_job["semantic_similarity"]:.1f}%'
        )


    # ========================================================
    # GAP EXPLANATION
    # ========================================================

    with st.spinner(
        "Generating skill-gap explanation..."
    ):

        explanation = explain_gap(
            selected_job["title"],
            matched_skills,
            missing_skills
        )

    st.markdown(
        explanation
    )


    # ========================================================
    # OPPORTUNITY UNLOCK
    # ========================================================

    st.markdown("---")

    st.markdown("""
    <div class="section-title">
        🚀 Opportunity Unlock Engine
    </div>

    <div class="section-subtitle">
        See which missing skills could unlock additional job opportunities.
    </div>
    """, unsafe_allow_html=True)


    unlock_data = opportunity_unlock(
        jobs,
        skills
    )


    if unlock_data:

        unlock_df = pd.DataFrame(
            unlock_data
        )

        st.dataframe(
            unlock_df.head(10),
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # WHAT IF SIMULATOR
    # ========================================================

    st.markdown("---")

    st.markdown("""
    <div class="section-title">
        🧪 What-If Skill Simulator
    </div>

    <div class="section-subtitle">
        Select a skill to simulate how your job matches could change.
    </div>
    """, unsafe_allow_html=True)


    missing_for_simulation = sorted(
        set(
            skill
            for job in jobs
            for skill in job["missing_skills"]
        )
    )


    if missing_for_simulation:

        simulated_skill = st.selectbox(
            "Choose a skill to learn",
            missing_for_simulation
        )


        simulated_skills = list(
            skills
        )

        simulated_skills.append(
            simulated_skill
        )


        simulated_jobs = match_jobs(
            simulated_skills,
            profile.get("location", "")
        )


        old_average = sum(
            job["match_score"]
            for job in jobs
        ) / len(jobs)


        new_average = sum(
            job["match_score"]
            for job in simulated_jobs
        ) / len(simulated_jobs)


        w1, w2, w3 = st.columns(3)


        with w1:

            st.metric(
                "Current Average Match",
                f"{old_average:.1f}%"
            )


        with w2:

            st.metric(
                "After Learning Skill",
                f"{new_average:.1f}%"
            )


        with w3:

            improvement = (
                new_average - old_average
            )

            st.metric(
                "Potential Improvement",
                f"{improvement:+.1f}%"
            )


# ============================================================
# TRAINING PATH
# ============================================================

if jobs:

    st.markdown("---")

    st.markdown("""
    <div class="section-title">
        📚 Personalized Training Path
    </div>

    <div class="section-subtitle">
        Training recommendations mapped directly to the selected job's skill gaps.
    </div>
    """, unsafe_allow_html=True)


    free_only = st.checkbox(
        "🆓 Show only free courses"
    )


    courses = recommend_courses(
        missing_skills,
        free_only=free_only
    )


    if courses:

        course_df = pd.DataFrame(
            courses
        )

        display_columns = [
            "skill",
            "course",
            "provider",
            "duration_weeks",
            "cost",
            "level"
        ]

        st.dataframe(
            course_df[display_columns],
            use_container_width=True,
            hide_index=True
        )


        total_weeks, total_cost = (
            calculate_time_and_cost(
                courses
            )
        )


        t1, t2 = st.columns(2)


        with t1:

            st.metric(
                "⏱️ Estimated Learning Time",
                f"{total_weeks} weeks"
            )


        with t2:

            st.metric(
                "💰 Estimated Cost",
                f"₹{total_cost:,.0f}"
            )


    else:

        st.warning(
            "No matching training resources found for these skill gaps."
        )


# ============================================================
# 30 / 60 / 90 DAY ROADMAP
# ============================================================

st.markdown("---")

st.markdown("""
<div class="section-title">
    📅 30 / 60 / 90 Day Career Roadmap
</div>
""", unsafe_allow_html=True)


r1, r2, r3 = st.columns(3)


with r1:

    st.markdown("""
    <div class="feature-card">

        <div class="feature-icon">
            🟢
        </div>

        <div class="feature-title">
            First 30 Days
        </div>

        <div class="feature-text">

            • Learn foundational missing skills<br>
            • Complete beginner courses<br>
            • Practice small exercises<br>
            • Build Git/GitHub consistency

        </div>

    </div>
    """, unsafe_allow_html=True)


with r2:

    st.markdown("""
    <div class="feature-card">

        <div class="feature-icon">
            🟡
        </div>

        <div class="feature-title">
            Days 31–60
        </div>

        <div class="feature-text">

            • Build practical projects<br>
            • Strengthen intermediate skills<br>
            • Practice job-specific tasks<br>
            • Improve portfolio

        </div>

    </div>
    """, unsafe_allow_html=True)


with r3:

    st.markdown("""
    <div class="feature-card">

        <div class="feature-icon">
            🔵
        </div>

        <div class="feature-title">
            Days 61–90
        </div>

        <div class="feature-text">

            • Complete capstone project<br>
            • Update resume<br>
            • Practice interviews<br>
            • Start targeted applications

        </div>

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#6b7280;
        padding:20px;
        font-size:14px;
    ">

        🎯 <b>SkillGap AI</b>

        <br>

        Resume → Skills → Jobs → Gaps → Training → Job Readiness

        <br><br>

        Built for Agentic AI Saksham Hackathon 2026

    </div>
    """,
    unsafe_allow_html=True
)