def opportunity_unlock(
    jobs,
    current_skills
):

    current_skills = {
        str(skill)
        .lower()
        .strip()
        for skill in current_skills
    }


    results = []


    for job in jobs:

        missing = {
            str(skill)
            .lower()
            .strip()
            for skill in job.get(
                "missing_skills",
                []
            )
        }


        for skill in missing:

            if skill in current_skills:

                continue


            results.append(
                {
                    "Skill": skill,
                    "Job": job["title"],
                    "Company": job["company"],
                    "Current Match": job[
                        "match_score"
                    ]
                }
            )


    return results