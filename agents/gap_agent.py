import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def explain_gap(
    job_title,
    matched_skills,
    missing_skills
):

    prompt = ChatPromptTemplate.from_template("""
You are a career skill-gap analysis agent.

Target job:
{job}

Skills already available:
{matched}

Missing skills:
{missing}

Explain:

1. Why each missing skill is important for this job.
2. What the candidate should learn.
3. Which missing skill should be learned first and why.
4. Give a short practical learning suggestion.

Do not invent job requirements.

Keep the answer clear and useful for a student.
""")

    chain = prompt | llm

    response = chain.invoke({
        "job": job_title,
        "matched": ", ".join(matched_skills),
        "missing": ", ".join(missing_skills)
    })

    return response.content