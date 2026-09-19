from typing import TypedDict

from langgraph.graph import StateGraph, END

from agents.profile_agent import extract_profile
from agents.matching_agent import match_jobs
from agents.gap_agent import explain_gap
from agents.training_agent import (
    recommend_courses,
    calculate_time_and_cost
)


class AgentState(TypedDict):

    resume_text: str
    profile: dict
    jobs: list
    selected_job: dict
    gap_explanation: str
    courses: list
    total_weeks: int
    total_cost: float


def profile_node(state):

    profile = extract_profile(
        state["resume_text"]
    )

    return {
        "profile": profile
    }


def matching_node(state):

    skills = state["profile"]["skills"]

    jobs = match_jobs(skills)

    return {
        "jobs": jobs
    }


def gap_node(state):

    jobs = state["jobs"]

    if not jobs:

        return {
            "selected_job": {},
            "gap_explanation": ""
        }

    selected = jobs[0]

    explanation = explain_gap(
        selected["title"],
        selected["matched_skills"],
        selected["missing_skills"]
    )

    return {
        "selected_job": selected,
        "gap_explanation": explanation
    }


def training_node(state):

    missing = state["selected_job"].get(
        "missing_skills",
        []
    )

    courses = recommend_courses(
        missing,
        free_only=False
    )

    weeks, cost = calculate_time_and_cost(
        courses
    )

    return {
        "courses": courses,
        "total_weeks": weeks,
        "total_cost": cost
    }


workflow = StateGraph(AgentState)

workflow.add_node(
    "profile",
    profile_node
)

workflow.add_node(
    "matching",
    matching_node
)

workflow.add_node(
    "gap",
    gap_node
)

workflow.add_node(
    "training",
    training_node
)

workflow.set_entry_point("profile")

workflow.add_edge(
    "profile",
    "matching"
)

workflow.add_edge(
    "matching",
    "gap"
)

workflow.add_edge(
    "gap",
    "training"
)

workflow.add_edge(
    "training",
    END
)

app = workflow.compile()