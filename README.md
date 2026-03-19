# Skill-Bridge Career Navigator

## Candidate Details

* **Candidate Name:** Ashish 
* **Scenario Chosen:** Skill-Bridge Career Navigator
* **Estimated Time Spent:** ~5 hours

---

## Project Overview

This project is an intelligent career navigation platform that identifies the gap between a user's current skills and the requirements of a target job role.

Users can input their resume or manually provide skills, select a target role, and receive:

* A detailed skill gap analysis
* A personalized learning roadmap
* A readiness score

The system leverages AI (LLaMA 3.1 via Groq) along with a deterministic fallback mechanism to ensure reliable and consistent results.

---

## Features

* **AI Skill Extraction:** Extracts skills from unstructured resume text using LLaMA 3.1
* **AI Fallback System:** Rule-based keyword matching ensures system reliability when AI fails
* **Skill Gap Analysis:** Compares user skills with role requirements
* **Readiness Score:** Displays how prepared the user is for the selected role
* **Priority Classification:** Missing skills categorized into High / Medium / Low
* **Personalized Roadmap:** Week-by-week plan to bridge skill gaps
* **Search & Filters:** Role and skill filtering capabilities
* **Demo Mode:** Simulates AI failure to test fallback system
* **Unit Testing:** Covers both AI and fallback workflows

---

## Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **AI Integration:** LLaMA 3.1 via Groq API
* **Testing:** Pytest
* **Data Storage:** JSON (Synthetic dataset)

---

## System Flow

1. **Input:** User provides resume text or manually enters skills and selects a target role
2. **Skill Extraction:** AI extracts skills; fallback uses regex/keyword matching if AI fails
3. **Gap Analysis:** Extracted skills are compared against predefined role requirements
4. **Output:** Missing skills, matched skills, and readiness score are displayed
5. **Roadmap Generation:** Personalized learning plan is generated
6. **Update Flow:** User can modify skills or role and regenerate results dynamically

---

## Demo Video

👉 [Watch Demo](https://youtu.be/your-final-video-link)

---

## Dataset

A synthetic dataset (`dataset.json`) is used, containing mappings of job roles to required skills.

* No real user data is used
* Ensures safe, controlled, and reproducible testing
* Avoids dependency on external APIs or scraping

---

## Quick Start

### Prerequisites

* Python 3.10+
* Groq API Key

### Run Commands

```bash
git clone https://github.com/ashishSoni1234/skill-bridge-career-navigator.git
cd skill-bridge-career-navigator/skill_bridge

pip install -r requirements.txt

cp .env.example .env
# Add your GROQ_API_KEY inside .env

streamlit run app.py
```

### Test Commands

```bash
python -m pytest tests/test_app.py -v
```

---

## Testing

* **Happy Path:**
  Valid resume input → correct skill extraction → accurate gap analysis → roadmap generated

* **Edge Case:**
  Empty or invalid input → fallback triggered → appropriate error handling and messaging

---

## Security

* API keys are stored securely using `.env`
* `.env.example` provided
* No secrets are committed to the repository

---

## AI Disclosure

* **Used AI tools:** Yes (ChatGPT, LLaMA 3.1 via Groq)

* **Verification:**

  * Manual validation of outputs
  * Whitelist filtering of extracted skills
  * Cross-checking with rule-based fallback
  * Unit testing

* **Rejected Example:**
  Raw AI outputs sometimes included noise such as sentences or emails.
  These were rejected and replaced with strict post-processing and normalization logic.

---

## Tradeoffs & Prioritization

* **Simplified Architecture:**
  Used Streamlit (monolithic app) instead of full frontend + backend split to save time

* **Synthetic Dataset over Live Data:**
  Avoided scraping job boards to ensure reproducibility and avoid API issues

* **Heuristic Matching over Deep NLP Models:**
  Chose rule-based + AI hybrid instead of training custom models due to time constraints

---

## Future Improvements

* Integration with real-time job APIs
* Use of embeddings for semantic skill matching
* User profile saving and progress tracking
* Advanced UI using React
* Improved recommendation system

---

## Known Limitations

* Synthetic dataset may not fully reflect real-world job variability
* AI output quality depends on prompt consistency
* Basic UI (focus was functionality, not design)

---

## Documentation

Detailed design, architecture, and implementation decisions are available here:
👉 [Technical Documentation](./TECHNICAL_DOCUMENTATION.md)
