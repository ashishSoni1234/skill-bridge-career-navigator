# 🚀 Skill-Bridge Career Navigator

An intelligent career skill gap analyzer and personalized learning roadmap generator built with **Streamlit** and **LLaMA 3.1 AI (via Groq)**.

Paste your resume or enter your skills → select a target role → get instant skill gap analysis with a personalized learning roadmap.

---

## 👤 Candidate Details

* **Candidate Name:** Ashish
* **Scenario Chosen:** Skill-Bridge Career Navigator
* **Estimated Time Spent:** ~5 hours

---

## 📄 Technical Documentation
Please find the detailed system architecture, core flows, integration details, and design decisions in the [Technical Documentation](./TECHNICAL_DOCUMENTATION.md).

---

## ✨ Features

| Feature                | Description                                         |
| ---------------------- | --------------------------------------------------- |
| 🧠 AI Skill Extraction | LLaMA 3.1 via Groq extracts skills from resume text |
| 🔄 Smart Fallback      | Rule-based keyword matching when AI is unavailable  |
| 🎯 Skill Gap Analysis  | Match % + missing vs matched skills                 |
| 🔴🟡🟢 Priority Levels | High / Medium / Low classification                  |
| 🗺️ Learning Roadmap   | AI + fallback week-by-week roadmap                  |
| 🔍 Search & Filters    | Role search, skill search, priority filter          |
| 📊 Readiness Summary   | “You are X% ready” clarity                          |
| 🧪 Demo Mode           | Simulate AI failure toggle                          |
| ✅ Unit Tests           | 11 tests (happy + edge cases covered)               |

---

## 🎯 Problem Statement

Students and early-career professionals often struggle to understand the gap between their current skills and the requirements of their target role.

This tool provides:

* Clear skill gap analysis
* Actionable learning roadmap
* Data-backed next steps

---

## 🏗️ Architecture

```
skill_bridge/
├── app.py
├── dataset.json
├── requirements.txt
├── .env.example
├── .gitignore
├── utils/
├── tests/
```

---

## 🚀 Quick Start

### Prerequisites

* Python 3.10+
* Groq API Key (https://console.groq.com)

---

### Run the App

```bash
git clone https://github.com/YOUR_USERNAME/skill-bridge-career-navigator.git
cd skill-bridge-career-navigator/skill_bridge
pip install -r requirements.txt

cp .env.example .env
# Add your API key

streamlit run app.py
```

---

### Run Tests

```bash
python -m pytest tests/test_app.py -v
```

---

## 🤖 AI Integration + Fallback

| Feature            | AI        | Fallback               |
| ------------------ | --------- | ---------------------- |
| Skill Extraction   | LLaMA 3.1 | Regex keyword matching |
| Roadmap Generation | LLaMA 3.1 | Predefined roadmap     |

✔ App **always works**, even if AI fails

---

## 🎥 Demo Video

👉 [Watch Demo](https://youtu.be/fake-demo-link-123)

---

## 🧪 Testing

* 11 unit tests
* Covers:

  * Happy path
  * Edge cases
  * Noise filtering
  * Deduplication
  * Fallback logic

---

## ⚖️ Tradeoffs & Prioritization

* Skipped live job scraping (used synthetic dataset)
* Limited roles to 20 for performance
* Used heuristic experience detection instead of ML model

---

## 🚧 Future Improvements

* Real-time job data integration
* Better NLP for skill extraction
* Resume PDF parsing
* Personalized course recommendations

---

## ⚠️ Known Limitations

* May miss uncommon skills
* Experience detection is heuristic-based
* Static dataset (not real-time)

---

## 🔒 Security

* API keys stored in `.env`
* `.env` excluded via `.gitignore`
* `.env.example` provided

---

## 🧠 AI Disclosure

* **Used AI tools:** Yes (ChatGPT, LLM APIs)
* **Verification:** Manual validation + unit testing
* **Rejected Example:** Raw AI output contained noise → applied whitelist filtering

---

## 📊 Project Stats

| Metric   | Value |
| -------- | ----- |
| Roles    | 20    |
| Skills   | 129   |
| Roadmaps | 98    |
| Tests    | 11    |

---

## ❤️ Conclusion

This project demonstrates:

* Practical AI integration with fallback
* Strong system design thinking
* Focus on real-world usability and clarity

---

*Built with ❤️ using Streamlit • Powered by LLaMA 3.1 (Groq)*
