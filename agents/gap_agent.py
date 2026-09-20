import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq

from langchain_core.prompts import (
    ChatPromptTemplate
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

        return None


    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key
    )


def explain_gap(
    job_title,
    matched_skills,
    missing_skills
):

    llm = get_llm()


    if not llm:

        return (
            "AI explanation is unavailable "
            "because the Groq API key is not configured."
        )


    prompt = ChatPromptTemplate.from_template(
        """
You are a career skill-gap advisor.

Target job:
{job}

Candidate skills already matched:
{matched}

Missing skills:
{missing}

Give a concise explanation.

Use exactly these sections:

Why These Skills Matter

Explain each missing skill in one short sentence.

What To Learn First

Identify the most important missing skill
and explain why.

Practical Action

Give three concrete learning actions.

Rules:

Do not invent job requirements.

Do not create tables.

Do not use HTML.

Do not use markdown tables.

Do not use <br>.

Keep the answer under 180 words.
"""
    )


    chain = prompt | llm


    response = chain.invoke(
        {
            "job": job_title,
            "matched": ", ".join(
                matched_skills
            ),
            "missing": ", ".join(
                missing_skills
            )
        }
    )


    return response.content