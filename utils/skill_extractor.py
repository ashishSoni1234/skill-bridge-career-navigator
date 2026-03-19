"""
Skill Extractor Module
======================
Extracts skills from user-provided text (resume or free-form input).

AI Integration:
  - PRIMARY: Uses LLaMA 3.1 (8B) via Groq API for intelligent skill extraction.
  - FALLBACK: If Groq fails (network error, invalid key, rate limit),
    automatically falls back to rule-based keyword matching.

Post-Processing (CRITICAL):
  - All AI-extracted skills are filtered through a SKILL WHITELIST
  - Removes noise: names, emails, universities, sentences, paragraphs
  - Normalizes casing and deduplicates results
  - Only real technical/professional skills pass through
"""

import os
import re
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ═══════════════════════════════════════════════════════════════════
# SKILL WHITELIST — comprehensive list of valid technical skills.
# AI output is filtered against this to remove noise (names, emails,
# universities, sentences, etc.). Only real skills pass through.
# ═══════════════════════════════════════════════════════════════════
SKILL_WHITELIST = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#",
    "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
    "r", "matlab", "perl", "lua", "dart", "assembly", "bash",
    "shell scripting", "powershell", "groovy", "elixir", "haskell",
    "objective-c", "visual basic", "vba",

    # Web Frontend
    "html", "css", "react", "angular", "vue", "vue.js", "svelte",
    "next.js", "nuxt.js", "gatsby", "jquery", "bootstrap",
    "tailwind css", "sass", "less", "webpack", "vite", "babel",
    "responsive design", "dom", "web components", "pwa",

    # Web Backend
    "node.js", "express", "express.js", "django", "flask", "fastapi",
    "spring", "spring boot", "asp.net", "ruby on rails", "laravel",
    "rest apis", "graphql", "grpc", "websockets", "authentication",
    "oauth", "jwt",

    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "sqlite", "oracle", "firebase",
    "database design", "indexing", "replication", "sharding",
    "performance tuning", "backup & recovery", "nosql",

    # Data Science & ML
    "machine learning", "deep learning", "nlp",
    "natural language processing", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "data visualization", "data analysis", "data cleaning",
    "data engineering", "data mining", "data modeling",
    "statistics", "mathematics", "linear algebra", "calculus",
    "probability", "hypothesis testing", "regression",
    "classification", "clustering", "neural networks",
    "cnn", "rnn", "lstm", "transformer", "transformers",
    "bert", "gpt", "llms", "large language models",
    "reinforcement learning", "generative ai", "rag",
    "mlops", "feature engineering", "model deployment",
    "a/b testing", "experiment tracking",

    # Tools & Platforms
    "jupyter", "jupyter notebook", "google colab", "anaconda",
    "tableau", "power bi", "excel", "google sheets",
    "looker", "metabase", "superset",

    # DevOps & Cloud
    "docker", "kubernetes", "ci/cd", "jenkins", "github actions",
    "gitlab ci", "circleci", "travis ci", "ansible", "puppet", "chef",
    "terraform", "cloudformation", "pulumi",
    "aws", "azure", "gcp", "google cloud", "heroku", "vercel",
    "netlify", "digitalocean",
    "linux", "ubuntu", "centos", "windows server",
    "nginx", "apache", "load balancing",
    "monitoring", "prometheus", "grafana", "datadog", "new relic",
    "logging", "elk stack", "splunk",
    "iam", "vpc", "s3", "ec2", "lambda", "cloudwatch",

    # CS Fundamentals
    "data structures", "algorithms", "oop",
    "object-oriented programming",
    "operating systems", "computer networks", "dbms",
    "database management systems",
    "system design", "design patterns", "solid principles",
    "microservices", "monolithic architecture",
    "distributed systems", "concurrency", "multithreading",
    "networking", "tcp/ip", "dns", "dhcp", "http", "https",

    # Version Control
    "git", "github", "gitlab", "bitbucket", "svn",

    # Testing
    "selenium", "cypress", "jest", "mocha", "pytest", "junit",
    "unit testing", "integration testing", "automation testing",
    "manual testing", "test planning", "api testing",
    "performance testing", "load testing", "tdd", "bdd",

    # Mobile
    "react native", "flutter", "swift", "kotlin", "swiftui",
    "android", "ios", "app store deployment", "xcode",
    "android studio", "ui design",

    # Security
    "network security", "cybersecurity", "penetration testing",
    "ethical hacking", "firewalls", "siem", "incident response",
    "cryptography", "owasp", "vulnerability assessment",
    "security", "encryption", "ssl", "tls",

    # Game Dev
    "unity", "unreal engine", "godot", "game design", "game physics",
    "3d mathematics", "shader programming", "opengl", "directx",
    "blender",

    # Embedded
    "rtos", "microcontrollers", "circuit design", "embedded linux",
    "debugging", "i2c", "spi", "uart", "arm", "arduino",
    "raspberry pi", "fpga", "pcb design", "iot",
    "internet of things",

    # Project Management & Business
    "agile", "scrum", "kanban", "jira", "trello", "asana",
    "confluence", "product strategy", "roadmap planning",
    "user research", "stakeholder management",
    "requirements gathering", "process modeling",
    "communication", "leadership", "project management",
    "uml", "bpmn",

    # Design
    "figma", "adobe xd", "sketch", "invision",
    "wireframing", "prototyping", "visual design",
    "usability testing", "design thinking",
    "information architecture", "user experience",
    "user interface", "graphic design", "adobe photoshop",
    "adobe illustrator",

    # Big Data
    "hadoop", "spark", "apache spark", "kafka", "apache kafka",
    "hive", "airflow", "apache airflow", "dbt",
    "etl", "data warehouse", "data lake", "snowflake",
    "bigquery", "redshift",

    # Other
    "api design", "technical writing", "documentation",
    "code review", "pair programming", "debugging",
    "performance optimization", "caching",
    "message queues", "rabbitmq", "celery",
    "regex", "xml", "json", "yaml", "csv",
    "blockchain", "web3", "solidity",
    "ar", "vr", "augmented reality", "virtual reality",
}


