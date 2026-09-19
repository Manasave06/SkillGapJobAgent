SKILL_ALIASES = {
    "js": "javascript",
    "javascript": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node": "node.js",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "mysql": "sql",
    "postgresql": "sql",
    "mongodb": "mongodb",
    "html5": "html",
    "css3": "css",
    "python3": "python",
    "git": "git",
}


def normalize_skill(skill):
    skill = skill.lower().strip()

    return SKILL_ALIASES.get(skill, skill)


def normalize_skills(skills):
    result = []

    for skill in skills:
        normalized = normalize_skill(skill)

        if normalized not in result:
            result.append(normalized)

    return result