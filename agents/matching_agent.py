import pandas as pd
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from utils.skill_normalizer import normalize_skill


# =========================================================
# LOAD EMBEDDING MODEL
# =========================================================

@lru_cache(maxsize=1)
def load_embedding_model():

    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )


# =========================================================
# LOAD JOBS
# =========================================================

def load_jobs():

    return pd.read_csv(
        "data/jobs.csv"
    )


# =========================================================
# SEMANTIC SIMILARITY
# =========================================================

def semantic_skill_similarity(
    user_skills,
    required_skills
):

    if not user_skills or not required_skills:

        return 0, []


    model = load_embedding_model()


    user_skills = [
        normalize_skill(skill)
        for skill in user_skills
    ]

    required_skills = [
        normalize_skill(skill)
        for skill in required_skills
    ]


    user_embeddings = model.encode(
        user_skills
    )

    required_embeddings = model.encode(
        required_skills
    )


    similarity_matrix = cosine_similarity(
        required_embeddings,
        user_embeddings
    )


    matched_skills = []

    best_scores = []


    for index, required_skill in enumerate(
        required_skills
    ):

        best_index = similarity_matrix[
            index
        ].argmax()

        best_score = similarity_matrix[
            index
        ][best_index]

        best_user_skill = user_skills[
            best_index
        ]

        best_scores.append(
            best_score
        )


        # Exact match
        if required_skill == best_user_skill:

            matched_skills.append(
                required_skill
            )

        # Semantic match
        elif best_score >= 0.65:

            matched_skills.append(
                required_skill
            )


    semantic_score = (
        sum(best_scores)
        / len(best_scores)
    ) * 100


    return (
        round(semantic_score, 2),
        list(
            dict.fromkeys(
                matched_skills
            )
        )
    )


# =========================================================
# JOB MATCHING
# =========================================================

def match_jobs(
    user_skills,
    candidate_location=None
):

    jobs = load_jobs()

    results = []


    normalized_user_skills = [
        normalize_skill(skill)
        for skill in user_skills
    ]


    for _, job in jobs.iterrows():

        required_skills = [
            skill.strip()
            for skill in str(
                job["skills"]
            ).split(",")
        ]


        normalized_required = [
            normalize_skill(skill)
            for skill in required_skills
        ]


        # -------------------------------------------------
        # EXACT MATCHING
        # -------------------------------------------------

        exact_matches = set(
            normalized_user_skills
        ).intersection(
            set(normalized_required)
        )


        skill_coverage = (
            len(exact_matches)
            / len(normalized_required)
        ) * 100 if normalized_required else 0


        # -------------------------------------------------
        # SEMANTIC MATCHING
        # -------------------------------------------------

        semantic_score, semantic_matches = (
            semantic_skill_similarity(
                normalized_user_skills,
                normalized_required
            )
        )


        # -------------------------------------------------
        # FINAL MATCH SCORE
        # -------------------------------------------------

        final_score = (
            skill_coverage * 0.60
            + semantic_score * 0.40
        )


        # -------------------------------------------------
        # MISSING SKILLS
        # -------------------------------------------------

        matched = list(
            dict.fromkeys(
                list(exact_matches)
                + semantic_matches
            )
        )


        missing = [
            skill
            for skill in normalized_required
            if skill not in matched
        ]


        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        job_location = str(
            job.get(
                "location",
                ""
            )
        )


        location_fit = 100


        if (
            candidate_location
            and candidate_location != "Not specified"
        ):

            candidate_location_lower = (
                str(candidate_location)
                .lower()
            )

            job_location_lower = (
                job_location
                .lower()
            )


            if (
                candidate_location_lower
                in job_location_lower
                or job_location_lower
                in candidate_location_lower
            ):

                location_fit = 100

            else:

                location_fit = 50


        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        results.append({

            "job_id": job["job_id"],

            "title": job["title"],

            "company": job["company"],

            "location": job_location,

            "match_score": round(
                final_score,
                2
            ),

            "skill_coverage": round(
                skill_coverage,
                2
            ),

            "semantic_similarity": round(
                semantic_score,
                2
            ),

            "location_fit": location_fit,

            "matched_skills": matched,

            "missing_skills": missing,

            "url": job.get(
                "url",
                ""
            )

        })


    # Highest score first
    results.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )


    return results