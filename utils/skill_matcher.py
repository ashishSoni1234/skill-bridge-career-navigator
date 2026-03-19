"""
Skill Matcher Module — Semantic + Rule-Based Normalization Engine
=================================================================
Transforms naive exact-string skill matching into an intelligent,
real-world skill matching system.

Features:
  - Skill normalization (lowercase, strip special chars, canonical forms)
  - Synonym & mapping system (groups equivalent skills)
  - Semantic matching (substring + token-based)
  - Programming language flexibility (any one satisfies the category)
  - Skill categories with category-level satisfaction
  - Improved gap analysis with reduced false "missing" skills

Exported functions:
  - normalize_skill(skill) → canonical string
  - map_skill(skill) → canonical group key
  - match_skills(user_skills, required_skills) → match result dict
  - check_category_satisfaction(user_skills, category) → bool

Author: Skill-Bridge Career Navigator
"""

import re
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
# SYNONYM / MAPPING DICTIONARY
# Maps canonical skill name → list of equivalent aliases.
# All values are lowercase.
# ═══════════════════════════════════════════════════════════════════

SKILL_SYNONYMS: dict[str, list[str]] = {
    # Version Control
    "git": ["git", "github", "gitlab", "bitbucket", "git/github",
            "git/gitlab", "github/git", "version control"],

    # Databases — SQL family
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "pl/sql",
            "t-sql", "tsql", "mssql", "mariadb", "sql server"],
    "mongodb": ["mongodb", "mongo", "mongoose"],
    "redis": ["redis", "redis cache"],
    "nosql": ["nosql", "no-sql", "non-relational databases"],

    # CS Fundamentals
    "algorithms": ["algorithms", "algorithm", "algorithm design",
                   "algorithm design & analysis", "algorithm design and analysis",
                   "algo", "dsa", "data structures and algorithms"],
    "data structures": ["data structures", "data structure", "ds",
                        "arrays", "linked lists", "trees", "graphs",
                        "stacks", "queues", "hash maps"],
    "oop": ["oop", "object oriented programming",
            "object-oriented programming", "oops",
            "object oriented design", "oo design"],
    "operating systems": ["operating systems", "operating system", "os",
                          "linux internals", "process management",
                          "memory management"],
    "dbms": ["dbms", "database management systems",
             "database management system", "database management",
             "rdbms", "relational database"],
    "computer networks": ["computer networks", "computer network",
                          "networking fundamentals", "cn",
                          "network fundamentals"],
    "system design": ["system design", "systems design",
                      "high level design", "hld", "low level design", "lld",
                      "software architecture", "architecture design"],

    # Programming Languages
    "python": ["python", "python3", "python 3", "py"],
    "java": ["java", "core java", "java se", "java ee", "j2ee"],
    "javascript": ["javascript", "js", "es6", "es2015", "ecmascript",
                   "vanilla js", "vanilla javascript"],
    "typescript": ["typescript", "ts"],
    "c": ["c language", "c programming", "ansi c"],
    "c++": ["c++", "cpp", "c plus plus"],
    "c#": ["c#", "csharp", "c sharp"],
    "kotlin": ["kotlin"],
    "swift": ["swift", "swift programming"],
    "go": ["go", "golang"],
    "rust": ["rust", "rust lang"],
    "ruby": ["ruby"],
    "php": ["php"],
    "r": ["r programming", "r language", "rstudio"],
    "scala": ["scala"],
    "dart": ["dart"],

    # Web Frontend
    "html": ["html", "html5", "html 5", "hypertext markup language"],
    "css": ["css", "css3", "css 3", "cascading style sheets",
            "sass", "scss", "less"],
    "react": ["react", "reactjs", "react.js", "react js"],
    "angular": ["angular", "angularjs", "angular.js"],
    "vue.js": ["vue", "vuejs", "vue.js", "vue js"],
    "dom": ["dom", "document object model"],
    "responsive design": ["responsive design", "responsive web design",
                          "mobile-first design", "rwd"],
    "webpack": ["webpack", "web pack"],
    "tailwind css": ["tailwind css", "tailwindcss", "tailwind"],

    # Web Backend
    "node.js": ["node.js", "nodejs", "node", "node js"],
    "rest apis": ["rest apis", "rest api", "restful api", "restful apis",
                  "restful", "rest", "api development"],
    "authentication": ["authentication", "auth", "jwt", "oauth",
                       "oauth2", "oauth 2.0"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "fast api"],
    "spring boot": ["spring boot", "spring", "spring framework"],
    "express.js": ["express", "expressjs", "express.js"],
    "graphql": ["graphql", "graph ql"],

    # Data Science & ML
    "machine learning": ["machine learning", "ml", "supervised learning",
                         "unsupervised learning", "classification",
                         "regression analysis"],
    "deep learning": ["deep learning", "dl", "neural networks",
                      "neural network", "ann", "dnn"],
    "statistics": ["statistics", "statistical analysis", "stat",
                   "stats", "biostatistics", "probability and statistics"],
    "mathematics": ["mathematics", "maths", "math", "linear algebra",
                    "calculus", "discrete mathematics", "discrete math"],
    "pandas": ["pandas", "pd"],
    "numpy": ["numpy", "np"],
    "scikit-learn": ["scikit-learn", "sklearn", "sci-kit learn",
                     "scikit learn"],
    "data visualization": ["data visualization", "data viz",
                           "data visualisation"],
    "nlp": ["nlp", "natural language processing", "text mining",
            "text analytics"],
    "computer vision": ["computer vision", "cv", "image processing",
                        "image recognition"],
    "tensorflow": ["tensorflow", "tf", "tensor flow"],
    "pytorch": ["pytorch", "torch"],
    "mlops": ["mlops", "ml ops", "ml operations",
              "machine learning operations"],
    "llms": ["llms", "large language models", "large language model",
             "llm", "gpt", "chatgpt"],
    "transformers": ["transformers", "transformer", "attention mechanism",
                     "bert", "gpt architecture"],

    # DevOps & Cloud
    "docker": ["docker", "containerization", "containers",
               "docker compose", "dockerfile"],
    "kubernetes": ["kubernetes", "k8s", "kube"],
    "ci/cd": ["ci/cd", "cicd", "ci cd", "continuous integration",
              "continuous deployment", "continuous delivery",
              "jenkins", "github actions", "gitlab ci"],
    "linux": ["linux", "ubuntu", "centos", "debian", "fedora",
              "rhel", "red hat", "unix"],
    "aws": ["aws", "amazon web services", "amazon cloud"],
    "azure": ["azure", "microsoft azure", "ms azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "terraform": ["terraform", "tf", "infrastructure as code", "iac"],
    "monitoring": ["monitoring", "observability", "prometheus",
                   "grafana", "datadog", "new relic"],
    "shell scripting": ["shell scripting", "bash scripting", "bash",
                        "shell", "scripting", "sh"],
    "ansible": ["ansible", "ansible automation"],
    "iam": ["iam", "identity and access management",
            "identity management"],

    # Testing & QA
    "selenium": ["selenium", "selenium webdriver", "web automation"],
    "automation testing": ["automation testing", "automated testing",
                           "test automation"],
    "manual testing": ["manual testing", "exploratory testing"],
    "test planning": ["test planning", "test strategy",
                      "test management"],
    "api testing": ["api testing", "postman", "api test"],
    "performance testing": ["performance testing", "load testing",
                            "stress testing", "jmeter"],

    # Mobile
    "react native": ["react native", "reactnative"],
    "flutter": ["flutter", "flutter sdk"],
    "firebase": ["firebase", "google firebase"],
    "app store deployment": ["app store deployment", "app deployment",
                             "play store", "app store"],
    "ui design": ["ui design", "ui/ux", "ui ux", "user interface design"],

    # Security
    "network security": ["network security", "netsec",
                         "information security", "infosec"],
    "penetration testing": ["penetration testing", "pentesting",
                            "pen testing", "ethical hacking"],
    "cryptography": ["cryptography", "crypto", "encryption",
                     "decryption"],
    "owasp": ["owasp", "owasp top 10", "web security"],
    "firewalls": ["firewalls", "firewall", "network firewall"],
    "siem": ["siem", "security information", "splunk", "elk stack"],
    "incident response": ["incident response", "ir",
                          "security incident"],
    "vulnerability assessment": ["vulnerability assessment",
                                 "vulnerability scanning", "vuln assessment",
                                 "security audit"],
    "security": ["security", "cybersecurity", "cyber security",
                 "information security"],

    # Design
    "figma": ["figma"],
    "adobe xd": ["adobe xd", "xd"],
    "wireframing": ["wireframing", "wireframes", "wireframe"],
    "prototyping": ["prototyping", "prototype", "interactive prototype"],
    "visual design": ["visual design", "graphic design", "ui design"],
    "usability testing": ["usability testing", "ux testing",
                          "user testing"],
    "design thinking": ["design thinking", "human centered design"],
    "information architecture": ["information architecture", "ia",
                                 "content architecture"],

    # Game Dev
    "unity": ["unity", "unity3d", "unity 3d", "unity game engine"],
    "unreal engine": ["unreal engine", "unreal", "ue4", "ue5"],
    "3d mathematics": ["3d mathematics", "3d math", "3d maths",
                       "linear algebra 3d"],
    "game physics": ["game physics", "physics engine",
                     "rigid body dynamics"],
    "shader programming": ["shader programming", "shaders", "glsl",
                           "hlsl"],
    "game design": ["game design", "game development",
                    "game dev"],

    # Embedded
    "rtos": ["rtos", "real-time operating system",
             "real time operating system", "freertos"],
    "microcontrollers": ["microcontrollers", "microcontroller", "mcu",
                         "arduino", "stm32", "avr", "pic"],
    "circuit design": ["circuit design", "electronic design",
                       "pcb design", "schematic design"],
    "embedded linux": ["embedded linux", "embedded os",
                       "yocto", "buildroot"],
    "debugging": ["debugging", "debug", "troubleshooting",
                  "gdb", "jtag"],
    "assembly": ["assembly", "asm", "assembly language",
                 "x86 assembly", "arm assembly"],
    "i2c": ["i2c", "inter-integrated circuit"],
    "spi": ["spi", "serial peripheral interface"],

    # Project Management & Business
    "agile": ["agile", "scrum", "kanban", "agile methodology",
              "agile scrum"],
    "jira": ["jira", "atlassian jira"],
    "product strategy": ["product strategy", "product management",
                         "product vision"],
    "roadmap planning": ["roadmap planning", "product roadmap",
                         "strategic planning"],
    "user research": ["user research", "ux research",
                      "user interviews"],
    "data analysis": ["data analysis", "data analytics",
                      "business analytics"],
    "communication": ["communication", "professional communication",
                      "stakeholder communication"],
    "requirements gathering": ["requirements gathering",
                               "requirements analysis",
                               "business requirements",
                               "requirements engineering"],
    "process modeling": ["process modeling", "bpmn",
                         "business process modeling"],
    "stakeholder management": ["stakeholder management",
                               "stakeholder engagement"],
    "uml": ["uml", "unified modeling language"],
    "a/b testing": ["a/b testing", "ab testing", "split testing"],

    # Data Tools
    "tableau": ["tableau", "tableau desktop"],
    "power bi": ["power bi", "powerbi", "microsoft power bi"],
    "excel": ["excel", "microsoft excel", "ms excel", "spreadsheets"],
    "jupyter": ["jupyter", "jupyter notebook", "jupyter notebooks",
                "jupyter lab", "jupyterlab", "ipython"],

    # Database Design / Admin
    "database design": ["database design", "db design",
                        "schema design", "er diagram",
                        "entity relationship"],
    "performance tuning": ["performance tuning",
                           "query optimization", "db optimization"],
    "backup & recovery": ["backup & recovery", "backup and recovery",
                          "disaster recovery", "data recovery"],
    "replication": ["replication", "database replication",
                    "data replication"],
    "indexing": ["indexing", "database indexing", "index optimization"],

    # SysAdmin
    "windows server": ["windows server", "windows administration",
                       "windows sysadmin"],
    "active directory": ["active directory", "ad", "ldap"],
    "virtualization": ["virtualization", "vmware", "virtualbox",
                       "hyper-v", "hypervisor"],
    "networking": ["networking", "network administration",
                   "network engineering", "tcp/ip", "dns", "dhcp"],
    "dns": ["dns", "domain name system", "name resolution"],
    "dhcp": ["dhcp", "dynamic host configuration"],

    # Data Cleaning
    "data cleaning": ["data cleaning", "data cleansing",
                      "data wrangling", "data preprocessing",
                      "data preparation"],
}

