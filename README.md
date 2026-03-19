# 🚀 Skill-Bridge Career Navigator

An intelligent career skill gap analyzer and personalized learning roadmap generator built with **Streamlit** and **LLaMA 3.1 AI** (via Groq).

Paste your resume or enter your skills → select a target role → get instant skill gap analysis with a personalized learning roadmap.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **AI Skill Extraction** | LLaMA 3.1 (8B) via Groq API extracts skills from resume text |
| 🔄 **Smart Fallback** | Rule-based keyword matching when AI is unavailable |
| 🎯 **Skill Gap Analysis** | Compares your skills vs. role requirements with match % |
| 🔴🟡🟢 **Priority Levels** | Missing skills classified as High / Medium / Low priority |
| 🗺️ **AI Learning Roadmap** | LLaMA 3.1 generates personalized week-by-week learning steps |
| 📌 **98 Custom Roadmaps** | Pre-built skill-specific learning plans as fallback |
| 🔍 **Search & Filters** | Role search, skill search, priority filter, match filter |
| 📊 **Readiness Summary** | Human-readable readiness score with next-step guidance |
| 🧪 **Demo Mode** | Toggle AI failure simulation to test fallback behavior |
| ✅ **11 Unit Tests** | Comprehensive test coverage for all core modules |

---

## 🏗️ Architecture

```
skill_bridge/
├── app.py                          # Streamlit UI (entry point)
├── dataset.json                    # 20 job roles × 9-12 skills
├── requirements.txt                # 4 dependencies
├── .env.example                    # API key template
├── .gitignore                      # Security exclusions
├── README.md                       # Documentation
├── utils/
│   ├── __init__.py                 # Package init
│   ├── skill_extractor.py          # AI + fallback skill extraction
│   ├── gap_analyzer.py             # Gap analysis + priority + readiness
│   └── roadmap_generator.py        # AI + fallback roadmap generation
└── tests/
    └── test_app.py                 # 11 unit tests
```

---

## 📦 Module Documentation

### 📄 `app.py` — Main Streamlit Application

The single entry point. Manages UI layout, user input, and orchestrates all modules.

| Section | What It Does |
|---|---|
| **Sidebar: Explore Roles** | Search & browse required skills for any role |
| **Sidebar: Filters** | Priority filter (🔴🟡🟢), Match filter (All/Matched/Missing) |
| **Sidebar: Settings** | AI failure simulation toggle with live status indicator |
| **Input Section** | Text area for skills/resume + role dropdown (20 roles) |
| **Required Skills Display** | Shows target role's required skills before analysis |
| **Skill Extraction** | Calls `extract_skills()` → AI + fallback + post-processing |
| **Gap Analysis** | Calls `analyze_gap()` → match %, matched/missing lists |
| **Skill Search** | Filter detected skills by keyword in real-time |
| **Detected Skills** | Shows skills with "Show More" expander (top 10 visible) |
| **Missing Skills** | Grouped by priority (High → Medium → Low) with filter support |
| **Skill Match** | Progress bar + percentage metric |
| **Readiness Summary** | Human-readable readiness message with experience level |
| **Next Step Guidance** | Prioritized learning path recommendation |
| **Personalized Roadmap** | AI-generated or pre-defined week-by-week learning plan |

**Key Function:**

| Function | Description |
|---|---|
| `load_dataset()` | Loads `dataset.json` with `@st.cache_data` for performance |

---

### 📄 `utils/skill_extractor.py` — Skill Extraction Module

Extracts skills from user text using AI with rule-based fallback. Includes a 352-skill whitelist for noise filtering.

**Data:**

| Constant | Description |
|---|---|
| `SKILL_WHITELIST` | Set of 352 lowercase skill names across 15+ categories (programming, ML, DevOps, cloud, design, etc.) |

**Functions:**

| Function | Type | Description |
|---|---|---|
| `extract_skills(text, all_skills, simulate_failure)` | **Main** | Orchestrator — tries AI first, falls back to rule-based. Applies post-processing. Returns `(clean_skills, method, error_message)` |
| `extract_skills_ai(text)` | Primary | Sends text to LLaMA 3.1 via Groq. Prompt instructs model to return ONLY skill names as JSON. Raises exception on failure |
| `extract_skills_fallback(text, all_skills)` | Fallback | Scans input for known skills using word-boundary regex (`\b`) matching |
| `_filter_and_deduplicate(raw_skills, all_known_skills)` | Post-processing | 5-step pipeline: clean → validate → whitelist check → normalize → deduplicate |
| `_clean_skill_text(text)` | Helper | Strips whitespace, removes trailing punctuation, strips numbering prefixes |
| `_is_valid_skill(text)` | Helper | Rejects emails, URLs, sentences (>50 chars), 4+ word phrases, pure numbers |
| `_normalize_skill(skill)` | Helper | Maps common variations to canonical form (e.g., `"js"` → `"JavaScript"`, `"ml"` → `"Machine Learning"`) |

