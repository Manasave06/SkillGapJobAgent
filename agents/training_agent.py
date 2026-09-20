import pandas as pd


# =========================================================
# LOAD COURSES
# =========================================================

def load_courses():

    return pd.read_csv(
        "data/courses.csv"
    )


# =========================================================
# RECOMMEND COURSES
# =========================================================

def recommend_courses(
    missing_skills,
    free_only=False
):

    courses = load_courses()

    recommendations = []


    for skill in missing_skills:

        matches = courses[
            courses["skill"]
            .astype(str)
            .str.lower()
            .str.strip()
            ==
            str(skill)
            .lower()
            .strip()
        ]


        if free_only:

            matches = matches[
                matches["is_free"]
                .astype(str)
                .str.lower()
                .isin(
                    [
                        "true",
                        "1",
                        "yes"
                    ]
                )
            ]


        if len(matches) == 0:

            continue


        matches = matches.sort_values(
            "duration_weeks"
        )


        course = matches.iloc[0]


        try:

            duration = int(
                course["duration_weeks"]
            )

        except Exception:

            duration = 0


        try:

            cost = float(
                course["cost"]
            )

        except Exception:

            cost = 0


        is_free = (
            str(
                course["is_free"]
            ).lower()
            in [
                "true",
                "1",
                "yes"
            ]
        )


        url = str(
            course.get(
                "url",
                ""
            )
        ).strip()


        if (
            not url
            or url.lower()
            in [
                "nan",
                "none",
                "null"
            ]
            or "example.com"
            in url.lower()
        ):

            url = ""


        recommendations.append(
            {
                "skill": skill,
                "course": course[
                    "course_name"
                ],
                "provider": course[
                    "provider"
                ],
                "duration_weeks": duration,
                "cost": cost,
                "is_free": is_free,
                "level": course[
                    "level"
                ],
                "url": url
            }
        )


    return recommendations


# =========================================================
# TIME AND COST
# =========================================================

def calculate_time_and_cost(
    courses
):

    total_weeks = sum(
        course[
            "duration_weeks"
        ]
        for course in courses
    )


    total_cost = sum(
        course[
            "cost"
        ]
        for course in courses
    )


    return (
        total_weeks,
        total_cost
    )