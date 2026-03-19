# Skill-Bridge Career Navigator: Technical Documentation

## 1. Problem Understanding
The skills gap is a persistent challenge for job seekers, especially students and early-career professionals. Candidates often struggle to identify exactly which skills they lack for a specific target role. Resumes might highlight experiences, but extracting actionable insights to bridge the gap between current proficiencies and industry requirements is tedious. Without clear identification of missing core competencies, candidates fail to optimize their learning paths, wasting time on less impactful skills.

## 2. Solution Overview
Skill-Bridge Career Navigator solves this problem by providing an intelligent skill gap analysis and personalized learning roadmap. Users input their resume or a comma-separated list of skills and choose a target job role. The system leverages AI (LLaMA 3.1) to intelligently extract and normalize their skills, compares them against a predefined dataset of role requirements, and identifies gaps. Finally, it generates a prioritized, week-by-week learning roadmap tailored to the user's detected experience level, guiding them on exactly what they need to learn next.

## 3. System Architecture
The application is built using a monolithic Streamlit architecture, integrating an external LLM API and relying on local JSON data. The flow is as follows:
- **Frontend**: A Streamlit interface that captures user inputs (resume text, target role, filter choices) and displays the analysis (match percentage, prioritized missing skills, and learning roadmaps).
- **Backend Logic (Utility Modules)**: Python functions handle skill extraction, semantic matching, and gap analysis.
- **AI/LLM Interaction**: The system makes asynchronous calls to the Groq API (LLaMA 3.1 8B) for parsing unstructured resume text into a standardized JSON list of skills and generating learning roadmaps. 
- **Data Layer**: A local `dataset.json` file serves as the source of truth for job roles and required skills.

## 4. Core Flow
1. **Input**: User pastes their resume text or a list of skills into the text area and selects a target role from the dropdown menu.
2. **Processing (Skill Extraction)**: The system sends the text to the Groq API (LLaMA 3.1) to extract technical skills as a JSON array. It then applies a post-processing whitelist filter to remove noise (names, emails, irrelevant sentences) and normalizes the strings.
3. **Processing (Gap Analysis)**: The `gap_analyzer` compares detected skills against required skills for the target role. It intelligently handles synonyms and category-based skill matching (e.g., MySQL satisfies an SQL requirement). Missing skills are categorized into High, Medium, and Low priorities.
4. **Output (Readiness & Gap)**: The app presents a Readiness Summary (e.g., Match Percentage 75%) along with visual tags for matched and missing skills.
5. **Output (Roadmap)**: For missing skills, the `roadmap_generator` evaluates the user's experience tier and creates a customized, week-by-week learning plan using AI or predefined fallback rules.

## 5. AI Integration and Fallback
**AI Usage**: 
- **Skill Extraction**: LLaMA 3.1 (via Groq) serves as the primary engine to intelligently extract only professional and technical skills from unstructured text.
- **Roadmap Generation**: AI is utilized to produce tailored, actionable learning steps for missing skills based on the user's experience level (Beginner, Intermediate, Advanced).

**Fallback Mechanism**:
If the AI fails (e.g., API rate limits, network issues, or invalid keys) after 3 retries, the system seamlessly degrades to a reliable rule-based fallback mechanism.
- **Extraction Fallback**: Applies regex word-boundary keyword matching against the known skills list.
- **Roadmap Fallback**: Triggers a robust set of predefined, skill-specific learning steps (`SKILL_ROADMAPS` dictionary) to ensure the user still receives actionable guidance.

## 6. Data Design
The system uses a synthetic dataset (`dataset.json`) containing 20 distinct job roles (e.g., Software Engineer, Data Scientist) mapped to their required core competencies (e.g., Python, SQL, Docker).

**Why Synthetic Data?**
Due to time constraints and the complexity of integrating with live job board APIs, a curated synthetic dataset guarantees reliable, clean, and normalized data for matching. It ensures predictable behavior during testing and validation without the latency or unpredictability of external services.

## 7. Tech Stack
- **Python 3.10**: Core programming language, chosen for its robust data manipulation capabilities.
- **Streamlit**: Selected for the frontend to allow rapid prototyping of interactive, data-rich web applications without writing boilerplate HTML/CSS/JS.
- **Groq API & LLaMA 3.1**: Chosen for ultra-fast, low-latency LLM inference.
- **Pytest**: Used for comprehensive unit testing to ensure system reliability.

## 8. Trade-offs and Design Decisions
- **Rule-based NLP vs Custom ML Models**: Instead of training a custom Named Entity Recognition (NER) model for skill extraction, we used an LLM prompt combined with a strict post-processing whitelist. This accelerated development while maintaining high output accuracy.
- **Heuristic Experience Detection**: Experience level is detected using simple keyword heuristics (e.g., "Senior," "led team," "5+ years") rather than a sophisticated NLP classification model, as predicting seniority from unstandardized text is highly subjective and complex.
- **Local JSON Storage**: Adopted `dataset.json` over a relational database (like PostgreSQL) to keep the project lightweight and easily runnable without external infrastructure dependencies.

## 9. Testing
The application employs `pytest` for robust unit testing across all key utility functions (with over 20+ tests implemented).

**Test Case 1: Normal (Happy Path)**
- **Scenario**: User provides valid skills ("Python", "SQL", "Git"), and the target role is "Software Engineer" requiring ("Python", "SQL", "Git", "Docker", "REST APIs", "System Design").
- **Expected Outcome**: The system correctly identifies 3 matched skills and 3 missing skills ("Docker", "REST APIs", "System Design"), yielding a 50% match percentage. The generated roadmap only covers the 3 missing skills.

**Test Case 2: Edge Case**
- **Scenario**: User provides an empty string as input.
- **Expected Outcome**: The fallback logic safely handles the empty text, returning 0 matched skills, categorizing all required skills as missing, and reliably logging a 0.0% match percentage without throwing an application error.

## 10. Limitations
- **Skill Vocabulary**: The system's understanding of skills is restricted to its predefined whitelist and dataset. Extremely niche or novel technologies might be ignored or misclassified.
- **Static Dataset**: Job role requirements are hardcoded and will not dynamically reflect real-time shifts in industry demand.
- **Heuristic Constraints**: The regex-based fallback might misinterpret complex phrasing (e.g., "I want to learn Docker" might be falsely detected as possessing the Docker skill in fallback mode).

## 11. Future Improvements
If more time were available, realistic next steps would include:
- **Live Job Scraping**: Integrate with APIs from LinkedIn or Glassdoor to continuously and dynamically update role requirements.
- **PDF Resume Parsing**: Allow users to upload `.pdf` or `.docx` files directly using libraries like `PyMuPDF` to extract text before passing it to the AI.
- **Advanced Semantic Matching**: Implement a local vector embedding model (using `sentence-transformers`) for more robust semantic matching of terminologies (e.g., matching "GCP" with "Google Cloud Platform" via vector cosine similarity rather than hardcoded synonyms).
