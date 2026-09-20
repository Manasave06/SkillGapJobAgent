import pandas as pd
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from utils.skill_normalizer import normalize_skill


# =========================================================
# LOAD JOBS
# =========================================================

@lru_cache(maxsize=1)
def load_jobs():

    return pd.read_csv(
        "data/jobs.csv"
    )


# =========================================================
# LOAD EMBEDDING MODEL ONLY ONCE
# =========================================================

@lru_cache(maxsize=1)
def load_embedding_model():

    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )


# =========================================================
# NORMALIZE SKILL LIST
# =========================================================

def prepare_skills(skills):

    result = []

    for skill in skills:

        if not skill:
            continue

        normalized = normalize_skill(
            str(skill)
        )

        if normalized not in result:

            result.append(
                normalized
            )

    return result


# =========================================================
# SEMANTIC MATCHING
# =========================================================

def semantic_matches(
    user_skills,
    required_skills
):

    if not user_skills or not required_skills:

        return {}

    model = load_embedding_model()

    user_embeddings = model.encode(
        user_skills,
        normalize_embeddings=True
    )

    required_embeddings = model.encode(
        required_skills,
        normalize_embeddings=True
    )

    matrix = cosine_similarity(
        required_embeddings,
        user_embeddings
    )

    results = {}

    for i, required in enumerate(
        required_skills
    ):

        best_index = matrix[i].argmax()

        best_score = float(
            matrix[i][best_index]
        )

        best_user_skill = user_skills[
            best_index
        ]

        results[required] = (
            best_user_skill,
            best_score
        )

    return results


# =========================================================
# MATCH ONE JOB
# =========================================================

def calculate_job_match(
    user_skills,
    job,
    candidate_location=""
):

    user_skills = prepare_skills(
        user_skills
    )

    required_skills = [
        normalize_skill(skill.strip())
        for skill in str(
            job["skills"]
        ).split(",")
        if skill.strip()
    ]

    required_skills = list(
        dict.fromkeys(
            required_skills
        )
    )

    # -----------------------------------------------------
    # EXACT MATCH
    # -----------------------------------------------------

    exact_matches = sorted(
        set(user_skills).intersection(
            set(required_skills)
        )
    )

    # -----------------------------------------------------
    # SEMANTIC MATCH
    # -----------------------------------------------------

    semantic_data = semantic_matches(
        user_skills,
        required_skills
    )

    semantic_matches_list = []

    for required in required_skills:

        if required in exact_matches:
            continue

        if required not in semantic_data:
            continue

        best_user_skill, score = (
            semantic_data[required]
        )

        # High threshold so unrelated skills
        # are not counted as matches.
        if score >= 0.82:

            semantic_matches_list.append(
                required
            )

    matched_skills = list(
        dict.fromkeys(
            exact_matches +
            semantic_matches_list
        )
    )

    # -----------------------------------------------------
    # MISSING SKILLS
    # -----------------------------------------------------

    missing_skills = [
        skill
        for skill in required_skills
        if skill not in matched_skills
    ]

    # -----------------------------------------------------
    # SKILL COVERAGE
    # -----------------------------------------------------

    if required_skills:

        skill_coverage = (
            len(matched_skills)
            /
            len(required_skills)
        ) * 100

    else:

        skill_coverage = 0

    # -----------------------------------------------------
    # LOCATION
    # -----------------------------------------------------

    job_location = str(
        job.get(
            "location",
            ""
        )
    )

    candidate_location = str(
        candidate_location or ""
    )

    if not candidate_location:

        location_fit = 50

    elif (
        candidate_location.lower()
        in job_location.lower()
        or
        job_location.lower()
        in candidate_location.lower()
    ):

        location_fit = 100

    else:

        location_fit = 50

    # -----------------------------------------------------
    # FINAL SCORE
    # -----------------------------------------------------
    #
    # Skill coverage is the main factor.
    # Location has a smaller effect.
    #
    # 90% skill coverage
    # 10% location
    #
    # This prevents semantic similarity from
    # artificially inflating the score.
    # -----------------------------------------------------

    final_score = (
        skill_coverage * 0.90
        +
        location_fit * 0.10
    )

    return {
        "job_id": job["job_id"],
        "title": job["title"],
        "company": job["company"],
        "location": job_location,
        "match_score": round(
            final_score,
            1
        ),
        "skill_coverage": round(
            skill_coverage,
            1
        ),
        "location_fit": round(
            location_fit,
            1
        ),
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "url": job.get(
            "url",
            ""
        )
    }


# =========================================================
# MATCH ALL JOBS
# =========================================================

def match_jobs(
    user_skills,
    candidate_location=""
):

    jobs = load_jobs()

    results = []

    for _, job in jobs.iterrows():

        result = calculate_job_match(
            user_skills,
            job,
            candidate_location
        )

        results.append(
            result
        )

    results.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return results