def _clean_skill_text(text: str) -> str:
    """
    Clean a single skill string:
    - Strip whitespace
    - Remove trailing periods, commas
    - Remove numbering like "1." or "- "
    """
    text = text.strip()
    text = re.sub(r"^\d+[\.\)]\s*", "", text)  # Remove "1." or "2)"
    text = re.sub(r"^[-•*]\s*", "", text)       # Remove "- " or "• "
    text = text.strip(" .,;:")
    return text


def _is_valid_skill(text: str) -> bool:
    """
    Filter out non-skill noise from AI output.
    Rejects:
      - Empty strings
      - Email addresses
      - URLs
      - Strings longer than 50 chars (likely sentences)
      - Strings with 4+ words (likely phrases/descriptions)
      - Pure numbers
    """
    if not text or len(text) < 1:
        return False
    if len(text) > 50:
        return False
    if "@" in text or "http" in text.lower():
        return False
    if text.replace(" ", "").isdigit():
        return False
    # Reject if more than 4 words (likely a sentence, not a skill)
    if len(text.split()) > 5:
        return False
    return True


def _normalize_skill(skill: str) -> str:
    """
    Normalize skill name for consistent display.
    Maps common variations to canonical form.
    """
    mappings = {
        "js": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
        "node": "Node.js",
        "nodejs": "Node.js",
        "react.js": "React",
        "reactjs": "React",
        "vue.js": "Vue.js",
        "angular.js": "Angular",
        "express.js": "Express.js",
        "next.js": "Next.js",
        "sklearn": "Scikit-learn",
        "sci-kit learn": "Scikit-learn",
        "scikit learn": "Scikit-learn",
        "postgres": "PostgreSQL",
        "mongo": "MongoDB",
        "k8s": "Kubernetes",
        "aws lambda": "Lambda",
        "amazon web services": "AWS",
        "google cloud platform": "GCP",
        "microsoft azure": "Azure",
        "object oriented programming": "OOP",
        "object-oriented programming": "OOP",
        "database management systems": "DBMS",
        "database management system": "DBMS",
        "operating system": "Operating Systems",
        "os": "Operating Systems",
        "cn": "Computer Networks",
        "computer network": "Computer Networks",
        "dsa": "Data Structures",
        "data structures and algorithms": "Data Structures",
        "large language models": "LLMs",
        "large language model": "LLMs",
        "natural language processing": "NLP",
        "ci cd": "CI/CD",
        "cicd": "CI/CD",
        "rest api": "REST APIs",
        "restful api": "REST APIs",
        "restful apis": "REST APIs",
    }
    lower = skill.lower().strip()
    if lower in mappings:
        return mappings[lower]
    return skill


def _filter_and_deduplicate(raw_skills: list[str], all_known_skills: list[str]) -> list[str]:
    """
    Post-processing pipeline (CRITICAL for clean output):
      1. Clean each skill string
      2. Validate it's a real skill (not a name/email/sentence)
      3. Check against whitelist OR known dataset skills
      4. Normalize casing
      5. Deduplicate (case-insensitive)

    Returns a clean, unique list of real skills.
    """
    # Build lowercase lookup sets
    whitelist_lower = SKILL_WHITELIST
    known_lower = {s.lower().strip() for s in all_known_skills}

    seen_lower = set()
    clean_skills = []

    for raw in raw_skills:
        skill = _clean_skill_text(raw)
        if not _is_valid_skill(skill):
            continue

        # Normalize common variations
        skill = _normalize_skill(skill)
        skill_lower = skill.lower().strip()

        # Skip duplicates
        if skill_lower in seen_lower:
            continue

        # Accept if in whitelist or in dataset's known skills
        if skill_lower in whitelist_lower or skill_lower in known_lower:
            seen_lower.add(skill_lower)
            # Use the canonical casing from known skills if available
            canonical = next(
                (s for s in all_known_skills if s.lower() == skill_lower),
                skill.title() if len(skill) > 3 else skill.upper(),
            )
            clean_skills.append(canonical)

    return clean_skills


