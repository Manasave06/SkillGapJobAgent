import pandas as pd


def load_jobs():

    jobs = pd.read_csv("data/jobs.csv")

    return jobs


def calculate_match(user_skills, required_skills):

    user_skills = set(skill.lower().strip() for skill in user_skills)

    required_skills = set(
        skill.lower().strip()
        for skill in required_skills
    )

    if not required_skills:
        return 0

    matched = user_skills.intersection(required_skills)

    score = (len(matched) / len(required_skills)) * 100

    return round(score, 2)


def match_jobs(user_skills):

    jobs = load_jobs()

    results = []

    for _, job in jobs.iterrows():

        required_skills = [
            x.strip()
            for x in job["skills"].split(",")
        ]

        score = calculate_match(
            user_skills,
            required_skills
        )

        matched = list(
            set(user_skills).intersection(
                set(required_skills)
            )
        )

        missing = list(
            set(required_skills) - set(user_skills)
        )

        results.append({
            "job_id": job["job_id"],
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "url": job["url"]
        })

    results.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return results