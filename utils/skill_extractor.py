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
# JSON CLEANUP UTILITIES
# ═══════════════════════════════════════════════════════════════════

import logging
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1


def _clean_json_response(response_text: str) -> str:
    """
    Attempt to clean/repair a potentially malformed JSON response from AI.

    Steps:
      1. Strip leading/trailing whitespace
      2. Remove markdown code fences (```json ... ```)
      3. Extract JSON substring (first [ ... last ])
      4. Fix trailing commas before ] or }
      5. Remove non-printable characters
    """
    text = response_text.strip()

    # Remove markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # Try to extract JSON array substring
    bracket_start = text.find("[")
    bracket_end = text.rfind("]")
    if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
        text = text[bracket_start:bracket_end + 1]

    # Fix trailing commas (e.g., ["Python", "Java",] → ["Python", "Java"])
    text = re.sub(r",\s*]", "]", text)
    text = re.sub(r",\s*}", "}", text)

    # Remove non-printable characters (except newlines/tabs)
    text = re.sub(r"[^\x20-\x7E\n\t]", "", text)

    return text


def _parse_json_safe(response_text: str) -> list:
    """
    Attempt to parse AI response as JSON with multiple cleanup strategies.

    Returns parsed list on success, raises ValueError on complete failure.
    """
    raw = response_text.strip()
    logger.info(f"[AI Response] (first 200 chars): {raw[:200]}")

    # Strategy 1: Direct parse
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            logger.info("[Parse] Strategy 1 (direct) succeeded.")
            return result
    except json.JSONDecodeError:
        pass

    # Strategy 2: Clean and parse
    cleaned = _clean_json_response(raw)
    try:
        result = json.loads(cleaned)
        if isinstance(result, list):
            logger.info("[Parse] Strategy 2 (cleaned) succeeded.")
            return result
    except json.JSONDecodeError:
        pass

    # Strategy 3: Try to find a JSON array anywhere in the text
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                logger.info("[Parse] Strategy 3 (regex extract) succeeded.")
                return result
        except json.JSONDecodeError:
            pass

    # Strategy 4: Split by lines/commas and extract skill-like strings
    partial_skills = _extract_partial_skills(raw)
    if partial_skills:
        logger.info(f"[Parse] Strategy 4 (partial recovery) extracted {len(partial_skills)} skills.")
        return partial_skills

    raise ValueError(f"Could not parse AI response after all cleanup strategies.")


def _extract_partial_skills(text: str) -> list[str]:
    """
    Last-resort: try to extract skill-like strings from a malformed response.
    Looks for quoted strings that look like skill names.
    """
    # Find all quoted strings
    matches = re.findall(r'"([^"]{1,50})"', text)
    if matches:
        # Filter to only skill-like entries
        skills = [m.strip() for m in matches if m.strip() and len(m.strip()) <= 50]
        return skills
    return []


# ═══════════════════════════════════════════════════════════════════
# AI EXTRACTION (PRIMARY) — with retry + robust parsing
# ═══════════════════════════════════════════════════════════════════

def _call_groq_skill_extraction(client, text: str) -> str:
    """
    Make a single API call to Groq for skill extraction.
    Returns the raw response text.
    """
    prompt = (
        "Extract ONLY technical and professional skills from the following text.\n"
        "Rules:\n"
        "- Return ONLY a valid JSON array of skill name strings\n"
        "- Include: programming languages, frameworks, tools, technologies, methodologies\n"
        "- EXCLUDE: person names, company names, university names, email addresses, "
        "job titles, dates, locations, sentences, descriptions\n"
        "- Keep skill names short (1-3 words max)\n"
        "- No duplicates\n"
        "- Return ONLY valid JSON. No explanation. No text. No markdown.\n\n"
        f"Text:\n{text}"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a skill extraction assistant. "
                    "Return ONLY a valid JSON array of technical skill strings. "
                    "No markdown, no explanation, no code fences. "
                    "Example output: [\"Python\", \"Docker\", \"SQL\"]"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        model="llama-3.1-8b-instant",
        temperature=0.1,
        max_tokens=1024,
    )

    return chat_completion.choices[0].message.content.strip()


