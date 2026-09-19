import os
import json

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from utils.skill_normalizer import normalize_skills


load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def extract_profile(resume_text):

    prompt = ChatPromptTemplate.from_template("""
You are a resume analysis agent.

Analyze the following resume.

Return ONLY valid JSON.

Resume:
{resume}

Use exactly this format:

{{
    "name": "",
    "education": [],
    "skills": [],
    "projects": [],
    "certifications": [],
    "interests": [],
    "experience": []
}}

Rules:

1. Do not invent information.
2. Extract only information actually present in the resume.
3. If something is not available, use an empty list or empty string.
4. Put technical skills inside "skills".
5. Put academic qualifications inside "education".
6. Put projects inside "projects".
7. Put certificates inside "certifications".
8. Put hobbies or career interests inside "interests".
9. Put work/internship experience inside "experience".
10. Return JSON only.
""")

    chain = prompt | llm

    response = chain.invoke({
        "resume": resume_text
    })

    content = response.content

    # Remove markdown formatting if the model adds it
    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    try:

        profile = json.loads(content)

    except json.JSONDecodeError:

        profile = {
            "name": "",
            "education": [],
            "skills": [],
            "projects": [],
            "certifications": [],
            "interests": [],
            "experience": []
        }

    # Normalize extracted skills
    profile["skills"] = normalize_skills(
        profile.get("skills", [])
    )

    return profile