# ═══════════════════════════════════════════════════════════════════
# AI EXTRACTION (PRIMARY)
# ═══════════════════════════════════════════════════════════════════

def extract_skills_ai(text: str) -> list[str]:
    """
    PRIMARY: AI-based skill extraction using LLaMA 3.1 via Groq.

    Sends user's text to Groq and asks LLaMA to extract ONLY
    technical/professional skills. Returns raw list (pre-filtering).

    Raises an exception on failure so the caller can fall back.
    """
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is not configured properly.")

    client = Groq(api_key=api_key)

    prompt = (
        "Extract ONLY technical and professional skills from the following text.\n"
        "Rules:\n"
        "- Return ONLY a JSON array of skill name strings\n"
        "- Include: programming languages, frameworks, tools, technologies, methodologies\n"
        "- EXCLUDE: person names, company names, university names, email addresses, "
        "job titles, dates, locations, sentences, descriptions\n"
        "- Keep skill names short (1-3 words max)\n"
        "- No duplicates\n\n"
        f"Text:\n{text}"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a skill extraction assistant. "
                    "Return ONLY a valid JSON array of technical skill strings. "
                    "No markdown, no explanation, no code fences."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        model="llama-3.1-8b-instant",
        temperature=0.1,
        max_tokens=1024,
    )

    response_text = chat_completion.choices[0].message.content.strip()

    # Clean markdown code fences if present
    if response_text.startswith("```"):
        response_text = re.sub(r"^```(?:json)?\s*", "", response_text)
        response_text = re.sub(r"\s*```$", "", response_text)

    skills = json.loads(response_text)

    if not isinstance(skills, list):
        raise ValueError("LLaMA 3 did not return a valid list.")

    return [str(s).strip() for s in skills if str(s).strip()]


# ═══════════════════════════════════════════════════════════════════
# FALLBACK EXTRACTION (RULE-BASED)
# ═══════════════════════════════════════════════════════════════════

def extract_skills_fallback(text: str, all_skills: list[str]) -> list[str]:
    """
    FALLBACK: Rule-based keyword matching.

    Scans input text for known skills using word-boundary regex.
    Only matches actual skill names from the dataset.
    """
    text_lower = text.lower()
    found = []

    for skill in all_skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)

    return found


# ═══════════════════════════════════════════════════════════════════
# MAIN EXTRACTION (AI + FALLBACK + POST-PROCESSING)
# ═══════════════════════════════════════════════════════════════════

def extract_skills(
    text: str,
    all_skills: list[str],
    simulate_failure: bool = False,
) -> tuple[list[str], str, str]:
    """
    Main extraction function — tries AI first, falls back to rule-based.

    Pattern:
        try:
            skills = extract_skills_ai(text)   ← LLaMA 3.1 via Groq
            method = "AI"
        except:
            skills = extract_skills_fallback()  ← keyword matching
            method = "Fallback"

    Post-processing:
        All results pass through _filter_and_deduplicate() to remove
        noise (names, emails, sentences) and keep only real skills.

    Args:
        text: User's input text.
        all_skills: Known skills from dataset (for fallback + filtering).
        simulate_failure: If True, skip AI to demo the fallback path.

    Returns:
        (clean_skills, method, error_message)
    """
    error_msg = ""

    if simulate_failure:
        # Demo mode: force fallback
        raw_skills = extract_skills_fallback(text, all_skills)
        method = "Fallback"
        error_msg = "AI was intentionally skipped (simulate failure mode)."
    else:
        try:
            raw_skills = extract_skills_ai(text)
            method = "AI"
        except Exception as e:
            # AI failed — automatically switch to fallback
            raw_skills = extract_skills_fallback(text, all_skills)
            method = "Fallback"
            err_str = str(e)
            if "429" in err_str or "rate" in err_str.lower():
                error_msg = "Groq API rate limit reached. Try again in a moment."
            elif "api_key" in err_str.lower() or "invalid" in err_str.lower() or "authentication" in err_str.lower():
                error_msg = "Invalid Groq API key. Check your .env file."
            elif "network" in err_str.lower() or "connection" in err_str.lower():
                error_msg = "Network error — could not reach Groq API."
            else:
                error_msg = f"AI extraction failed: {type(e).__name__}"

    # ── Post-processing: filter noise, deduplicate, normalize ──
    clean_skills = _filter_and_deduplicate(raw_skills, all_skills)

    return clean_skills, method, error_msg