**AI + Fallback Pattern:**

```python
try:
    raw_skills = extract_skills_ai(text)     # LLaMA 3.1 via Groq
    method = "AI"
except Exception:
    raw_skills = extract_skills_fallback(text, all_skills)  # Keyword matching
    method = "Fallback"

clean_skills = _filter_and_deduplicate(raw_skills, all_skills)  # Always applied
```

---

### 📄 `utils/gap_analyzer.py` — Gap Analysis Module

Compares user skills against role requirements. Classifies skills by priority and detects experience level.

**Data:**

| Constant | Description |
|---|---|
| `HIGH_PRIORITY_SKILLS` | Set of core/foundational skills (DSA, Algorithms, OOP, System Design, Python, etc.) |
| `MEDIUM_PRIORITY_SKILLS` | Set of important but not foundational skills (Git, REST APIs, CI/CD, Docker, etc.) |

**Functions:**

| Function | Returns | Description |
|---|---|---|
| `analyze_gap(user_skills, required_skills)` | `dict` | Core analysis — case-insensitive matching, returns `{matched, missing, match_percentage, matched_list, missing_list}`. Each skill entry includes `{skill, priority}` |
| `get_skill_priority(skill)` | `str` | Classifies a single skill: `"high"` / `"medium"` / `"low"` |
| `detect_experience_level(text)` | `str` | Keyword-based detection: `"beginner"` (student, fresher) / `"intermediate"` (2+ years) / `"advanced"` (senior, led team, 5+ years) |
| `get_readiness_summary(match_pct, missing_count, role)` | `str` | Human-readable summary (e.g., "You are 50% ready for Software Engineer...") |
| `get_prioritized_skills(missing_skills)` | `list` | Sorts missing skills: High priority first → Medium → Low |
| `get_next_step_guidance(prioritized_skills)` | `str` | Generates recommended learning path text with top 3 skills to focus on |

**Match Calculation:**

```python
match_percentage = (len(matched_skills) / len(required_skills)) * 100
```

---

### 📄 `utils/roadmap_generator.py` — Roadmap Generation Module

Generates personalized week-by-week learning plans using AI with pre-defined fallback.

**Data:**

| Constant | Description |
|---|---|
| `SKILL_ROADMAPS` | Dictionary with 98 skill-specific learning plans (3 concrete steps per skill) |
| `LEVEL_TIPS` | Experience-level tips appended to fallback roadmap steps |

**Functions:**

| Function | Type | Description |
|---|---|---|
| `generate_roadmap(missing_skills, experience_level, target_role, simulate_failure)` | **Main** | Orchestrator — tries AI first, falls back to rule-based. Returns `(roadmap, method, error_message)` |
| `generate_roadmap_ai(missing_skills, target_role, experience_level)` | Primary | Sends skills + role + level to LLaMA 3.1 via Groq. Prompt requests JSON array with week/skill/steps format. Raises exception on failure |
| `generate_roadmap_fallback(missing_skills, experience_level)` | Fallback | Uses `SKILL_ROADMAPS` dict for custom steps. Falls back to generic 3-step plan for unlisted skills. Appends experience-level tip |

**AI Roadmap Prompt Strategy:**

- One week per missing skill
- 3 actionable steps per week (mentions real resources: LeetCode, official docs, projects)
- Difficulty tailored to experience level
- Returns valid JSON array

---

### 📄 `dataset.json` — Role & Skills Dataset

Contains 20 job roles, each with 9-12 required skills.

