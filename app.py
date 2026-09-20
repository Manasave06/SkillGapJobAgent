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


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SkillGap AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM UI STYLE
# =========================================================

st.markdown(
    """
    <style>

    /* Main application background */

    .stApp {
        background-color: #f5f7fb;
    }


    /* Main content width */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }


    /* Main title */

    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #172554;
        margin-bottom: 4px;
        letter-spacing: -1px;
    }


    .main-subtitle {
        font-size: 16px;
        color: #64748b;
        margin-bottom: 25px;
    }


    /* Section headings */

    .section-title {
        font-size: 25px;
        font-weight: 750;
        color: #172554;
        border-left: 5px solid #4f46e5;
        padding-left: 12px;
        margin-top: 28px;
        margin-bottom: 18px;
    }


    .small-title {
        font-size: 18px;
        font-weight: 700;
        color: #1e293b;
        margin-top: 15px;
        margin-bottom: 10px;
    }


    /* Header card */

    .header-card {
        background: linear-gradient(
            135deg,
            #172554,
            #3730a3
        );
        padding: 30px;
        border-radius: 18px;
        margin-bottom: 28px;
        box-shadow: 0 8px 25px rgba(30, 41, 59, 0.12);
    }


    .header-card-title {
        color: white;
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 8px;
    }


    .header-card-text {
        color: #dbeafe;
        font-size: 16px;
        line-height: 1.6;
    }


    /* Metric cards */

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        min-height: 125px;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.05);
    }


    .metric-label {
        color: #64748b;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }


    .metric-value {
        color: #172554;
        font-size: 32px;
        font-weight: 800;
    }


    /* Upload area */

    .upload-card {
        background: white;
        border: 2px dashed #a5b4fc;
        border-radius: 18px;
        padding: 25px;
        margin-top: 10px;
        margin-bottom: 20px;
    }


    /* Information cards */

    .info-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        margin-top: 12px;
        margin-bottom: 12px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
    }


    .card-title {
        color: #172554;
        font-size: 19px;
        font-weight: 750;
        margin-bottom: 8px;
    }


    .card-text {
        color: #475569;
        font-size: 14px;
        line-height: 1.6;
    }


    /* Job cards */

    .job-card {
        background: white;
        border: 1px solid #dbeafe;
        border-radius: 16px;
        padding: 22px;
        margin: 12px 0;
        box-shadow: 0 4px 15px rgba(30, 64, 175, 0.06);
    }


    .job-title {
        color: #172554;
        font-size: 20px;
        font-weight: 800;
    }


    .job-company {
        color: #64748b;
        font-size: 14px;
        margin-top: 4px;
    }


    /* Skill boxes */

    .skill-box {
        background: #eef2ff;
        color: #3730a3;
        border: 1px solid #c7d2fe;
        border-radius: 9px;
        padding: 7px 11px;
        display: inline-block;
        margin: 4px;
        font-size: 13px;
        font-weight: 600;
    }


    .missing-box {
        background: #fff7ed;
        color: #c2410c;
        border: 1px solid #fed7aa;
        border-radius: 9px;
        padding: 7px 11px;
        display: inline-block;
        margin: 4px;
        font-size: 13px;
        font-weight: 600;
    }


    /* Score */

    .score-box {
        background: #eef2ff;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        margin-top: 12px;
    }


    .score-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
    }


    .score-value {
        color: #3730a3;
        font-size: 27px;
        font-weight: 800;
    }


    /* Training cards */

    .training-card {
        background: white;
        border: 1px solid #dbeafe;
        border-radius: 15px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
    }


    .training-title {
        color: #172554;
        font-size: 18px;
        font-weight: 750;
    }


    .training-detail {
        color: #64748b;
        font-size: 14px;
        margin-top: 5px;
    }


    /* Status boxes */

    .success-box {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        padding: 14px 16px;
        border-radius: 12px;
        margin: 10px 0;
    }


    .warning-box {
        background: #fffbeb;
        border: 1px solid #fde68a;
        color: #92400e;
        padding: 14px 16px;
        border-radius: 12px;
        margin: 10px 0;
    }


    /* Sidebar */

    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }


    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #172554;
    }


    /* Buttons */

    .stButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 44px;
    }


    /* Dataframes */

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }


    /* Tabs */

    button[data-baseweb="tab"] {
        font-weight: 650;
        color: #475569;
    }


    /* Divider */

    hr {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 28px 0;
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
# APPLICATION HEADER
# =========================================================

st.markdown(
    """
    <div class="header-card">
        <div class="header-card-title">
            SkillGap AI
        </div>
        <div class="header-card-text">
            Intelligent resume analysis, job matching,
            skill-gap detection and personalized
            learning recommendations.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("Application Settings")

    free_only = st.checkbox(
        "Show only free courses",
        value=False
    )

    st.divider()

    st.subheader("Analysis Pipeline")

    st.write(
        "Resume"
    )

    st.write(
        "Profile extraction"
    )

    st.write(
        "Skill normalization"
    )

    st.write(
        "Job matching"
    )

    st.write(
        "Skill-gap analysis"
    )

    st.write(
        "Training recommendation"
    )

    st.divider()

    st.caption(
        "Information that is unavailable in the "
        "dataset is shown as Not available."
    )


# =========================================================
# UPLOAD SECTION
# =========================================================

st.markdown(
    '<div class="section-title">Resume Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="upload-card">
        <div class="card-title">
            Upload Candidate Resumes
        </div>
        <div class="card-text">
            Upload one or more PDF resumes.
            All candidates will be processed together.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


uploaded_files = st.file_uploader(
    "Select PDF resumes",
    type=["pdf"],
    accept_multiple_files=True
)


# =========================================================
# SELECTED FILES
# =========================================================

if uploaded_files:

    st.markdown(
        '<div class="small-title">Selected Resumes</div>',
        unsafe_allow_html=True
    )

    file_rows = []

    for file in uploaded_files:

        file_rows.append(
            {
                "Resume": file.name,
                "Size": f"{file.size / 1024:.1f} KB"
            }
        )

    st.dataframe(
        pd.DataFrame(file_rows),
        use_container_width=True,
        hide_index=True
    )

    st.write(
        f"{len(uploaded_files)} resume(s) selected."
    )


# =========================================================
# ANALYZE BUTTON
# =========================================================

if uploaded_files:

    if st.button(
        "Analyze All Candidates",
        type="primary",
        use_container_width=True
    ):

        candidates = []

        progress_bar = st.progress(0)

        status_text = st.empty()

        total_files = len(
            uploaded_files
        )

        for index, uploaded_file in enumerate(
            uploaded_files
        ):

            status_text.write(
                f"Analyzing {uploaded_file.name}"
            )

            try:

                # -----------------------------------------
                # READ PDF
                # -----------------------------------------

                resume_text = extract_text_from_pdf(
                    uploaded_file
                )

                if not resume_text.strip():

                    st.warning(
                        f"No readable text found in "
                        f"{uploaded_file.name}."
                    )

                    continue


                # -----------------------------------------
                # PROFILE EXTRACTION
                # -----------------------------------------

                profile = extract_profile(
                    resume_text
                )


                # -----------------------------------------
                # SKILLS
                # -----------------------------------------

                skills = profile.get(
                    "skills",
                    []
                )


                location = profile.get(
                    "location",
                    ""
                )


                # -----------------------------------------
                # JOB MATCHING
                # -----------------------------------------

                jobs = match_jobs(
                    skills,
                    location
                )


                # -----------------------------------------
                # SAVE CANDIDATE
                # -----------------------------------------

                candidates.append(
                    {
                        "filename": uploaded_file.name,
                        "resume_text": resume_text,
                        "profile": profile,
                        "skills": skills,
                        "jobs": jobs
                    }
                )


            except Exception as error:

                st.error(
                    f"Could not analyze "
                    f"{uploaded_file.name}: {error}"
                )


            progress_bar.progress(
                (index + 1) / total_files
            )


        status_text.empty()

        st.session_state.candidates = candidates

        st.session_state.analysis_done = True

        st.success(
            f"Analysis completed for "
            f"{len(candidates)} candidate(s)."
        )

        st.rerun()


# =========================================================
# STOP IF NOTHING ANALYZED
# =========================================================

if not st.session_state.analysis_done:

    st.info(
        "Upload resumes and select Analyze All Candidates."
    )

    st.stop()


if not st.session_state.candidates:

    st.error(
        "No candidate information could be extracted."
    )

    st.stop()


# =========================================================
# DASHBOARD
# =========================================================

st.markdown(
    '<div class="section-title">Dashboard</div>',
    unsafe_allow_html=True
)


candidate_count = len(
    st.session_state.candidates
)


all_skills = []

total_jobs = 0


for candidate in st.session_state.candidates:

    all_skills.extend(
        candidate["skills"]
    )

    total_jobs += len(
        candidate["jobs"]
    )


unique_skills = set(
    str(skill).lower().strip()
    for skill in all_skills
)


try:

    course_count = len(
        pd.read_csv(
            "data/courses.csv"
        )
    )

except Exception:

    course_count = 0


metric_col1, metric_col2, metric_col3, metric_col4 = (
    st.columns(4)
)


with metric_col1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Candidates
            </div>
            <div class="metric-value">
                {candidate_count}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with metric_col2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Unique Skills
            </div>
            <div class="metric-value">
                {len(unique_skills)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with metric_col3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Jobs Analyzed
            </div>
            <div class="metric-value">
                {total_jobs}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with metric_col4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Learning Resources
            </div>
            <div class="metric-value">
                {course_count}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# CANDIDATE ANALYSIS
# =========================================================

st.markdown(
    '<div class="section-title">Candidate Analysis</div>',
    unsafe_allow_html=True
)


candidate_names = []


for index, candidate in enumerate(
    st.session_state.candidates
):

    name = candidate["profile"].get(
        "name",
        ""
    )


    if not name.strip():

        name = f"Candidate {index + 1}"


    candidate_names.append(
        name
    )


candidate_tabs = st.tabs(
    candidate_names
)


# =========================================================
# EACH CANDIDATE
# =========================================================

for candidate_index, tab in enumerate(
    candidate_tabs
):

    candidate = st.session_state.candidates[
        candidate_index
    ]

    profile = candidate["profile"]

    skills = candidate["skills"]

    jobs = candidate["jobs"]


    with tab:

        # =================================================
        # PROFILE
        # =================================================

        st.markdown(
            '<div class="section-title">Candidate Profile</div>',
            unsafe_allow_html=True
        )


        profile_col1, profile_col2 = st.columns(2)


        with profile_col1:

            st.markdown(
                """
                <div class="info-card">
                    <div class="card-title">
                        Basic Information
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


            name = profile.get(
                "name",
                ""
            )


            if not name:

                name = "Not available"


            location = profile.get(
                "location",
                ""
            )


            if not location:

                location = "Not available"


            st.write(
                f"Name: {name}"
            )

            st.write(
                f"Location: {location}"
            )

            st.write(
                f"Resume: {candidate['filename']}"
            )


        with profile_col2:

            st.markdown(
                """
                <div class="info-card">
                    <div class="card-title">
                        Education
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


            education = profile.get(
                "education",
                []
            )


            if education:

                for item in education:

                    st.write(
                        f"- {item}"
                    )

            else:

                st.write(
                    "Not available"
                )


        # =================================================
        # EXPERIENCE
        # =================================================

        st.markdown(
            '<div class="small-title">Experience</div>',
            unsafe_allow_html=True
        )


        experience = profile.get(
            "experience",
            []
        )


        if experience:

            for item in experience:

                st.write(
                    f"- {item}"
                )

        else:

            st.write(
                "Not available"
            )


        # =================================================
        # SKILLS
        # =================================================

        st.markdown(
            '<div class="section-title">Current Skills</div>',
            unsafe_allow_html=True
        )


        if skills:

            skill_columns = st.columns(
                min(4, len(skills))
            )


            for index, skill in enumerate(
                skills
            ):

                with skill_columns[
                    index % len(skill_columns)
                ]:

                    st.markdown(
                        f"""
                        <div class="skill-box">
                            {skill}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        else:

            st.warning(
                "No technical skills were detected."
            )


        # =================================================
        # CERTIFICATIONS
        # =================================================

        certifications = profile.get(
            "certifications",
            []
        )


        if certifications:

            st.markdown(
                '<div class="small-title">Certifications</div>',
                unsafe_allow_html=True
            )


            for certificate in certifications:

                st.write(
                    f"- {certificate}"
                )


        # =================================================
        # INTERESTS
        # =================================================

        interests = profile.get(
            "interests",
            []
        )


        if interests:

            st.markdown(
                '<div class="small-title">Interests</div>',
                unsafe_allow_html=True
            )


            for interest in interests:

                st.write(
                    f"- {interest}"
                )


        # =================================================
        # JOB MATCHING
        # =================================================

        st.markdown(
            '<div class="section-title">Job Matching</div>',
            unsafe_allow_html=True
        )


        if jobs:

            job_rows = []


            for job in jobs:

                job_rows.append(
                    {
                        "Job": job.get(
                            "title",
                            "Not available"
                        ),
                        "Company": job.get(
                            "company",
                            "Not available"
                        ),
                        "Location": job.get(
                            "location",
                            "Not available"
                        ),
                        "Match": (
                            f"{job.get('match_score', 0)}%"
                        ),
                        "Skill Coverage": (
                            f"{job.get('skill_coverage', 0)}%"
                        ),
                        "Location Fit": (
                            f"{job.get('location_fit', 0)}%"
                        )
                    }
                )


            st.dataframe(
                pd.DataFrame(job_rows),
                use_container_width=True,
                hide_index=True
            )


        else:

            st.warning(
                "No jobs are available for matching."
            )


        # =================================================
        # TOP JOB MATCHES
        # =================================================

        if jobs:

            st.markdown(
                '<div class="section-title">Top Job Opportunities</div>',
                unsafe_allow_html=True
            )


            for number, job in enumerate(
                jobs[:5],
                start=1
            ):

                st.markdown(
                    f"""
                    <div class="job-card">
                        <div class="job-title">
                            {number}. {job['title']}
                        </div>
                        <div class="job-company">
                            {job['company']} |
                            {job['location']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


                score_col1, score_col2 = (
                    st.columns(2)
                )


                with score_col1:

                    st.markdown(
                        f"""
                        <div class="score-box">
                            <div class="score-label">
                                Match Score
                            </div>
                            <div class="score-value">
                                {job['match_score']}%
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                with score_col2:

                    st.markdown(
                        f"""
                        <div class="score-box">
                            <div class="score-label">
                                Skill Coverage
                            </div>
                            <div class="score-value">
                                {job['skill_coverage']}%
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                st.markdown(
                    '<div class="small-title">Matched Skills</div>',
                    unsafe_allow_html=True
                )


                matched = job.get(
                    "matched_skills",
                    []
                )


                if matched:

                    for skill in matched:

                        st.markdown(
                            f"""
                            <span class="skill-box">
                                {skill}
                            </span>
                            """,
                            unsafe_allow_html=True
                        )

                else:

                    st.write(
                        "None"
                    )


                st.markdown(
                    '<div class="small-title">Missing Skills</div>',
                    unsafe_allow_html=True
                )


                missing = job.get(
                    "missing_skills",
                    []
                )


                if missing:

                    for skill in missing:

                        st.markdown(
                            f"""
                            <span class="missing-box">
                                {skill}
                            </span>
                            """,
                            unsafe_allow_html=True
                        )

                else:

                    st.write(
                        "None"
                    )


                st.write("")


                # -----------------------------------------
                # SOURCE URL
                # -----------------------------------------

                job_url = str(
                    job.get(
                        "url",
                        ""
                    )
                ).strip()


                if (
                    job_url
                    and job_url.lower()
                    not in [
                        "nan",
                        "none",
                        "null",
                        ""
                    ]
                    and "example.com"
                    not in job_url.lower()
                ):

                    st.link_button(
                        "Open Job Source",
                        job_url
                    )

                else:

                    st.caption(
                        "Job source: Not available"
                    )


        # =================================================
        # DETAILED SKILL GAP
        # =================================================

        if jobs:

            st.markdown(
                '<div class="section-title">Detailed Skill Gap</div>',
                unsafe_allow_html=True
            )


            job_labels = []


            for job in jobs:

                job_labels.append(
                    f"{job['title']} | "
                    f"{job['company']} | "
                    f"{job['match_score']}%"
                )


            selected_job_index = st.selectbox(
                "Select a job for detailed analysis",
                range(len(jobs)),
                format_func=lambda x: job_labels[x],
                key=f"job_select_{candidate_index}"
            )


            selected_job = jobs[
                selected_job_index
            ]


            metric1, metric2, metric3 = (
                st.columns(3)
            )


            with metric1:

                st.metric(
                    "Match Score",
                    f"{selected_job['match_score']}%"
                )


            with metric2:

                st.metric(
                    "Skill Coverage",
                    f"{selected_job['skill_coverage']}%"
                )


            with metric3:

                st.metric(
                    "Location Fit",
                    f"{selected_job['location_fit']}%"
                )


            st.markdown(
                '<div class="small-title">Required Skills</div>',
                unsafe_allow_html=True
            )


            required = selected_job.get(
                "required_skills",
                []
            )


            if required:

                st.write(
                    ", ".join(required)
                )

            else:

                st.write(
                    "Not available"
                )


            st.markdown(
                '<div class="small-title">Matched Skills</div>',
                unsafe_allow_html=True
            )


            matched = selected_job.get(
                "matched_skills",
                []
            )


            if matched:

                for skill in matched:

                    st.markdown(
                        f"""
                        <span class="skill-box">
                            {skill}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.write(
                    "None"
                )


            st.markdown(
                '<div class="small-title">Missing Skills</div>',
                unsafe_allow_html=True
            )


            missing = selected_job.get(
                "missing_skills",
                []
            )


            if missing:

                for skill in missing:

                    st.markdown(
                        f"""
                        <span class="missing-box">
                            {skill}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.write(
                    "None"
                )


        # =================================================
        # AI EXPLANATION
        # =================================================

        if jobs:

            st.markdown(
                '<div class="section-title">AI Skill Gap Explanation</div>',
                unsafe_allow_html=True
            )


            if st.button(
                "Generate Explanation",
                key=(
                    f"explanation_"
                    f"{candidate_index}_"
                    f"{selected_job_index}"
                )
            ):

                with st.spinner(
                    "Generating explanation..."
                ):

                    try:

                        explanation = explain_gap(
                            selected_job["title"],
                            selected_job[
                                "matched_skills"
                            ],
                            selected_job[
                                "missing_skills"
                            ]
                        )

                        st.write(
                            explanation
                        )

                    except Exception as error:

                        st.error(
                            f"Could not generate explanation: "
                            f"{error}"
                        )


        # =================================================
        # TRAINING
        # =================================================

        st.markdown(
            '<div class="section-title">Training Recommendation</div>',
            unsafe_allow_html=True
        )


        if jobs:

            if missing:

                courses = recommend_courses(
                    missing,
                    free_only=free_only
                )


                if courses:

                    total_weeks, total_cost = (
                        calculate_time_and_cost(
                            courses
                        )
                    )


                    training_metric1, training_metric2 = (
                        st.columns(2)
                    )


                    with training_metric1:

                        st.metric(
                            "Time to Ready",
                            f"{total_weeks} weeks"
                        )


                    with training_metric2:

                        st.metric(
                            "Total Training Cost",
                            f"Rs {total_cost:.0f}"
                        )


                    for course in courses:

                        st.markdown(
                            f"""
                            <div class="training-card">
                                <div class="training-title">
                                    {course['course']}
                                </div>
                                <div class="training-detail">
                                    Provider:
                                    {course['provider']}
                                </div>
                                <div class="training-detail">
                                    Skill:
                                    {course['skill']}
                                </div>
                                <div class="training-detail">
                                    Duration:
                                    {course['duration_weeks']}
                                    weeks
                                </div>
                                <div class="training-detail">
                                    Cost:
                                    Rs {course['cost']}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                        course_url = str(
                            course.get(
                                "url",
                                ""
                            )
                        ).strip()


                        if (
                            course_url
                            and course_url.lower()
                            not in [
                                "nan",
                                "none",
                                "null",
                                ""
                            ]
                            and "example.com"
                            not in course_url.lower()
                        ):

                            st.link_button(
                                "Open Course Source",
                                course_url
                            )

                        else:

                            st.caption(
                                "Course source: Not available"
                            )


                else:

                    st.info(
                        "No course was found for "
                        "the selected missing skills."
                    )


            else:

                st.success(
                    "No missing skills were identified."
                )


        # =================================================
        # OPPORTUNITY UNLOCK
        # =================================================

        st.markdown(
            '<div class="section-title">Opportunity Unlock Analysis</div>',
            unsafe_allow_html=True
        )


        unlock_data = opportunity_unlock(
            jobs,
            skills
        )


        if unlock_data:

            unlock_dataframe = pd.DataFrame(
                unlock_data
            )


            skill_counts = (
                unlock_dataframe
                .groupby("Skill")
                .size()
                .reset_index(
                    name="Additional Jobs"
                )
                .sort_values(
                    "Additional Jobs",
                    ascending=False
                )
            )


            st.dataframe(
                skill_counts,
                use_container_width=True,
                hide_index=True
            )


        else:

            st.info(
                "No additional skill opportunities "
                "were identified."
            )


        # =================================================
        # ROADMAP
        # =================================================

        st.markdown(
            '<div class="section-title">Personalized Learning Roadmap</div>',
            unsafe_allow_html=True
        )


        if jobs:

            best_job = jobs[0]

            roadmap_skills = best_job.get(
                "missing_skills",
                []
            )


            if roadmap_skills:

                roadmap_steps = [
                    "Learn the identified missing skills.",
                    "Complete the recommended training.",
                    "Build practical projects.",
                    "Update the resume with demonstrated skills.",
                    "Run the analysis again after learning."
                ]


                for number, step in enumerate(
                    roadmap_steps,
                    start=1
                ):

                    st.markdown(
                        f"""
                        <div class="info-card">
                            <div class="card-title">
                                Step {number}
                            </div>
                            <div class="card-text">
                                {step}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


            else:

                st.success(
                    "No major skill gap was identified."
                )


# =========================================================
# CANDIDATE COMPARISON
# =========================================================

st.markdown(
    '<div class="section-title">Candidate Comparison</div>',
    unsafe_allow_html=True
)


comparison_rows = []


for candidate in st.session_state.candidates:

    profile = candidate["profile"]

    jobs = candidate["jobs"]


    name = profile.get(
        "name",
        ""
    )


    if not name.strip():

        name = candidate["filename"]


    if jobs:

        highest_match = max(
            job["match_score"]
            for job in jobs
        )


        average_match = (
            sum(
                job["match_score"]
                for job in jobs
            )
            / len(jobs)
        )

    else:

        highest_match = 0

        average_match = 0


    comparison_rows.append(
        {
            "Candidate": name,
            "Skills": len(
                candidate["skills"]
            ),
            "Jobs Analyzed": len(jobs),
            "Highest Match": (
                f"{highest_match:.1f}%"
            ),
            "Average Match": (
                f"{average_match:.1f}%"
            )
        }
    )


st.dataframe(
    pd.DataFrame(
        comparison_rows
    ),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "SkillGap AI uses information available in the "
    "uploaded resumes, job dataset and course dataset. "
    "Unavailable information is displayed as "
    "Not available."
)