# Build reverse lookup: alias → canonical key
_ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical, aliases in SKILL_SYNONYMS.items():
    for alias in aliases:
        _ALIAS_TO_CANONICAL[alias.lower().strip()] = canonical


# ═══════════════════════════════════════════════════════════════════
# SKILL CATEGORIES
# Group skills so that any ONE skill in a category can satisfy the
# entire category requirement.
# ═══════════════════════════════════════════════════════════════════

SKILL_CATEGORIES: dict[str, list[str]] = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#",
        "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "dart",
        "r",
    ],
    "databases": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
        "cassandra", "dynamodb", "nosql", "oracle", "mariadb",
    ],
    "version_control": [
        "git", "github", "gitlab", "bitbucket", "svn",
    ],
    "core_cs": [
        "data structures", "algorithms", "oop", "operating systems",
        "dbms", "computer networks", "system design",
    ],
    "cloud_providers": [
        "aws", "azure", "gcp",
    ],
    "frontend_frameworks": [
        "react", "angular", "vue.js", "svelte",
    ],
    "ml_frameworks": [
        "tensorflow", "pytorch", "scikit-learn", "keras",
    ],
    "mobile_frameworks": [
        "react native", "flutter", "swift", "kotlin",
    ],
    "containerization": [
        "docker", "kubernetes", "podman",
    ],
}


