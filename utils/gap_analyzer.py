"""
Gap Analyzer Module
===================
Compares user's detected skills against required skills for a target role.

Features:
  - Intelligent skill matching via Semantic + Rule-Based Normalization
  - Synonym/alias resolution (e.g. GitHub → git, MySQL → sql)
  - Programming language flexibility (any one lang satisfies all lang requirements)
  - Category-based satisfaction (e.g. MySQL satisfies SQL requirement)
  - Correct match percentage: (matched / total_required) * 100
  - Priority classification: 🔴 High / 🟡 Medium / 🟢 Low for missing skills
  - Readiness summary with human-readable message
  - Prioritized skill ordering for logical learning path
  - Next-step guidance
  - Experience level detection (beginner vs advanced)
"""

from utils.skill_matcher import (
    match_skills,
    normalize_skill,
    get_match_method_label,
)

# ═══════════════════════════════════════════════════════════════════
# PRIORITY CLASSIFICATION
# Skills marked as HIGH are core/foundational for most roles.
# MEDIUM are important but more specialized.
# LOW are nice-to-have or tooling.
# ═══════════════════════════════════════════════════════════════════

HIGH_PRIORITY_SKILLS = {
    # CS Fundamentals (critical for interviews)
    "data structures", "algorithms", "oop", "operating systems",
    "dbms", "computer networks", "system design", "sql",
    # Core languages per domain
    "python", "java", "javascript", "c", "c++",
    # Core ML
    "machine learning", "deep learning", "statistics", "mathematics",
    # Core Web
    "html", "css", "react", "node.js",
    # Core DevOps
    "docker", "kubernetes", "linux", "aws",
    # Core Security
    "network security", "cryptography", "owasp",
    # Core Mobile
    "swift", "kotlin", "react native", "flutter",
}

MEDIUM_PRIORITY_SKILLS = {
    "git", "rest apis", "authentication", "database design",
    "typescript", "mongodb", "postgresql", "redis",
    "ci/cd", "terraform", "monitoring", "shell scripting",
    "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn",
    "data visualization", "nlp", "computer vision",
    "selenium", "api testing", "automation testing",
    "agile", "jira", "figma", "wireframing", "prototyping",
    "firebase", "graphql", "webpack", "responsive design",
    "mlops", "ansible", "networking",
    "penetration testing", "firewalls", "siem",
    "unity", "unreal engine",
    "rtos", "microcontrollers", "embedded linux",
}

# Everything else defaults to LOW priority


def get_skill_priority(skill: str) -> str:
    """
    Classify a skill as High / Medium / Low priority.

    Returns:
        "high", "medium", or "low"
    """
    lower = skill.lower().strip()
    if lower in HIGH_PRIORITY_SKILLS:
        return "high"
    elif lower in MEDIUM_PRIORITY_SKILLS:
        return "medium"
    else:
        return "low"


# ═══════════════════════════════════════════════════════════════════
# LOGICAL LEARNING ORDER
# Foundational skills come first, applied skills later.
# ═══════════════════════════════════════════════════════════════════

SKILL_PRIORITY_ORDER = [
    # Programming fundamentals
    "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript",
    # CS core
    "Data Structures", "Algorithms", "OOP", "Mathematics", "Statistics",
    "Operating Systems", "DBMS", "Computer Networks",
    # Web basics
    "HTML", "CSS", "DOM",
    # Databases
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Database Design",
    # Backend
    "REST APIs", "Node.js", "Authentication",
    # Frontend
    "React", "Responsive Design", "Webpack", "Tailwind CSS",
    # Data & ML
    "Pandas", "NumPy", "Scikit-learn", "Data Visualization",
    "Tableau", "Power BI", "Excel", "Jupyter",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
    "NLP", "Computer Vision", "LLMs", "Transformers", "MLOps",
    # DevOps & Cloud
    "Git", "Docker", "Kubernetes", "CI/CD", "Linux",
    "Shell Scripting", "Ansible",
    "AWS", "Azure", "GCP", "Terraform", "IAM",
    # Architecture
    "System Design", "Networking", "Monitoring", "Security",
    # Testing
    "Selenium", "Automation Testing", "Test Planning", "API Testing",
    "Performance Testing", "Manual Testing",
    # Mobile
    "React Native", "Flutter", "Swift", "Kotlin", "Firebase",
    "SQLite", "App Store Deployment", "UI Design",
    # Design
    "Figma", "Adobe XD", "Wireframing", "Prototyping",
    "Visual Design", "Usability Testing", "Design Thinking",
    "Information Architecture",
    # Security
    "Network Security", "SIEM", "Penetration Testing",
    "Firewalls", "Incident Response", "Cryptography",
    "OWASP", "Vulnerability Assessment",
    # Game Dev
    "Unity", "Unreal Engine", "3D Mathematics", "Game Physics",
    "Game Design", "Shader Programming",
    # Embedded
    "RTOS", "Microcontrollers", "Circuit Design", "Embedded Linux",
    "Debugging", "Assembly", "I2C", "SPI",
    # Business
    "Agile", "JIRA", "Product Strategy", "Roadmap Planning",
    "User Research", "Data Analysis", "Communication",
    "Requirements Gathering", "Process Modeling", "UML",
    "Stakeholder Management", "A/B Testing",
]