| # | Role | Sample Skills |
|---|---|---|
| 1 | Software Engineer | Python, DSA, OS, DBMS, Git, REST APIs, System Design, OOP, SQL |
| 2 | Data Scientist | Python, Machine Learning, Statistics, SQL, Pandas, Data Visualization |
| 3 | Frontend Developer | HTML, CSS, JavaScript, React, Responsive Design, Git, TypeScript |
| 4 | Backend Developer | Python, SQL, REST APIs, Docker, Git, System Design, Authentication |
| 5 | DevOps Engineer | Docker, Kubernetes, CI/CD, Linux, AWS, Terraform, Monitoring |
| 6 | ML Engineer | Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, MLOps |
| 7 | Full Stack Developer | HTML, CSS, JavaScript, React, Node.js, SQL, REST APIs, Git, Docker |
| 8 | Cloud Architect | AWS, Azure, GCP, Docker, Kubernetes, Terraform, System Design |
| 9 | Cybersecurity Analyst | Networking, Linux, Security, Penetration Testing, Firewalls, SIEM |
| 10 | Mobile App Developer | Flutter, React Native, Swift, Kotlin, REST APIs, Git, Firebase |
| 11-20 | *+ 10 more roles* | Data Analyst, Product Manager, QA Engineer, UI/UX Designer, etc. |

---

### 📄 `tests/test_app.py` — Test Suite

11 unit tests covering all core modules. Run with `python -m pytest tests/test_app.py -v`.

| # | Test | What It Validates |
|---|---|---|
| 1 | `test_happy_path` | End-to-end: skills → gap analysis → roadmap for matching/missing skills |
| 2 | `test_empty_input` | Edge case: empty skills list returns 0% match, no crashes |
| 3 | `test_noise_filtering` | Removes names, emails, universities, sentences from AI output |
| 4 | `test_deduplication` | Case-insensitive dedup: "Python", "python", "PYTHON" → 1 entry |
| 5 | `test_priority_classification` | DSA/Python = High, Git/REST = Medium, unknown = Low |
| 6 | `test_experience_level` | "student" → beginner, "senior, led team" → advanced |
| 7 | `test_personalized_roadmap` | Roadmap only contains missing skills, not known ones |
| 8 | `test_readiness_summary` | Summary includes match % and role name |
| 9 | `test_skill_validation` | Rejects emails, URLs, long sentences, pure numbers |
| 10 | `test_roadmap_ai_fallback` | simulate_failure=True → returns "Fallback" method |
| 11 | `test_filtering` | Priority filter and search filter work correctly on results |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Groq API Key (free at [console.groq.com](https://console.groq.com))

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/skill-bridge-career-navigator.git
cd skill-bridge-career-navigator/skill_bridge

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
cp .env.example .env
# Edit .env and add your Groq API key

# 4. Run the app
streamlit run app.py

# 5. Run tests
python -m pytest tests/test_app.py -v
```

### Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥1.30.0 | Web application framework |
| `groq` | ≥0.4.0 | LLaMA 3.1 API client |
| `python-dotenv` | ≥1.0.0 | Environment variable management |
| `pytest` | ≥7.4.0 | Testing framework |

---

## 🧠 AI Integration

The app uses **LLaMA 3.1 (8B)** via Groq API in **two places**, both with automatic fallback:

| Feature | AI Method | Fallback Method | When Fallback Triggers |
|---|---|---|---|
| **Skill Extraction** | LLaMA 3.1 prompt → JSON skills list | Regex keyword matching against whitelist | API error, rate limit, invalid key, network failure |
| **Roadmap Generation** | LLaMA 3.1 prompt → week-by-week JSON | Pre-defined `SKILL_ROADMAPS` dict (98 skills) | Same as above |

**Fallback guarantee:** The app **always works** — even without internet or API key — using rule-based methods.

---

## 📊 Project Stats

| Metric | Value |
|---|---|
| Job roles | 20 |
| Unique required skills | 129 |
| Skill whitelist entries | 352 |
| Custom roadmap plans | 98 skills |
| Unit tests | 11 (all passing) |
| AI model | LLaMA 3.1 (8B) via Groq |
| Source files | 7 |

---

## 📸 App Sections Overview

1. **Input** → Enter skills or paste resume + select target role
2. **Required Skills** → Shows what the role needs before analysis
3. **Skill Extraction** → AI extracts skills, shows method used
4. **Skill Search** → Filter detected skills by keyword
5. **Detected vs Missing** → Side-by-side with priority badges
6. **Skill Match** → Progress bar with percentage
7. **Readiness Summary** → Human-readable score + experience level
8. **Next Step Guidance** → Top 3 skills to learn first
9. **Learning Roadmap** → AI-generated or pre-defined weekly plan

---

## 🔒 Security

- API keys stored in `.env` (excluded from git via `.gitignore`)
- `.env.example` provided with placeholder values
- No hardcoded secrets in source code

---

## 📝 License

This project is for educational and demonstration purposes.

---

*Built with ❤️ using Streamlit • AI powered by LLaMA 3.1 (Groq)*
