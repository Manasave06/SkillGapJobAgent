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
You are a professional resume understanding agent.

Analyze the resume carefully.

Return ONLY valid JSON.

The JSON must contain these fields:

"name"
"location"
"education"
"skills"
"projects"
"certifications"
"interests"
"experience"

Rules:

1. Do not invent information.
2. Extract only information actually present in the resume.
3. If information is unavailable, use an empty string or empty list.
4. Put technical skills inside skills.
5. Put education inside education.
6. Put projects inside projects.
7. Put certificates inside certifications.
8. Put hobbies and career interests inside interests.
9. Put work and internship experience inside experience.
10. Extract city, state, or country into location when available.
11. Return JSON only.
12. Do not include markdown.
13. Do not include code fences.
14. Make sure the response is valid JSON.

Resume:

{resume}
""")

    chain = prompt | llm

    response = chain.invoke({
        "resume": resume_text
    })

    content = response.content.strip()

    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    try:
        profile = json.loads(content)

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
        profile.get("skills", [])
    )

    return profile