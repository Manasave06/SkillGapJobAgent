import os
import streamlit as st
import pandas as pd

from dotenv import load_dotenv

from utils.pdf_reader import extract_text_from_pdf
from agents.profile_agent import extract_profile
from agents.matching_agent import match_jobs
from agents.gap_agent import explain_gap
from agents.training_agent import recommend_courses, calculate_time_and_cost
from utils.scoring import opportunity_unlock


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

st.set_page_config(
    page_title="SkillGap AI",
    page_icon="🎯",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f5f7fb;
    }

    .main-title {
        font-size: 48px;
        font-weight: 800;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #667085;
        margin-bottom: 35px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 750;
        margin-top: 30px;
        margin-bottom: 8px;
    }

    .section-description {
        color: #667085;
        font-size: 16px;
        margin-bottom: 20px;
    }

    .feature-box {
        background: white;
        border-radius: 16px;
        padding: 22px;
        min-height: 180px;
        border: 1px solid #e5e7eb;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.04);
    }

    .feature-icon {
        font-size: 32px;
    }

    .feature-title {
        font-size: 19px;
        font-weight: 700;
        margin-top: 10px;
    }

    .feature-text {
        color: #667085;
        margin-top: 8px;
        line-height: 1.5;
    }

    .metric-box {
        background: white;
        padding: 22px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #e5e7eb;
        box-shadow: 0px 3px 12px rgba(0,0,0,0.04);
    }

    .metric-number {
        font-size: 34px;
        font-weight: 800;
    }

    .metric-label {
        color: #667085;
        margin-top: 5px;
    }

    .job-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }

    .success-box {
        background: #ecfdf3;
        border: 1px solid #abefc6;
        padding: 15px;
        border-radius: 12px;
    }

    .warning-box {
        background: #fffaeb;
        border: 1px solid #fedf89;
        padding: 15px;
        border-radius: 12px;
    }

    .footer {
        text-align: center;
        color: #667085;
        padding: 40px 0 20px 0;
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

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False


# =========================================================
# HEADER
# =========================================================

st.title("🎯 SkillGap AI")

st.markdown(
    """
    <div class="subtitle">
    Transform resumes into actionable career intelligence.
    Discover candidate skills, identify job-specific gaps,
    and build a personalized path to job readiness.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# WHAT SKILLGAP AI DOES
# =========================================================

st.markdown(
    '<div class="section-title">✨ What SkillGap AI does</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'One intelligent workflow from resume understanding to personalized career planning.'
    '</div>',
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 📄 Resume Intelligence")
    st.write(
        "Extract education, skills, projects, certifications "
        "and experience automatically."
    )

with col2:
    st.markdown("### 🎯 Job Matching")
    st.write(
        "Compare candidate skills with relevant job "
        "requirements."
    )

with col3:
    st.markdown("### 🔍 Skill Gap Analysis")
    st.write(
        "Identify the exact skills missing for target "
        "job opportunities."
    )

with col4:
    st.markdown("### 🚀 Career Roadmap")
    st.write(
        "Get courses, learning time, cost and an "
        "actionable career path."
    )


st.divider()


# =========================================================
# RESUME UPLOAD
# =========================================================

st.markdown(
    '<div class="section-title">📄 Analyze Candidate Resumes</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Upload one or more PDF resumes. Each candidate is analyzed independently.'
    '</div>',
    unsafe_allow_html=True
)

uploaded_files = st.file_uploader(
    "Choose PDF resumes",
    type=["pdf"],
    accept_multiple_files=True
)


# =========================================================
# MANUAL PROFILE
# =========================================================

st.markdown("### ✍️ Or enter a candidate profile manually")

manual_name = st.text_input(
    "Candidate Name",
    placeholder="Example: Manasa V E"
)

manual_skills = st.text_input(
    "Skills",
    placeholder="Example: Python, SQL, HTML, CSS"
)

manual_location = st.text_input(
    "Location",
    placeholder="Example: Bengaluru"
)

manual_education = st.text_input(
    "Education",
    placeholder="Example: B.E. Computer Science"
)


# =========================================================
# ANALYZE BUTTON
# =========================================================

if st.button(
    "🚀 Analyze Candidate",
    type="primary",
    use_container_width=True
):

    candidates = []

    # -----------------------------------------------------
    # PDF ANALYSIS
    # -----------------------------------------------------

    if uploaded_files:

        progress = st.progress(0)

        total_files = len(uploaded_files)

        for index, uploaded_file in enumerate(uploaded_files):

            try:

                with st.spinner(
                    f"Analyzing {uploaded_file.name}..."
                ):

                    resume_text = extract_text_from_pdf(
                        uploaded_file
                    )

                    if not resume_text.strip():
                        st.warning(
                            f"No readable text found in {uploaded_file.name}"
                        )
                        continue

                    profile = extract_profile(
                        resume_text
                    )

                    candidates.append(
                        {
                            "name": profile.get(
                                "name",
                                uploaded_file.name
                            ),
                            "location": profile.get(
                                "location",
                                ""
                            ),
                            "education": profile.get(
                                "education",
                                []
                            ),
                            "skills": profile.get(
                                "skills",
                                []
                            ),
                            "projects": profile.get(
                                "projects",
                                []
                            ),
                            "certifications": profile.get(
                                "certifications",
                                []
                            ),
                            "interests": profile.get(
                                "interests",
                                []
                            ),
                            "experience": profile.get(
                                "experience",
                                []
                            ),
                            "source": uploaded_file.name
                        }
                    )

                progress.progress(
                    (index + 1) / total_files
                )

            except Exception as e:

                st.error(
                    f"Could not analyze {uploaded_file.name}"
                )

                st.exception(e)


    # -----------------------------------------------------
    # MANUAL PROFILE
    # -----------------------------------------------------

    if manual_name and manual_skills:

        skills = [
            skill.strip()
            for skill in manual_skills.split(",")
            if skill.strip()
        ]

        candidates.append(
            {
                "name": manual_name,
                "location": manual_location,
                "education": [manual_education]
                if manual_education
                else [],
                "skills": skills,
                "projects": [],
                "certifications": [],
                "interests": [],
                "experience": [],
                "source": "Manual Profile"
            }
        )


    # -----------------------------------------------------
    # SAVE RESULTS
    # -----------------------------------------------------

    if candidates:

        st.session_state.candidates = candidates
        st.session_state.analysis_done = True

        st.success(
            f"Successfully analyzed {len(candidates)} candidate(s)."
        )

    else:

        st.warning(
            "Please upload a PDF resume or enter a manual profile."
        )


# =========================================================
# DASHBOARD
# =========================================================

st.markdown(
    '<div class="section-title">📊 Career Intelligence Dashboard</div>',
    unsafe_allow_html=True
)

candidate_count = len(
    st.session_state.candidates
)

skill_count = 0

for candidate in st.session_state.candidates:
    skill_count += len(
        candidate.get("skills", [])
    )

try:
    jobs_df = pd.read_csv(
        "data/jobs.csv"
    )

    job_count = len(jobs_df)

except Exception:
    job_count = 0


try:
    courses_df = pd.read_csv(
        "data/courses.csv"
    )

    course_count = len(courses_df)

except Exception:
    course_count = 0


m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "Candidates Analyzed",
        candidate_count
    )

with m2:
    st.metric(
        "Skills Detected",
        skill_count
    )

with m3:
    st.metric(
        "Job Opportunities",
        job_count
    )

with m4:
    st.metric(
        "Learning Resources",
        course_count
    )


# =========================================================
# STOP IF NO CANDIDATE
# =========================================================

if not st.session_state.candidates:

    st.info(
        "Upload a PDF resume above to start the career analysis."
    )

    st.markdown(
        """
        <div class="footer">
        🎯 SkillGap AI • Agentic Career Intelligence
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# =========================================================
# CANDIDATE SELECTOR
# =========================================================

st.divider()

st.markdown("## 👤 Candidate Analysis")

candidate_names = [
    candidate["name"]
    for candidate in st.session_state.candidates
]

selected_name = st.selectbox(
    "Select Candidate",
    candidate_names
)

selected_candidate = next(
    candidate
    for candidate in st.session_state.candidates
    if candidate["name"] == selected_name
)


# =========================================================
# PROFILE
# =========================================================

st.markdown("### 👤 Candidate Profile")

profile_col1, profile_col2 = st.columns(2)

with profile_col1:

    st.write(
        "**Name:**",
        selected_candidate.get("name", "Not available")
    )

    st.write(
        "**Location:**",
        selected_candidate.get("location", "Not specified")
    )

    st.write(
        "**Education:**",
        selected_candidate.get("education", [])
    )

with profile_col2:

    st.write(
        "**Skills:**"
    )

    skills = selected_candidate.get(
        "skills",
        []
    )

    if skills:

        st.write(
            ", ".join(skills)
        )

    else:

        st.write(
            "No skills detected."
        )


# =========================================================
# PROJECTS / CERTIFICATIONS
# =========================================================

with st.expander("📁 Projects"):

    projects = selected_candidate.get(
        "projects",
        []
    )

    if projects:

        for project in projects:
            st.write("•", project)

    else:

        st.write(
            "No projects found in the resume."
        )


with st.expander("🏆 Certifications"):

    certifications = selected_candidate.get(
        "certifications",
        []
    )

    if certifications:

        for certification in certifications:
            st.write("•", certification)

    else:

        st.write(
            "No certifications found."
        )


# =========================================================
# JOB MATCHING
# =========================================================

st.divider()

st.markdown("## 🎯 Job Matching")

candidate_skills = selected_candidate.get(
    "skills",
    []
)

candidate_location = selected_candidate.get(
    "location",
    ""
)

with st.spinner("Finding suitable job opportunities..."):

    job_results = match_jobs(
        candidate_skills,
        candidate_location
    )


if not job_results:

    st.warning(
        "No job opportunities found."
    )

else:

    st.write(
        f"Found {len(job_results)} matching opportunities."
    )

    for index, job in enumerate(job_results[:5]):

        with st.container(border=True):

            st.markdown(
                f"### {index + 1}. {job['title']}"
            )

            st.write(
                f"🏢 **Company:** {job['company']}"
            )

            st.write(
                f"📍 **Location:** {job['location']}"
            )

            st.progress(
                min(
                    int(job["match_score"]),
                    100
                )
            )

            st.write(
                f"**Match Score:** {job['match_score']}%"
            )

            col_a, col_b = st.columns(2)

            with col_a:

                st.write(
                    "**Matched Skills**"
                )

                if job["matched_skills"]:

                    st.write(
                        ", ".join(
                            job["matched_skills"]
                        )
                    )

                else:

                    st.write(
                        "No strong skill matches."
                    )

            with col_b:

                st.write(
                    "**Missing Skills**"
                )

                if job["missing_skills"]:

                    st.write(
                        ", ".join(
                            job["missing_skills"]
                        )
                    )

                else:

                    st.write(
                        "No major skill gaps detected."
                    )


# =========================================================
# SELECT TARGET JOB
# =========================================================

st.divider()

st.markdown("## 🔍 Deep Skill Gap Analysis")

job_titles = [
    f"{job['title']} — {job['company']}"
    for job in job_results
]

selected_job_index = st.selectbox(
    "Choose a target job",
    range(len(job_titles)),
    format_func=lambda x: job_titles[x]
)

selected_job = job_results[
    selected_job_index
]


st.write(
    f"### {selected_job['title']}"
)

st.write(
    f"Company: **{selected_job['company']}**"
)

st.write(
    f"Current Match: **{selected_job['match_score']}%**"
)


# =========================================================
# MATCH BREAKDOWN
# =========================================================

st.markdown("### 📊 Match Breakdown")

b1, b2, b3 = st.columns(3)

with b1:

    st.metric(
        "Skill Coverage",
        f"{selected_job['skill_coverage']}%"
    )

with b2:

    st.metric(
        "Semantic Similarity",
        f"{selected_job['semantic_similarity']}%"
    )

with b3:

    st.metric(
        "Location Fit",
        f"{selected_job['location_fit']}%"
    )


# =========================================================
# MATCHED / MISSING
# =========================================================

matched = selected_job.get(
    "matched_skills",
    []
)

missing = selected_job.get(
    "missing_skills",
    []
)

col1, col2 = st.columns(2)

with col1:

    st.markdown("### ✅ Skills You Have")

    if matched:

        for skill in matched:
            st.success(skill)

    else:

        st.info(
            "No matching skills detected."
        )


with col2:

    st.markdown("### ❌ Skills You Need")

    if missing:

        for skill in missing:
            st.warning(skill)

    else:

        st.success(
            "No major missing skills."
        )


# =========================================================
# AI GAP EXPLANATION
# =========================================================

st.markdown("### 🤖 AI Skill Gap Explanation")

with st.spinner(
    "Generating personalized skill-gap analysis..."
):

    try:

        explanation = explain_gap(
            selected_job["title"],
            matched,
            missing
        )

        st.write(explanation)

    except Exception as e:

        st.error(
            "Unable to generate AI explanation."
        )

        st.exception(e)


# =========================================================
# OPPORTUNITY UNLOCK
# =========================================================

st.divider()

st.markdown(
    "## 🚀 Opportunity Unlock Engine"
)

st.write(
    "See which missing skills can unlock additional job opportunities."
)

unlock_data = opportunity_unlock(
    job_results,
    candidate_skills
)

if unlock_data:

    unlock_df = pd.DataFrame(
        unlock_data
    )

    st.dataframe(
        unlock_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No additional skill opportunities identified."
    )


# =========================================================
# WHAT-IF SIMULATOR
# =========================================================

st.divider()

st.markdown(
    "## 🧪 What-If Skill Simulator"
)

st.write(
    "Choose a skill you could learn and see how it may affect job matching."
)

all_missing_skills = sorted(
    set(
        skill
        for job in job_results
        for skill in job["missing_skills"]
    )
)

if all_missing_skills:

    what_if_skill = st.selectbox(
        "Select a skill to simulate",
        all_missing_skills
    )

    simulated_skills = list(
        candidate_skills
    )

    simulated_skills.append(
        what_if_skill
    )

    with st.spinner(
        "Simulating new job matches..."
    ):

        simulated_results = match_jobs(
            simulated_skills,
            candidate_location
        )

    current_count = sum(
        1
        for job in job_results
        if job["match_score"] >= 50
    )

    simulated_count = sum(
        1
        for job in simulated_results
        if job["match_score"] >= 50
    )

    st.metric(
        "Jobs meeting 50%+ match",
        simulated_count,
        simulated_count - current_count
    )

else:

    st.info(
        "No missing skills available for simulation."
    )


# =========================================================
# TRAINING RECOMMENDATIONS
# =========================================================

st.divider()

st.markdown(
    "## 🎓 Personalized Training Path"
)

free_only = st.checkbox(
    "Show only free learning resources"
)

courses = recommend_courses(
    missing,
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

    total_weeks, total_cost = calculate_time_and_cost(
        courses
    )

    t1, t2 = st.columns(2)

    with t1:

        st.metric(
            "Estimated Learning Time",
            f"{total_weeks} weeks"
        )

    with t2:

        st.metric(
            "Estimated Cost",
            f"₹{total_cost:,.0f}"
        )

else:

    st.info(
        "No course recommendation found for the selected skill gaps."
    )


# =========================================================
# TIME TO READY
# =========================================================

st.divider()

st.markdown(
    "## ⏱️ Time-to-Ready Estimate"
)

if courses:

    st.write(
        f"To address the selected job's identified gaps, "
        f"the estimated learning time is **{total_weeks} weeks**."
    )

    st.write(
        f"Estimated learning cost: **₹{total_cost:,.0f}**."
    )

    if free_only:

        st.success(
            "Free-only learning mode is enabled."
        )

else:

    st.info(
        "Add suitable courses to calculate time-to-ready."
    )


# =========================================================
# 30 / 60 / 90 DAY ROADMAP
# =========================================================

st.divider()

st.markdown(
    "## 🗺️ 30 / 60 / 90 Day Career Roadmap"
)

roadmap1, roadmap2, roadmap3 = st.columns(3)

with roadmap1:

    st.markdown("### 📅 First 30 Days")

    st.write(
        "• Learn the highest-priority missing skill."
    )

    st.write(
        "• Complete beginner-level learning resources."
    )

    st.write(
        "• Build one small practical project."
    )


with roadmap2:

    st.markdown("### 📅 Days 31–60")

    st.write(
        "• Continue intermediate learning."
    )

    st.write(
        "• Build a project related to the target role."
    )

    st.write(
        "• Improve GitHub/project documentation."
    )


with roadmap3:

    st.markdown("### 📅 Days 61–90")

    st.write(
        "• Complete remaining skill gaps."
    )

    st.write(
        "• Update resume with relevant projects."
    )

    st.write(
        "• Start applying to suitable opportunities."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        🎯 SkillGap AI<br>
        Agentic AI Career Intelligence
    </div>
    """,
    unsafe_allow_html=True
)