import pandas as pd


def load_courses():

    return pd.read_csv(
        "data/courses.csv"
    )


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
                == "true"
            ]

        if len(matches) == 0:
            continue

        matches = matches.sort_values(
            "duration_weeks"
        )

        course = matches.iloc[0]

        recommendations.append(
            {
                "skill": skill,
                "course": course[
                    "course_name"
                ],
                "provider": course[
                    "provider"
                ],
                "duration_weeks": int(
                    course[
                        "duration_weeks"
                    ]
                ),
                "cost": float(
                    course["cost"]
                ),
                "is_free":
                    str(
                        course["is_free"]
                    ).lower()
                    == "true",
                "level": course[
                    "level"
                ],
                "url": course[
                    "url"
                ]
            }
        )

    return recommendations


def calculate_time_and_cost(
    courses
):

    total_weeks = sum(
        course["duration_weeks"]
        for course in courses
    )

    total_cost = sum(
        course["cost"]
        for course in courses
    )

    return (
        total_weeks,
        total_cost
    )