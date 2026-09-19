def opportunity_unlock(jobs, current_skills):

    current_skills = set(
        skill.lower()
        for skill in current_skills
    )

    skill_impact = {}

    for job in jobs:

        missing = set(
            job["missing_skills"]
        )

        for skill in missing:

            if skill not in skill_impact:
                skill_impact[skill] = 0

            skill_impact[skill] += 1

    result = []

    for skill, count in skill_impact.items():

        result.append({
            "skill": skill,
            "additional_jobs": count
        })

    result.sort(
        key=lambda x: x["additional_jobs"],
        reverse=True
    )

    return result