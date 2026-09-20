import os
import json

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import (
    ChatPromptTemplate
)

from utils.skill_normalizer import (
    normalize_skills
)

load_dotenv()


def get_api_key():

    key = os.getenv(
        "GROQ_API_KEY"
    )

    if key:
        return key

    try:

        import streamlit as st

        return st.secrets[
            "GROQ_API_KEY"
        ]

    except Exception:

        return None


def get_llm():

    api_key = get_api_key()

    if not api_key:

        raise ValueError(
            "GROQ_API_KEY is not configured."
        )

    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key
    )


def extract_profile(
    resume_text
):

    llm = get_llm()

    prompt = ChatPromptTemplate.from_template(
        """
You are a resume parsing agent.

Read the resume below.

Return ONLY valid JSON.

Use these fields:

name
location
education
skills
projects
certifications
interests
experience

Rules:

- Do not invent information.
- Extract only information present in the resume.
- If information is unavailable, use an empty list or empty string.
- Put technical abilities in skills.
- Put degrees and schools in education.
- Put projects in projects.
- Put certificates in certifications.
- Put hobbies and career interests in interests.
- Put internships and jobs in experience.
- Return valid JSON only.
- Do not use markdown.
- Do not use code fences.

Resume:

{resume}
"""
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "resume": resume_text
        }
    )

    content = response.content.strip()

    content = content.replace(
        "```json",
        ""
    )

    content = content.replace(
        "```",
        ""
    )

    content = content.strip()

    try:

        profile = json.loads(
            content
        )

    except json.JSONDecodeError:

        profile = {
            "name": "",
            "location": "",
            "education": [],
            "skills": [],
            "projects": [],
            "certifications": [],
            "interests": [],
            "experience": []
        }

    profile["skills"] = normalize_skills(
        profile.get(
            "skills",
            []
        )
    )

    return profile