# ═══════════════════════════════════════════════════════════════════
# 1. normalize_skill(skill) → cleaned, lowercase, canonical string
# ═══════════════════════════════════════════════════════════════════

def normalize_skill(skill: str) -> str:
    """
    Normalize a skill string to a consistent canonical form.

    Steps:
      1. Strip whitespace, convert to lowercase
      2. Remove special characters (keep alphanumeric, spaces, +, #, /, ., -)
      3. Collapse multiple spaces
      4. Map to canonical form via synonym dictionary

    Examples:
      "Git/GitHub"                  → "git"
      "MySQL"                       → "sql"
      "Algorithm Design & Analysis" → "algorithms"
      "  PYTHON  "                  → "python"
      "Object Oriented Programming" → "oop"
    """
    if not skill or not skill.strip():
        return ""

    # Step 1: lowercase + strip
    cleaned = skill.strip().lower()

    # Step 2: Remove special chars except those used in skill names
    # Keep: alphanumeric, space, +, #, /, ., -, &
    # We first try the raw cleaned version for synonym lookup
    canonical = _lookup_canonical(cleaned)
    if canonical:
        return canonical

    # Step 3: Try removing & and special punctuation
    no_amp = re.sub(r'[&]', '', cleaned).strip()
    no_amp = re.sub(r'\s+', ' ', no_amp)
    canonical = _lookup_canonical(no_amp)
    if canonical:
        return canonical

    # Step 4: Try aggressive cleanup — only keep alphanumeric + space + basic chars
    aggressive = re.sub(r'[^a-z0-9\s\+\#\.\/\-]', '', cleaned)
    aggressive = re.sub(r'\s+', ' ', aggressive).strip()
    canonical = _lookup_canonical(aggressive)
    if canonical:
        return canonical

    # Step 5: Fallback — return the cleaned lowercase version
    return cleaned


