import streamlit as st
import pandas as pd

from utils.pdf_reader import extract_text_from_pdf
from agents.profile_agent import extract_profile
from agents.matching_agent import match_jobs
from agents.gap_agent import explain_gap
from agents.training_agent import recommend_courses, calculate_time_and_cost
from utils.scoring import opportunity_unlock


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="SkillGap AI",
    page_icon=None,
    layout="wide"
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "candidates" not in st.session_state:
    st.session_state.candidates = []

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("SkillGap AI")

st.write(
    "Analyze candidate skills, identify job gaps, "
    "and create personalized learning paths."
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.header("SkillGap AI")

st.sidebar.write(
    "Upload resumes to analyze candidate skills "
    "and match them with available jobs."
)

free_only = st.sidebar.checkbox(
    "Show only free courses",
    value=False
)


# ---------------------------------------------------------
# RESUME UPLOAD
# ---------------------------------------------------------

st.header("Upload Candidate Resumes")

uploaded_files = st.file_uploader(
    "Upload one or more resume PDF files",
    type=["pdf"],
    accept_multiple_files=True
)


# ---------------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------------

if uploaded_files:

    st.write(
        "Selected resumes:",
        len(uploaded_files)
    )

    for file in uploaded_files:
        st.write(file.name)

    if st.button("Analyze All Candidates"):

        candidates = []

        progress = st.progress(0)

        total_files = len(uploaded_files)

        for index, uploaded_file in enumerate(uploaded_files):

            try:

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
                    "filename": uploaded_file.name,
                    "resume_text": resume_text,
                    "profile": profile,
                    "skills": skills,
                    "jobs": jobs
                }

                candidates.append(candidate)

            except Exception as error:

                st.error(
                    f"Error processing {uploaded_file.name}: {error}"
                )

            progress.progress(
                (index + 1) / total_files
            )

        st.session_state.candidates = candidates
        st.session_state.analysis_done = True

        st.success(
            f"Analysis completed for {len(candidates)} candidates."
        )


# ---------------------------------------------------------
# STOP IF NO ANALYSIS
# ---------------------------------------------------------

if not st.session_state.analysis_done:

    st.info(
        "Upload resumes and click Analyze All Candidates."
    )

    st.stop()


if not st.session_state.candidates:

    st.warning(
        "No candidates were successfully analyzed."
    )

    st.stop()


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

st.header("Dashboard")

candidate_count = len(
    st.session_state.candidates
)

all_skills = []

all_jobs = []

for candidate in st.session_state.candidates:

    all_skills.extend(
        candidate["skills"]
    )

    all_jobs.extend(
        candidate["jobs"]
    )


unique_skills = set(
    skill.lower().strip()
    for skill in all_skills
)


total_jobs = 0

for candidate in st.session_state.candidates:
    total_jobs += len(
        candidate["jobs"]
    )


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Candidates",
        candidate_count
    )

with col2:
    st.metric(
        "Unique Skills",
        len(unique_skills)
    )

with col3:
    st.metric(
        "Jobs Analyzed",
        total_jobs
    )

with col4:
    st.metric(
        "Learning Resources",
        len(pd.read_csv("data/courses.csv"))
    )


# ---------------------------------------------------------
# CANDIDATE TABS
# ---------------------------------------------------------

st.header("Candidate Analysis")

candidate_names = []

for index, candidate in enumerate(
    st.session_state.candidates
):

    profile = candidate["profile"]

    name = profile.get(
        "name",
        ""
    )

    if not name:
        name = f"Candidate {index + 1}"

    candidate_names.append(
        name
    )


tabs = st.tabs(
    candidate_names
)