def analyze_gap(user_skills: list[str], required_skills: list[str]) -> dict:
    """
    Performs skill gap analysis using intelligent semantic matching.

    Uses the skill_matcher module for:
      - Synonym/alias resolution (GitHub → git, MySQL → sql)
      - Programming language flexibility (Python satisfies Java requirement)
      - Category-based satisfaction (databases, version control)
      - Substring/token matching ("Algorithm Design & Analysis" ↔ "Algorithms")

    Correctly computes:
        match_percentage = (len(matched) / len(required_skills)) * 100

    Returns:
        {
            "matched": [{"skill": "Python", "priority": "high", "matched_by": "...", "match_type": "..."}, ...],
            "missing": [{"skill": "Docker", "priority": "high"}, ...],
            "match_percentage": 75.0,
            "matched_list": ["Python", ...],
            "missing_list": ["Docker", ...],
            "match_method": "Semantic + Rule-Based Normalization",
        }
    """
    # Use the intelligent skill matcher
    result = match_skills(user_skills, required_skills)

    # Add priority classification to matched skills
    matched_with_priority = sorted(
        [
            {
                "skill": m["skill"],
                "priority": get_skill_priority(m["skill"]),
                "matched_by": m.get("matched_by", m["skill"]),
                "match_type": m.get("match_type", "exact"),
            }
            for m in result["matched"]
        ],
        key=lambda x: ({"high": 0, "medium": 1, "low": 2}[x["priority"]], x["skill"]),
    )

    # Add priority classification to missing skills
    missing_with_priority = sorted(
        [
            {
                "skill": m["skill"],
                "priority": get_skill_priority(m["skill"]),
            }
            for m in result["missing"]
        ],
        key=lambda x: ({"high": 0, "medium": 1, "low": 2}[x["priority"]], x["skill"]),
    )

    return {
        "matched": matched_with_priority,
        "missing": missing_with_priority,
        "match_percentage": result["match_percentage"],
        "matched_list": result["matched_list"],
        "missing_list": result["missing_list"],
        "match_method": result.get("method", "Semantic + Rule-Based Normalization"),
    }


def detect_experience_level(text: str) -> str:
    """
    Detect user's experience level from their input text.

    Returns: "beginner", "intermediate", or "advanced"
    """
    text_lower = text.lower()

    advanced_signals = [
        "senior", "lead", "architect", "principal", "staff",
        "5+ years", "6+ years", "7+ years", "8+ years", "10+ years",
        "managed team", "led team", "designed system", "scaled",
        "microservices", "distributed", "production",
    ]
    intermediate_signals = [
        "2+ years", "3+ years", "4+ years", "experience with",
        "worked on", "developed", "implemented", "built",
        "contributed", "maintained",
    ]

    advanced_count = sum(1 for s in advanced_signals if s in text_lower)
    intermediate_count = sum(1 for s in intermediate_signals if s in text_lower)

    if advanced_count >= 2:
        return "advanced"
    elif intermediate_count >= 2 or advanced_count >= 1:
        return "intermediate"
    else:
        return "beginner"


def get_readiness_summary(match_percentage: float, missing_count: int, role: str) -> str:
    """
    Generates a human-readable readiness summary.
    """
    if match_percentage == 100:
        return f"🎉 You are **100% ready** for the **{role}** role! You have all the required skills."
    elif match_percentage >= 75:
        return (
            f"You are **{match_percentage}%** ready for the **{role}** role. "
            f"Almost there! Just **{missing_count}** skill{'s' if missing_count != 1 else ''} to go."
        )
    elif match_percentage >= 50:
        return (
            f"You are **{match_percentage}%** ready for the **{role}** role. "
            f"You need to focus on **{missing_count}** key missing skill{'s' if missing_count != 1 else ''}."
        )
    elif match_percentage > 0:
        return (
            f"You are **{match_percentage}%** ready for the **{role}** role. "
            f"There are **{missing_count}** skills you need to learn."
        )
    else:
        return (
            f"You are **0%** ready for the **{role}** role. "
            f"You need to learn all **{missing_count}** required skills — "
            f"but don't worry, the roadmap below will guide you!"
        )


def get_prioritized_skills(missing_skills: list[str]) -> list[str]:
    """
    Returns missing skills sorted in logical learning order.
    High-priority foundational skills come first.
    """
    priority_lower = {s.lower(): idx for idx, s in enumerate(SKILL_PRIORITY_ORDER)}

    def sort_key(skill):
        lower = skill.lower()
        if lower in priority_lower:
            return (0, priority_lower[lower])
        return (1, lower)

    return sorted(missing_skills, key=sort_key)


def get_next_step_guidance(prioritized_skills: list[str]) -> str:
    """
    Generates a recommended learning path string.
    Focuses on high-priority skills first.
    """
    if not prioritized_skills:
        return "You're all set — no additional skills needed! 🎯"

    if len(prioritized_skills) == 1:
        return f"Focus on **{prioritized_skills[0]}** to complete your skill set."

    # Show up to 5 skills in the path
    path_skills = prioritized_skills[:5]
    path = f"Start with **{path_skills[0]}**"
    for s in path_skills[1:]:
        path += f" → then **{s}**"

    if len(prioritized_skills) > 5:
        path += f" → and {len(prioritized_skills) - 5} more"

    return path