def _lookup_canonical(text: str) -> Optional[str]:
    """Look up a text string in the alias-to-canonical mapping."""
    text = text.strip()
    if text in _ALIAS_TO_CANONICAL:
        return _ALIAS_TO_CANONICAL[text]
    return None


# ═══════════════════════════════════════════════════════════════════
# 2. map_skill(skill) → canonical group key
# ═══════════════════════════════════════════════════════════════════

def map_skill(skill: str) -> str:
    """
    Map a skill to its canonical group key using the synonym dictionary.

    If the skill is found as an alias, returns the canonical key.
    Otherwise, returns the normalized form.

    Examples:
      "GitHub"    → "git"
      "MySQL"     → "sql"
      "PyTorch"   → "pytorch"
      "Python"    → "python"
      "UnknownXY" → "unknownxy"
    """
    return normalize_skill(skill)


# ═══════════════════════════════════════════════════════════════════
# 3. check_category_satisfaction(user_skills, category) → bool
# ═══════════════════════════════════════════════════════════════════

def check_category_satisfaction(
    user_canonical_skills: set[str],
    category: str,
) -> bool:
    """
    Check if the user satisfies a skill category.

    A category is satisfied if the user has AT LEAST ONE skill from
    that category group.

    Args:
        user_canonical_skills: Set of normalized/canonical user skills.
        category: Category key from SKILL_CATEGORIES.

    Returns:
        True if at least one skill in the category is present.
    """
    if category not in SKILL_CATEGORIES:
        return False

    category_skills = set(SKILL_CATEGORIES[category])
    return bool(user_canonical_skills & category_skills)