for index, tab in enumerate(tabs):

    candidate = st.session_state.candidates[index]

    profile = candidate["profile"]

    skills = candidate["skills"]

    jobs = candidate["jobs"]

    with tab:

        # -------------------------------------------------
        # BASIC PROFILE
        # -------------------------------------------------

        st.subheader("Candidate Profile")

        profile_col1, profile_col2 = st.columns(2)

        with profile_col1:

            name = profile.get(
                "name",
                ""
            )

            location = profile.get(
                "location",
                ""
            )

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

            education = profile.get(
                "education",
                []
            )

            experience = profile.get(
                "experience",
                []
            )

            certifications = profile.get(
                "certifications",
                []
            )

            interests = profile.get(
                "interests",
                []
            )

            st.write(
                "Education:"
            )

            if education:
                for item in education:
                    st.write(
                        f"- {item}"
                    )
            else:
                st.write(
                    "No education information found."
                )

            st.write(
                "Experience:"
            )

            if experience:
                for item in experience:
                    st.write(
                        f"- {item}"
                    )
            else:
                st.write(
                    "No experience information found."
                )


        # -------------------------------------------------
        # SKILLS
        # -------------------------------------------------

        st.subheader("Current Skills")

        if skills:

            skills_text = ", ".join(
                skills
            )

            st.write(
                skills_text
            )

        else:

            st.write(
                "No technical skills detected."
            )


        # -------------------------------------------------
        # CERTIFICATIONS
        # -------------------------------------------------

        if certifications:

            st.subheader("Certifications")

            for certificate in certifications:

                st.write(
                    f"- {certificate}"
                )


        # -------------------------------------------------
        # INTERESTS
        # -------------------------------------------------

        if interests:

            st.subheader("Interests")

            for interest in interests:

                st.write(
                    f"- {interest}"
                )


        # -------------------------------------------------
        # JOB MATCHING
        # -------------------------------------------------

        st.subheader("Job Matching")

        if not jobs:

            st.warning(
                "No jobs were found."
            )

        else:

            job_rows = []

            for job in jobs:

                job_rows.append(
                    {
                        "Job": job["title"],
                        "Company": job["company"],
                        "Location": job["location"],
                        "Match Score": job["match_score"],
                        "Skill Coverage": job["skill_coverage"],
                        "Location Fit": job["location_fit"]
                    }
                )

            job_dataframe = pd.DataFrame(
                job_rows
            )

            st.dataframe(
                job_dataframe,
                use_container_width=True,
                hide_index=True
            )


        # -------------------------------------------------
        # TOP JOB MATCHES
        # -------------------------------------------------

        st.subheader("Top Job Matches")

        top_jobs = jobs[:5]

        if top_jobs:

            for job_index, job in enumerate(top_jobs):

                st.write(
                    f"{job_index + 1}. {job['title']}"
                )

                st.write(
                    f"Company: {job['company']}"
                )

                st.write(
                    f"Location: {job['location']}"
                )

                st.write(
                    f"Match Score: {job['match_score']} percent"
                )

                st.write(
                    f"Skill Coverage: {job['skill_coverage']} percent"
                )

                matched = job.get(
                    "matched_skills",
                    []
                )

                missing = job.get(
                    "missing_skills",
                    []
                )

                st.write(
                    "Matched Skills:"
                )

                if matched:

                    st.write(
                        ", ".join(matched)
                    )

                else:

                    st.write(
                        "None"
                    )

                st.write(
                    "Missing Skills:"
                )

                if missing:

                    st.write(
                        ", ".join(missing)
                    )

                else:

                    st.write(
                        "None"
                    )

                if job.get("url"):

                    st.write(
                        f"Job Link: {job['url']}"
                    )

                st.divider()


        # -------------------------------------------------
        # SELECT JOB
        # -------------------------------------------------

        if jobs:

            st.subheader(
                "Detailed Skill Gap Analysis"
            )

            job_options = []

            for job in jobs:

                label = (
                    f"{job['title']} - "
                    f"{job['company']} - "
                    f"{job['match_score']} percent"
                )

                job_options.append(
                    label
                )

            selected_index = st.selectbox(
                "Select a job",
                range(len(job_options)),
                format_func=lambda x: job_options[x],
                key=f"job_select_{index}"
            )

            selected_job = jobs[selected_index]

            st.write(
                f"Job Title: {selected_job['title']}"
            )

            st.write(
                f"Company: {selected_job['company']}"
            )

            st.write(
                f"Location: {selected_job['location']}"
            )

            st.write(
                f"Match Score: {selected_job['match_score']} percent"
            )

            st.write(
                f"Skill Coverage: {selected_job['skill_coverage']} percent"
            )

            st.write(
                f"Location Fit: {selected_job['location_fit']} percent"
            )

            st.write(
                "Required Skills:"
            )

            st.write(
                ", ".join(
                    selected_job["required_skills"]
                )
            )

            st.write(
                "Matched Skills:"
            )

            if selected_job["matched_skills"]:

                st.write(
                    ", ".join(
                        selected_job["matched_skills"]
                    )
                )

            else:

                st.write(
                    "None"
                )

            st.write(
                "Missing Skills:"
            )

            if selected_job["missing_skills"]:

                st.write(
                    ", ".join(
                        selected_job["missing_skills"]
                    )
                )

            else:

                st.write(
                    "None"
                )


            # ---------------------------------------------
            # AI GAP EXPLANATION
            # ---------------------------------------------

            explain_key = (
                f"explain_{index}_{selected_index}"
            )

            if st.button(
                "Generate AI Skill Gap Explanation",
                key=explain_key
            ):

                with st.spinner(
                    "Generating explanation..."
                ):

                    try:

                        explanation = explain_gap(
                            selected_job["title"],
                            selected_job["matched_skills"],
                            selected_job["missing_skills"]
                        )

                        st.write(
                            explanation
                        )

                    except Exception as error:

                        st.error(
                            f"Could not generate explanation: {error}"
                        )


            # ---------------------------------------------
            # TRAINING PATH
            # ---------------------------------------------

            st.subheader(
                "Training Path"
            )

            missing_skills = selected_job.get(
                "missing_skills",
                []
            )

            if missing_skills:

                courses = recommend_courses(
                    missing_skills,
                    free_only=free_only
                )

                if courses:

                    course_rows = []

                    for course in courses:

                        course_rows.append(
                            {
                                "Missing Skill": course["skill"],
                                "Course": course["course"],
                                "Provider": course["provider"],
                                "Duration": (
                                    f"{course['duration_weeks']} weeks"
                                ),
                                "Cost": course["cost"],
                                "Level": course["level"]
                            }
                        )

                    course_dataframe = pd.DataFrame(
                        course_rows
                    )

                    st.dataframe(
                        course_dataframe,
                        use_container_width=True,
                        hide_index=True
                    )

                    total_weeks, total_cost = (
                        calculate_time_and_cost(
                            courses
                        )
                    )

                    time_col1, time_col2 = st.columns(2)

                    with time_col1:

                        st.metric(
                            "Time to Ready",
                            f"{total_weeks} weeks"
                        )

                    with time_col2:

                        st.metric(
                            "Total Training Cost",
                            f"Rs {total_cost:.0f}"
                        )


                    st.write(
                        "Courses required to close the identified skill gaps:"
                    )

                    for course in courses:

                        st.write(
                            f"{course['course']} "
                            f"by {course['provider']}"
                        )

                        st.write(
                            f"Skill: {course['skill']}"
                        )

                        st.write(
                            f"Duration: "
                            f"{course['duration_weeks']} weeks"
                        )

                        st.write(
                            f"Cost: Rs {course['cost']}"
                        )

                        if course["url"]:

                            st.write(
                                f"Course Link: {course['url']}"
                            )

                        st.divider()

                else:

                    st.info(
                        "No matching courses were found "
                        "for the selected skill gaps."
                    )

            else:

                st.success(
                    "No missing skills were identified "
                    "for this job."
                )


        # -------------------------------------------------
        # OPPORTUNITY UNLOCK ENGINE
        # -------------------------------------------------

        st.subheader(
            "Opportunity Unlock Analysis"
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
            )

            skill_counts = skill_counts.sort_values(
                "Additional Jobs",
                ascending=False
            )

            st.write(
                "Skills that appear as missing requirements "
                "across the analyzed jobs:"
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


        # -------------------------------------------------
        # ROADMAP
        # -------------------------------------------------

        st.subheader(
            "Personalized Learning Roadmap"
        )

        if jobs:

            best_job = jobs[0]

            roadmap_missing = best_job.get(
                "missing_skills",
                []
            )

            if roadmap_missing:

                st.write(
                    "Step 1: Learn the most important missing skills."
                )

                for skill_number, skill in enumerate(
                    roadmap_missing[:3],
                    start=1
                ):

                    st.write(
                        f"{skill_number}. {skill}"
                    )

                st.write(
                    "Step 2: Complete the recommended courses."
                )

                st.write(
                    "Step 3: Build projects using the newly learned skills."
                )

                st.write(
                    "Step 4: Update the resume with demonstrated skills."
                )

                st.write(
                    "Step 5: Re-run SkillGap AI to measure the updated profile."
                )

            else:

                st.write(
                    "The candidate currently covers "
                    "the identified requirements."
                )


# ---------------------------------------------------------
# CANDIDATE COMPARISON
# ---------------------------------------------------------

st.header("Candidate Comparison")

comparison_rows = []

for candidate in st.session_state.candidates:

    profile = candidate["profile"]

    jobs = candidate["jobs"]

    name = profile.get(
        "name",
        ""
    )

    if not name:

        name = candidate["filename"]

    if jobs:

        average_score = sum(
            job["match_score"]
            for job in jobs
        ) / len(jobs)

        highest_score = jobs[0]["match_score"]

    else:

        average_score = 0
        highest_score = 0

    comparison_rows.append(
        {
            "Candidate": name,
            "Skills": len(
                candidate["skills"]
            ),
            "Jobs Analyzed": len(jobs),
            "Highest Match": round(
                highest_score,
                1
            ),
            "Average Match": round(
                average_score,
                1
            )
        }
    )


comparison_dataframe = pd.DataFrame(
    comparison_rows
)

st.dataframe(
    comparison_dataframe,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.write(
    "SkillGap AI converts resume information into "
    "structured skills, job matches, skill gaps, "
    "training paths, and time-to-ready estimates."
)