def extract_skills_ai(text: str) -> list[str]:
    """
    PRIMARY: AI-based skill extraction using LLaMA 3.1 via Groq.

    Features:
      - 3 retry attempts before giving up
      - Robust JSON cleanup and parsing
      - Partial result recovery from malformed responses
      - Detailed logging for debugging

    Raises an exception ONLY on critical failures (network, auth).
    """
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is not configured properly.")

    client = Groq(api_key=api_key)

    last_error = None
    last_response = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"[Skill Extraction] Attempt {attempt}/{MAX_RETRIES}...")
            response_text = _call_groq_skill_extraction(client, text)
            last_response = response_text

            # Parse with robust cleanup
            skills = _parse_json_safe(response_text)

            if not isinstance(skills, list):
                raise ValueError("AI did not return a valid list.")

            result = [str(s).strip() for s in skills if str(s).strip()]

            if result:
                logger.info(f"[Skill Extraction] ✅ Success on attempt {attempt}. Extracted {len(result)} skills.")
                return result
            else:
                logger.warning(f"[Skill Extraction] Attempt {attempt}: Empty result, retrying...")
                last_error = ValueError("AI returned empty skills list")

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"[Skill Extraction] Attempt {attempt} parse error: {e}")
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            continue

        except Exception as e:
            err_str = str(e).lower()
            # Critical errors — don't retry, raise immediately
            if any(kw in err_str for kw in ["api_key", "invalid", "authentication", "unauthorized", "401"]):
                logger.error(f"[Skill Extraction] ❌ Auth error (no retry): {e}")
                raise
            if any(kw in err_str for kw in ["network", "connection", "timeout", "dns"]):
                logger.error(f"[Skill Extraction] ❌ Network error (no retry): {e}")
                raise
            if "429" in str(e) or "rate" in err_str:
                logger.warning(f"[Skill Extraction] ⚠️ Rate limited on attempt {attempt}")
                last_error = e
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS * 2)  # Longer delay for rate limits
                continue

            logger.warning(f"[Skill Extraction] Attempt {attempt} error: {e}")
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            continue

    # All retries exhausted — try one last partial recovery from last response
    if last_response:
        logger.info("[Skill Extraction] All retries exhausted. Attempting final partial recovery...")
        partial = _extract_partial_skills(last_response)
        if partial:
            logger.info(f"[Skill Extraction] ✅ Partial recovery: {len(partial)} skills from last response.")
            return partial

    # Truly failed
    raise last_error or ValueError("AI skill extraction failed after all retries.")


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

    Robust behavior:
      - When simulate_failure=False: ALWAYS prioritizes AI with 3 retries
        and JSON repair. Only falls back on true critical failures
        (network down, API key invalid).
      - When simulate_failure=True: Forces fallback mode.

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
        logger.info("[Extract] Simulate failure ON — using fallback.")
        raw_skills = extract_skills_fallback(text, all_skills)
        method = "Fallback"
        error_msg = "AI was intentionally skipped (simulate failure mode)."
    else:
        try:
            raw_skills = extract_skills_ai(text)
            method = "AI"
            logger.info(f"[Extract] ✅ AI extraction successful. {len(raw_skills)} raw skills.")
        except Exception as e:
            # AI truly failed after all retries — switch to fallback
            logger.error(f"[Extract] ❌ AI failed after all retries: {e}. Switching to fallback.")
            raw_skills = extract_skills_fallback(text, all_skills)
            method = "Fallback"
            err_str = str(e)
            if "429" in err_str or "rate" in err_str.lower():
                error_msg = "Groq API rate limit reached after retries. Try again in a moment."
            elif "api_key" in err_str.lower() or "invalid" in err_str.lower() or "authentication" in err_str.lower():
                error_msg = "Invalid Groq API key. Check your .env file."
            elif "network" in err_str.lower() or "connection" in err_str.lower():
                error_msg = "Network error — could not reach Groq API."
            else:
                error_msg = f"AI extraction failed after {MAX_RETRIES} retries: {type(e).__name__}"

    # ── Post-processing: filter noise, deduplicate, normalize ──
    clean_skills = _filter_and_deduplicate(raw_skills, all_skills)

    return clean_skills, method, error_msg