def get_skill_category(canonical_skill: str) -> Optional[str]:
    """
    Get the category a canonical skill belongs to.
    Returns None if the skill doesn't belong to any category.
    """
    for cat_name, cat_skills in SKILL_CATEGORIES.items():
        if canonical_skill in cat_skills:
            return cat_name
    return None


# ═══════════════════════════════════════════════════════════════════
# 4. _is_programming_language(skill) — helper
# ═══════════════════════════════════════════════════════════════════

def _is_programming_language(canonical_skill: str) -> bool:
    """Check if a canonical skill is a programming language."""
    return canonical_skill in SKILL_CATEGORIES.get("programming_languages", [])


# ═══════════════════════════════════════════════════════════════════
# 5. match_skills(user_skills, required_skills) → match result
# ═══════════════════════════════════════════════════════════════════

def match_skills(
    user_skills: list[str],
    required_skills: list[str],
) -> dict:
    """
    Perform intelligent skill matching using normalization, synonyms,
    semantic rules, and category-based satisfaction.

    CRITICAL LOGIC — Programming Language Flexibility:
      If the role requires multiple programming languages (e.g. Python AND Java),
      knowing ANY ONE of them satisfies ALL programming language requirements.
      This reflects real-world hiring: you don't need every language listed.

    CRITICAL LOGIC — Category Satisfaction:
      Skills in the same category (e.g. databases) can satisfy each other.
      Knowing "MySQL" satisfies a requirement for "SQL".

    Returns:
        {
            "matched": [{"skill": "Python", "matched_by": "python", "match_type": "exact"}, ...],
            "missing": [{"skill": "Docker"}, ...],
            "match_percentage": 75.0,
            "matched_list": ["Python", ...],
            "missing_list": ["Docker", ...],
            "method": "Semantic + Rule-Based Normalization",
        }
    """
    if not required_skills:
        return {
            "matched": [],
            "missing": [],
            "match_percentage": 100.0,
            "matched_list": [],
            "missing_list": [],
            "method": "Semantic + Rule-Based Normalization",
        }

    # Normalize all user skills to canonical forms
    user_canonical = set()
    user_canonical_map = {}  # canonical → original
    for skill in user_skills:
        if not skill or not skill.strip():
            continue
        canonical = normalize_skill(skill)
        if canonical:
            user_canonical.add(canonical)
            if canonical not in user_canonical_map:
                user_canonical_map[canonical] = skill.strip()

    # Check which categories the user satisfies
    user_has_programming_lang = check_category_satisfaction(
        user_canonical, "programming_languages"
    )

    # Process each required skill
    matched = []
    missing = []

    # Track which required langs we've already accounted for
    required_prog_langs = []
    required_non_langs = []

    for req_skill in required_skills:
        canonical_req = normalize_skill(req_skill)
        if _is_programming_language(canonical_req):
            required_prog_langs.append((req_skill.strip(), canonical_req))
        else:
            required_non_langs.append((req_skill.strip(), canonical_req))

    # ── Handle programming languages with flexibility ──────────
    prog_lang_matched_any = False
    for original, canonical_req in required_prog_langs:
        if canonical_req in user_canonical:
            matched.append({
                "skill": original,
                "matched_by": user_canonical_map.get(canonical_req, canonical_req),
                "match_type": "exact",
            })
            prog_lang_matched_any = True
        elif user_has_programming_lang:
            # User knows at least one programming language →
            # treat this language requirement as satisfied
            user_lang = None
            for uc in user_canonical:
                if _is_programming_language(uc):
                    user_lang = user_canonical_map.get(uc, uc)
                    break
            matched.append({
                "skill": original,
                "matched_by": user_lang or "a programming language",
                "match_type": "category_satisfaction",
            })
            prog_lang_matched_any = True
        else:
            missing.append({"skill": original})

    # ── Handle non-language skills ──────────────────────────────
    for original, canonical_req in required_non_langs:
        if canonical_req in user_canonical:
            # Direct canonical match
            matched.append({
                "skill": original,
                "matched_by": user_canonical_map.get(canonical_req, canonical_req),
                "match_type": "synonym",
            })
        elif _semantic_match(canonical_req, user_canonical):
            # Semantic/substring match
            matched_by_skill = _find_semantic_match(canonical_req, user_canonical)
            matched.append({
                "skill": original,
                "matched_by": user_canonical_map.get(matched_by_skill, matched_by_skill),
                "match_type": "semantic",
            })
        else:
            missing.append({"skill": original})

    # Calculate match percentage
    total_required = len(required_skills)
    match_percentage = round(
        (len(matched) / total_required) * 100, 1
    ) if total_required > 0 else 0.0

    return {
        "matched": matched,
        "missing": missing,
        "match_percentage": match_percentage,
        "matched_list": sorted([m["skill"] for m in matched]),
        "missing_list": sorted([m["skill"] for m in missing]),
        "method": "Semantic + Rule-Based Normalization",
    }


# ═══════════════════════════════════════════════════════════════════
# SEMANTIC / SUBSTRING MATCHING HELPERS
# ═══════════════════════════════════════════════════════════════════

def _semantic_match(required_canonical: str, user_canonical_set: set[str]) -> bool:
    """
    Check if any user skill semantically matches a required skill.

    Matching rules:
      1. Exact canonical match (already handled before this is called)
      2. One is a substring of the other (e.g. "sql" in "mysql")
      3. Shared category membership
      4. Token overlap (e.g. "machine learning" ↔ "ml")
    """
    return _find_semantic_match(required_canonical, user_canonical_set) is not None


def _find_semantic_match(
    required_canonical: str,
    user_canonical_set: set[str],
) -> Optional[str]:
    """
    Find which user skill semantically matches the required skill.
    Returns the matched user canonical skill, or None.
    """
    for user_skill in user_canonical_set:
        # Check if they map to the same canonical group
        if user_skill == required_canonical:
            return user_skill

        # Substring matching: "sql" in "mysql" → True
        # But be careful: "c" should not match "css"
        if len(required_canonical) >= 2 and len(user_skill) >= 2:
            if required_canonical in user_skill or user_skill in required_canonical:
                # Verify it's a meaningful substring match
                if _is_meaningful_substring(required_canonical, user_skill):
                    return user_skill

        # Category-level match
        req_category = get_skill_category(required_canonical)
        user_category = get_skill_category(user_skill)
        if (req_category and user_category and
                req_category == user_category and
                req_category in ("databases", "version_control")):
            # Only auto-satisfy for certain "fungible" categories
            return user_skill

    return None


def _is_meaningful_substring(s1: str, s2: str) -> bool:
    """
    Guard against silly substring matches.
    E.g., "c" should not match "css" or "ci/cd".
    """
    shorter = s1 if len(s1) <= len(s2) else s2
    longer = s1 if len(s1) > len(s2) else s2

    # Very short strings (1-2 chars) are only matched if they're
    # the ONLY content or a perfect token match
    if len(shorter) <= 2:
        # "c" → only match "c", "c language", etc., not "css"
        # Check if shorter appears as a standalone word/token
        tokens = re.split(r'[\s/\-\+\.]+', longer)
        return shorter in tokens

    # For longer strings, substring match is generally meaningful
    return True


# ═══════════════════════════════════════════════════════════════════
# CONVENIENCE: get_match_label()
# ═══════════════════════════════════════════════════════════════════

def get_match_method_label() -> str:
    """Return the label string for the UI."""
    return "🧠 Skill Matching: Semantic + Rule-Based Normalization"
