"""
Roadmap Generator Module
========================
Generates a personalized, week-by-week learning roadmap
for each missing skill identified by the gap analyzer.

Key Decision:
  Each skill has CUSTOM, skill-specific learning steps rather than
  generic placeholders. This makes the roadmap actionable and realistic.
"""


# Skill-specific learning roadmaps.
# Each skill maps to a list of concrete, actionable steps.
SKILL_ROADMAPS = {
    # Programming Languages
    "python": [
        "Learn Python basics — variables, loops, functions, and data types",
        "Practice with 15+ coding exercises on HackerRank or LeetCode",
        "Build a small CLI project (e.g., to-do app or file organizer)",
    ],
    "java": [
        "Learn Java fundamentals — OOP, classes, interfaces, and generics",
        "Practice with 15+ coding problems focusing on collections framework",
        "Build a small REST API project using Spring Boot",
    ],
    "c": [
        "Learn C fundamentals — pointers, memory management, structs",
        "Practice with 10+ exercises on arrays, strings, and file I/O",
        "Build a small project like a calculator or linked list implementation",
    ],
    "c++": [
        "Learn C++ basics — classes, templates, STL containers",
        "Practice with competitive programming problems (Codeforces/LeetCode)",
        "Build a small project using OOP principles and smart pointers",
    ],
    "c#": [
        "Learn C# fundamentals — classes, LINQ, async/await",
        "Practice with 10+ exercises on collections and exception handling",
        "Build a small console app or Unity script",
    ],
    "javascript": [
        "Learn JS fundamentals — closures, promises, async/await, DOM",
        "Build 3 small interactive projects (calculator, quiz app, weather app)",
        "Study ES6+ features and practice with array/object methods",
    ],
    "typescript": [
        "Learn TypeScript basics — types, interfaces, generics, enums",
        "Convert a small JavaScript project to TypeScript",
        "Build a typed React component or Node.js module",
    ],

    # CS Fundamentals
    "data structures": [
        "Study arrays, linked lists, stacks, queues, and hash maps",
        "Implement each data structure from scratch in your language",
        "Solve 20+ LeetCode problems tagged 'data structures'",
    ],
    "algorithms": [
        "Learn sorting algorithms (merge sort, quicksort) and searching (binary search)",
        "Study recursion, dynamic programming, and greedy algorithms",
        "Solve 20+ LeetCode problems (Easy → Medium difficulty)",
    ],
    "mathematics": [
        "Review linear algebra — vectors, matrices, eigenvalues",
        "Study calculus essentials — derivatives, gradients, chain rule",
        "Practice probability & statistics concepts with real datasets",
    ],
    "statistics": [
        "Learn descriptive statistics — mean, median, standard deviation",
        "Study probability distributions, hypothesis testing, and p-values",
        "Apply statistical analysis to a sample dataset using Python",
    ],
    "system design": [
        "Study fundamental concepts — load balancing, caching, database sharding",
        "Learn common patterns — microservices, message queues, CDNs",
        "Practice by designing systems like URL shortener, chat app, or news feed",
    ],

    # Web
    "html": [
        "Learn HTML5 semantic elements — header, nav, section, article, footer",
        "Build 3 complete web pages with proper structure and forms",
        "Study accessibility best practices and SEO-friendly markup",
    ],
    "css": [
        "Learn CSS layout — Flexbox and CSS Grid",
        "Build responsive designs using media queries",
        "Practice animations, transitions, and modern design patterns",
    ],
    "react": [
        "Learn React fundamentals — components, props, state, hooks",
        "Build a complete project (e.g., task manager or e-commerce page)",
        "Study React Router, Context API, and component lifecycle",
    ],
    "responsive design": [
        "Learn mobile-first design principles and breakpoints",
        "Practice with CSS media queries and flexible layouts",
        "Build a fully responsive portfolio page from scratch",
    ],
    "webpack": [
        "Understand bundling concepts — entry, output, loaders, plugins",
        "Set up Webpack from scratch for a small JavaScript project",
        "Learn code splitting and optimization techniques",
    ],

    # Databases
    "sql": [
        "Learn SQL fundamentals — SELECT, JOIN, GROUP BY, subqueries",
        "Practice 20+ SQL problems on LeetCode or HackerRank",
        "Design and query a sample database (e.g., e-commerce schema)",
    ],
    "postgresql": [
        "Learn PostgreSQL-specific features — CTEs, window functions, JSONB",
        "Set up a local PostgreSQL instance and practice complex queries",
        "Study indexing strategies and query optimization with EXPLAIN",
    ],
    "mysql": [
        "Learn MySQL fundamentals and practice common queries",
        "Study stored procedures, triggers, and views",
        "Set up replication and understand backup strategies",
    ],
    "database design": [
        "Study normalization (1NF through 3NF) and denormalization trade-offs",
        "Design ER diagrams for 3 different business scenarios",
        "Learn indexing strategies and query performance optimization",
    ],

    # Backend
    "rest apis": [
        "Learn REST principles — HTTP methods, status codes, URL design",
        "Build a CRUD API using Flask or FastAPI with proper error handling",
        "Study authentication (JWT, OAuth) and API versioning",
    ],
    "node.js": [
        "Learn Node.js fundamentals — event loop, modules, npm",
        "Build a REST API with Express.js including middleware",
        "Study async patterns — callbacks, promises, and async/await",
    ],
    "authentication": [
        "Learn authentication vs. authorization concepts",
        "Implement JWT-based auth in a small project",
        "Study OAuth 2.0 flow and session management best practices",
    ],

    # Data & ML
    "pandas": [
        "Learn DataFrame operations — filtering, grouping, merging",
        "Clean and analyze a real-world dataset (CSV/Excel)",
        "Practice 10 data manipulation exercises on Kaggle",
    ],
    "numpy": [
        "Learn array operations, broadcasting, and vectorization",
        "Practice matrix operations and statistical computations",
        "Optimize a slow Python loop by converting it to NumPy",
    ],
    "data visualization": [
        "Learn Matplotlib and Seaborn for static visualizations",
        "Create 5 different chart types (bar, line, scatter, heatmap, box)",
        "Build an interactive dashboard using Plotly or Streamlit",
    ],
    "tableau": [
        "Learn Tableau basics — connecting data, building views, filters",
        "Create 3 interactive dashboards with different chart types",
        "Study calculated fields, parameters, and dashboard actions",
    ],
    "power bi": [
        "Learn Power BI Desktop — data import, modeling, DAX basics",
        "Build a complete dashboard with slicers and drill-through",
        "Study DAX measures and publish reports to Power BI Service",
    ],
    "excel": [
        "Master VLOOKUP, INDEX/MATCH, pivot tables, and conditional formatting",
        "Learn data analysis with Power Query and Power Pivot",
        "Build an automated reporting template with macros",
    ],
    "machine learning": [
        "Learn supervised learning — linear regression, decision trees, SVM",
        "Build an end-to-end ML project: data → model → evaluation",
        "Study cross-validation, feature engineering, and hyperparameter tuning",
    ],
    "deep learning": [
        "Learn neural network basics — perceptrons, backpropagation, activation functions",
        "Build a CNN for image classification using TensorFlow or PyTorch",
        "Study architectures — RNN, LSTM, Transformer basics",
    ],
    "tensorflow": [
        "Complete TensorFlow's official beginner tutorials",
        "Build and train a model using tf.keras Sequential API",
        "Learn TensorFlow Serving for model deployment",
    ],
    "pytorch": [
        "Learn PyTorch fundamentals — tensors, autograd, nn.Module",
        "Build and train a neural network from scratch",
        "Study data loading, transforms, and model saving/loading",
    ],
    "nlp": [
        "Learn text preprocessing — tokenization, stemming, TF-IDF",
        "Build a text classification model using scikit-learn or HuggingFace",
        "Study word embeddings (Word2Vec, BERT) and sequence models",
    ],
    "computer vision": [
        "Learn image processing basics with OpenCV",
        "Build an image classifier using a pretrained CNN (ResNet/VGG)",
        "Study object detection concepts — YOLO, SSD architectures",
    ],
    "mlops": [
        "Learn ML pipeline concepts — data versioning, experiment tracking",
        "Set up MLflow or Weights & Biases for experiment tracking",
        "Study model deployment with Docker and CI/CD for ML",
    ],

    # DevOps & Cloud
    "git": [
        "Learn Git basics — init, add, commit, branch, merge, rebase",
        "Practice branching strategies (Git Flow) and resolving merge conflicts",
        "Set up a collaborative workflow with pull requests on GitHub",
    ],
    "docker": [
        "Learn Docker basics — images, containers, Dockerfile, volumes",
        "Containerize an existing application with a multi-stage Dockerfile",
        "Practice Docker Compose for multi-container applications",
    ],
    "kubernetes": [
        "Learn K8s core concepts — pods, services, deployments, namespaces",
        "Deploy an application on Minikube or Kind locally",
        "Study scaling, rolling updates, and ConfigMaps/Secrets",
    ],
    "ci/cd": [
        "Learn CI/CD principles and pipeline stages",
        "Set up a GitHub Actions or GitLab CI pipeline for a sample project",
        "Implement automated testing, linting, and deployment steps",
    ],
    "linux": [
        "Learn essential commands — file management, permissions, processes",
        "Practice shell scripting — write 5 automation scripts",
        "Study system administration — services, cron jobs, log analysis",
    ],
    "aws": [
        "Learn core AWS services — EC2, S3, RDS, Lambda, IAM",
        "Deploy a simple web app on AWS using EC2 or Elastic Beanstalk",
        "Study VPC networking, security groups, and CloudWatch monitoring",
    ],
    "azure": [
        "Learn Azure fundamentals — VMs, App Service, Azure SQL, Blob Storage",
        "Deploy an application using Azure App Service",
        "Study Azure Active Directory and Role-Based Access Control",
    ],
    "gcp": [
        "Learn GCP core — Compute Engine, Cloud Storage, BigQuery, Cloud Functions",
        "Deploy an application on Google App Engine or Cloud Run",
        "Study IAM, VPC networks, and Cloud Monitoring",
    ],
    "terraform": [
        "Learn Terraform basics — providers, resources, variables, state",
        "Write Terraform configs to provision cloud infrastructure (VMs, networks)",
        "Study modules, workspaces, and remote state management",
    ],
    "monitoring": [
        "Learn monitoring concepts — metrics, logs, traces, alerting",
        "Set up Prometheus + Grafana for a sample application",
        "Study dashboarding best practices and alert fatigue prevention",
    ],
    "security": [
        "Learn security fundamentals — encryption, authentication, OWASP Top 10",
        "Perform a basic security audit on a sample web application",
        "Study network security, firewalls, and vulnerability scanning",
    ],
    "networking": [
        "Learn networking fundamentals — TCP/IP, DNS, HTTP/HTTPS, subnets",
        "Practice with network configuration and troubleshooting tools",
        "Study load balancing, proxies, and VPN concepts",
    ],
    "scripting": [
        "Learn Bash or PowerShell scripting fundamentals",
        "Write 5 automation scripts for common system tasks",
        "Study error handling, logging, and cron/task scheduling",
    ],

    # Mobile
    "react native": [
        "Learn React Native basics — components, navigation, styling",
        "Build a simple mobile app (e.g., notes app) with local storage",
        "Study platform-specific code and app deployment to stores",
    ],
    "flutter": [
        "Learn Dart basics and Flutter widget system",
        "Build a complete app with navigation, state management, and API calls",
        "Study platform channels and app store deployment process",
    ],
    "swift": [
        "Learn Swift fundamentals — optionals, protocols, closures",
        "Build an iOS app with UIKit or SwiftUI",
        "Study networking, Core Data, and App Store submission",
    ],
    "kotlin": [
        "Learn Kotlin basics — null safety, coroutines, data classes",
        "Build an Android app using Jetpack Compose",
        "Study MVVM architecture and Room database",
    ],
    "firebase": [
        "Learn Firebase services — Auth, Firestore, Cloud Functions",
        "Integrate Firebase into a mobile or web project",
        "Study real-time database, push notifications, and analytics",
    ],
    "ui design": [
        "Learn UI design principles — hierarchy, spacing, color theory",
        "Study Material Design and Human Interface Guidelines",
        "Design and prototype 3 mobile app screens in Figma",
    ],

    # QA & Testing
    "selenium": [
        "Learn Selenium WebDriver basics — locators, waits, actions",
        "Write automated test scripts for a sample web application",
        "Study Page Object Model pattern and test reporting",
    ],
    "test planning": [
        "Learn test planning fundamentals — test strategy, test cases, coverage",
        "Write a complete test plan for a sample application",
        "Study risk-based testing and defect management processes",
    ],
    "automation testing": [
        "Learn automation testing frameworks (pytest, JUnit, or TestNG)",
        "Automate 10+ test cases for a web application",
        "Study test data management and continuous testing in CI/CD",
    ],
    "jira": [
        "Learn JIRA basics — issues, workflows, boards, sprints",
        "Set up a sample project with proper workflows and boards",
        "Study JQL queries, dashboards, and reporting",
    ],
    "api testing": [
        "Learn API testing with Postman — requests, assertions, environments",
        "Write automated API tests using Python requests or REST Assured",
        "Study API contract testing and performance testing basics",
    ],

    # DBA & SysAdmin
    "performance tuning": [
        "Learn query optimization — EXPLAIN plans, index usage",
        "Practice optimizing 10 slow queries on a sample database",
        "Study database configuration tuning and caching strategies",
    ],
    "backup & recovery": [
        "Learn backup strategies — full, incremental, differential",
        "Set up automated backup and practice restore procedures",
        "Study disaster recovery planning and RTO/RPO concepts",
    ],
    "windows server": [
        "Learn Windows Server administration — AD, DNS, DHCP, Group Policy",
        "Set up a Windows Server lab environment with VMs",
        "Study PowerShell automation for server management",
    ],
    "shell scripting": [
        "Learn Bash scripting fundamentals — variables, loops, functions",
        "Write 5 system automation scripts (log rotation, backup, monitoring)",
        "Study error handling, input validation, and cron scheduling",
    ],
    "active directory": [
        "Learn AD concepts — domains, OUs, users, groups, GPOs",
        "Set up a lab AD environment and practice user management",
        "Study Group Policy configuration and troubleshooting",
    ],
    "virtualization": [
        "Learn virtualization concepts — hypervisors, VMs, containers",
        "Set up a virtual lab with VirtualBox or VMware",
        "Study resource allocation, snapshots, and high availability",
    ],

    # Product & Business
    "product strategy": [
        "Study product strategy frameworks — Porter's Five Forces, Blue Ocean",
        "Analyze 3 successful products and their market positioning",
        "Write a product strategy document for a hypothetical product",
    ],
    "agile": [
        "Learn Agile principles, Scrum framework, and sprint ceremonies",
        "Practice writing user stories with acceptance criteria",
        "Study Kanban, sprint planning, and retrospective techniques",
    ],
    "user research": [
        "Learn user research methods — interviews, surveys, usability testing",
        "Conduct 3 user interviews and synthesize findings",
        "Study persona creation and journey mapping techniques",
    ],
    "roadmap planning": [
        "Learn roadmap frameworks — Now/Next/Later, timeline-based",
        "Create a product roadmap for a sample application",
        "Study stakeholder communication and prioritization (RICE/MoSCoW)",
    ],
    "data analysis": [
        "Learn data analysis workflow — collection, cleaning, analysis, visualization",
        "Analyze a dataset and present findings with charts",
        "Study A/B testing, cohort analysis, and funnel metrics",
    ],
    "communication": [
        "Study professional communication — presentations, writing, stakeholder management",
        "Practice presenting technical concepts to non-technical audiences",
        "Learn active listening and feedback techniques",
    ],
    "requirements gathering": [
        "Learn requirements elicitation techniques — interviews, workshops, observation",
        "Write a detailed BRD (Business Requirements Document)",
        "Study user story mapping and requirements traceability",
    ],
    "process modeling": [
        "Learn process modeling notations — BPMN, flowcharts, swimlane diagrams",
        "Model 3 business processes and identify improvement opportunities",
        "Study gap analysis and process optimization techniques",
    ],

    # Design
    "figma": [
        "Learn Figma basics — frames, components, auto-layout, variants",
        "Design a complete mobile app UI (5+ screens) in Figma",
        "Study prototyping, design systems, and developer handoff",
    ],
    "wireframing": [
        "Learn wireframing principles — layout, hierarchy, user flows",
        "Create wireframes for 5 different page types (landing, dashboard, form)",
        "Study low-fidelity vs. high-fidelity wireframing approaches",
    ],
    "prototyping": [
        "Learn prototyping tools and interaction design patterns",
        "Build an interactive prototype with click-through navigation",
        "Study micro-interactions and animation principles for prototypes",
    ],
    "visual design": [
        "Study visual design principles — color theory, typography, spacing",
        "Create a design system with colors, fonts, and component styles",
        "Redesign an existing app interface with improved visual design",
    ],
    "usability testing": [
        "Learn usability testing methods — moderated, unmoderated, A/B testing",
        "Conduct a usability test with 3 participants and document findings",
        "Study heuristic evaluation and Nielsen's 10 usability heuristics",
    ],
    "adobe xd": [
        "Learn Adobe XD basics — artboards, components, repeat grid",
        "Design and prototype a mobile app with interactive elements",
        "Study design sharing, developer specs, and plugin ecosystem",
    ],

    # Game Development
    "unity": [
        "Learn Unity editor, GameObjects, components, and scripting with C#",
        "Build a simple 2D game (platformer or puzzle)",
        "Study physics, animation system, and UI toolkit",
    ],
    "unreal engine": [
        "Learn Unreal Editor, Blueprints, and basic C++ integration",
        "Build a simple 3D environment with player movement",
        "Study materials, lighting, and level design basics",
    ],
    "3d mathematics": [
        "Study vectors, matrices, and transformations in 3D space",
        "Learn quaternions, projections, and coordinate systems",
        "Apply 3D math in a simple game or graphics project",
    ],
    "game physics": [
        "Learn rigid body dynamics, collision detection, and raycasting",
        "Implement basic physics (gravity, bounce) from scratch",
        "Study physics engine integration and optimization",
    ],
    "shader programming": [
        "Learn HLSL/GLSL basics — vertex shaders, fragment shaders",
        "Write custom shaders for simple effects (color, lighting, outline)",
        "Study post-processing effects and shader optimization",
    ],

    # Embedded
    "rtos": [
        "Learn RTOS concepts — tasks, semaphores, queues, schedulers",
        "Set up FreeRTOS on a development board and run multi-task programs",
        "Study timing analysis, priority inversion, and debugging techniques",
    ],
    "microcontrollers": [
        "Learn microcontroller architecture — GPIO, UART, SPI, I2C",
        "Program an Arduino or STM32 for sensor reading and control",
        "Study interrupts, timers, and low-power modes",
    ],
    "circuit design": [
        "Learn basic circuit design — resistors, capacitors, transistors, op-amps",
        "Design and simulate circuits using tools like LTspice",
        "Study PCB layout basics and schematic reading",
    ],
    "embedded linux": [
        "Learn embedded Linux basics — cross-compilation, device trees, drivers",
        "Set up a Raspberry Pi project with custom kernel modules",
        "Study Buildroot or Yocto for custom Linux image creation",
    ],
    "debugging": [
        "Learn debugging tools — GDB, JTAG, logic analyzers",
        "Practice systematic debugging on sample buggy programs",
        "Study debugging methodologies and root cause analysis",
    ],
    "assembly": [
        "Learn assembly basics — registers, instructions, memory addressing",
        "Write small assembly programs for x86 or ARM architecture",
        "Study how C code compiles to assembly and optimize critical sections",
    ],

    # Security
    "network security": [
        "Learn network security fundamentals — firewalls, IDS/IPS, VPNs",
        "Set up and configure a firewall in a lab environment",
        "Study common network attacks (MITM, DDoS) and defense strategies",
    ],
    "siem": [
        "Learn SIEM concepts — log collection, correlation, alerting",
        "Set up a basic SIEM (Splunk or ELK) and ingest sample logs",
        "Study security event analysis and incident investigation",
    ],
    "penetration testing": [
        "Learn penetration testing methodology — recon, scanning, exploitation",
        "Practice on CTF platforms (HackTheBox, TryHackMe) — complete 5 challenges",
        "Study OWASP Top 10 vulnerabilities and how to test for them",
    ],
    "firewalls": [
        "Learn firewall types, rule configuration, and best practices",
        "Configure firewall rules for a sample network topology",
        "Study next-gen firewalls, application-layer filtering, and logging",
    ],
    "incident response": [
        "Learn incident response framework — preparation, detection, containment, recovery",
        "Create an incident response plan for a sample organization",
        "Study digital forensics basics and evidence preservation",
    ],
    "cryptography": [
        "Learn cryptographic primitives — symmetric/asymmetric encryption, hashing",
        "Implement basic encryption/decryption in Python",
        "Study TLS/SSL, digital certificates, and key management",
    ],
}

# Import priority classifier from gap_analyzer
from utils.gap_analyzer import get_skill_priority

import os
import re
import json
import logging
import time
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1


# ═══════════════════════════════════════════════════════════════════
# JSON CLEANUP UTILITIES (for roadmap responses)
# ═══════════════════════════════════════════════════════════════════

def _clean_roadmap_json(response_text: str) -> str:
    """
    Clean/repair a potentially malformed JSON response from AI for roadmaps.

    Steps:
      1. Strip whitespace
      2. Remove markdown code fences
      3. Extract JSON array substring
      4. Fix trailing commas
      5. Remove non-printable characters
    """
    text = response_text.strip()

    # Remove markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # Extract JSON array substring
    bracket_start = text.find("[")
    bracket_end = text.rfind("]")
    if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
        text = text[bracket_start:bracket_end + 1]

    # Fix trailing commas
    text = re.sub(r",\s*]", "]", text)
    text = re.sub(r",\s*}", "}", text)

    # Remove non-printable characters (except newlines/tabs)
    text = re.sub(r"[^\x20-\x7E\n\t]", "", text)

    return text


def _parse_roadmap_json_safe(response_text: str) -> list[dict]:
    """
    Parse AI roadmap response with multiple cleanup strategies.

    Returns parsed list of dicts on success, raises ValueError on failure.
    """
    raw = response_text.strip()
    logger.info(f"[Roadmap AI Response] (first 300 chars): {raw[:300]}")

    # Strategy 1: Direct parse
    try:
        result = json.loads(raw)
        if isinstance(result, list) and len(result) > 0:
            logger.info("[Roadmap Parse] Strategy 1 (direct) succeeded.")
            return result
    except json.JSONDecodeError:
        pass

    # Strategy 2: Clean and parse
    cleaned = _clean_roadmap_json(raw)
    try:
        result = json.loads(cleaned)
        if isinstance(result, list) and len(result) > 0:
            logger.info("[Roadmap Parse] Strategy 2 (cleaned) succeeded.")
            return result
    except json.JSONDecodeError:
        pass

    # Strategy 3: Regex extract JSON array
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list) and len(result) > 0:
                logger.info("[Roadmap Parse] Strategy 3 (regex extract) succeeded.")
                return result
        except json.JSONDecodeError:
            pass

    # Strategy 4: Try to recover partial roadmap entries
    partial = _extract_partial_roadmap(raw)
    if partial:
        logger.info(f"[Roadmap Parse] Strategy 4 (partial recovery) extracted {len(partial)} entries.")
        return partial

    raise ValueError("Could not parse AI roadmap response after all cleanup strategies.")


def _extract_partial_roadmap(text: str) -> list[dict]:
    """
    Last-resort: extract individual roadmap entries from malformed response.
    Looks for patterns like {"week": N, "skill": "...", "steps": [...]}
    """
    entries = []
    # Try to find individual JSON objects with week/skill/steps
    pattern = r'\{[^{}]*"week"\s*:\s*\d+[^{}]*"skill"\s*:\s*"[^"]*"[^{}]*"steps"\s*:\s*\[[^\]]*\][^{}]*\}'
    matches = re.findall(pattern, text, re.DOTALL)
    for m in matches:
        try:
            entry = json.loads(m)
            if isinstance(entry, dict) and "skill" in entry:
                entries.append(entry)
        except json.JSONDecodeError:
            continue

    return entries


# ═══════════════════════════════════════════════════════════════════
# AI ROADMAP GENERATION (PRIMARY) — with retry + robust parsing
# ═══════════════════════════════════════════════════════════════════

def _call_groq_roadmap(client, missing_skills, target_role, experience_level) -> str:
    """
    Make a single API call to Groq for roadmap generation.
    Returns the raw response text.
    """
    skills_list = ", ".join(missing_skills)

    prompt = (
        f"I want to become a {target_role}. My experience level is {experience_level}.\n"
        f"I am missing these skills: {skills_list}\n\n"
        "Create a personalized week-by-week learning roadmap.\n"
        "Rules:\n"
        "- One week per skill, in the order given\n"
        "- Each week has exactly 3 actionable learning steps\n"
        "- Steps should be specific and practical (mention real resources like LeetCode, official docs, projects)\n"
        f"- Tailor difficulty to {experience_level} level\n"
        "- Return ONLY a valid JSON array with this format:\n"
        '[{"week": 1, "skill": "SkillName", "steps": ["step1", "step2", "step3"]}, ...]\n'
        "- Return ONLY valid JSON. No explanation. No text. No markdown. No code fences."
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a career learning roadmap generator. "
                    "Return ONLY a valid JSON array. No markdown, no explanation. "
                    'Example output: [{"week": 1, "skill": "Python", "steps": ["step1", "step2", "step3"]}]'
                ),
            },
            {"role": "user", "content": prompt},
        ],
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=2048,
    )

    return chat_completion.choices[0].message.content.strip()


def generate_roadmap_ai(
    missing_skills: list[str],
    target_role: str,
    experience_level: str = "beginner",
) -> list[dict]:
    """
    PRIMARY: Generates a personalized roadmap using LLaMA 3.1 via Groq.

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
        raise ValueError("GROQ_API_KEY is not configured.")

    client = Groq(api_key=api_key)

    last_error = None
    last_response = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"[Roadmap Generation] Attempt {attempt}/{MAX_RETRIES}...")
            response_text = _call_groq_roadmap(client, missing_skills, target_role, experience_level)
            last_response = response_text

            # Parse with robust cleanup
            roadmap = _parse_roadmap_json_safe(response_text)

            if not isinstance(roadmap, list) or len(roadmap) == 0:
                raise ValueError("LLM did not return a valid roadmap list.")

            # Add priority to each entry
            result = []
            for entry in roadmap:
                skill = entry.get("skill", "Unknown")
                steps = entry.get("steps", [])
                if not isinstance(steps, list) or len(steps) == 0:
                    continue
                result.append({
                    "week": entry.get("week", len(result) + 1),
                    "skill": skill,
                    "steps": [str(s) for s in steps],
                    "priority": get_skill_priority(skill),
                })

            if result:
                logger.info(f"[Roadmap Generation] ✅ Success on attempt {attempt}. {len(result)} weeks generated.")
                return result
            else:
                logger.warning(f"[Roadmap Generation] Attempt {attempt}: Empty result after processing, retrying...")
                last_error = ValueError("LLM roadmap was empty after processing.")

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"[Roadmap Generation] Attempt {attempt} parse error: {e}")
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            continue

        except Exception as e:
            err_str = str(e).lower()
            # Critical errors — don't retry, raise immediately
            if any(kw in err_str for kw in ["api_key", "invalid", "authentication", "unauthorized", "401"]):
                logger.error(f"[Roadmap Generation] ❌ Auth error (no retry): {e}")
                raise
            if any(kw in err_str for kw in ["network", "connection", "timeout", "dns"]):
                logger.error(f"[Roadmap Generation] ❌ Network error (no retry): {e}")
                raise
            if "429" in str(e) or "rate" in err_str:
                logger.warning(f"[Roadmap Generation] ⚠️ Rate limited on attempt {attempt}")
                last_error = e
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS * 2)
                continue

            logger.warning(f"[Roadmap Generation] Attempt {attempt} error: {e}")
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            continue

    # All retries exhausted — try partial recovery from last response
    if last_response:
        logger.info("[Roadmap Generation] All retries exhausted. Attempting final partial recovery...")
        partial = _extract_partial_roadmap(last_response)
        if partial:
            result = []
            for entry in partial:
                skill = entry.get("skill", "Unknown")
                steps = entry.get("steps", [])
                if steps:
                    result.append({
                        "week": entry.get("week", len(result) + 1),
                        "skill": skill,
                        "steps": [str(s) for s in steps],
                        "priority": get_skill_priority(skill),
                    })
            if result:
                logger.info(f"[Roadmap Generation] ✅ Partial recovery: {len(result)} weeks from last response.")
                return result

    # Truly failed
    raise last_error or ValueError("AI roadmap generation failed after all retries.")


# ═══════════════════════════════════════════════════════════════════
# RULE-BASED ROADMAP GENERATION (FALLBACK)
# ═══════════════════════════════════════════════════════════════════

# Experience-level tips appended to fallback roadmap steps
LEVEL_TIPS = {
    "beginner": "💡 Tip: Start with official beginner tutorials and take your time with fundamentals.",
    "intermediate": "💡 Tip: Focus on building projects and reading real-world codebases.",
    "advanced": "💡 Tip: Dive into advanced patterns, contribute to open-source, and build production-grade projects.",
}


def generate_roadmap_fallback(
    missing_skills: list[str],
    experience_level: str = "beginner",
) -> list[dict]:
    """
    FALLBACK: Rule-based roadmap using pre-defined SKILL_ROADMAPS dict.

    Each skill has custom, actionable learning steps.
    Falls back to generic steps for skills not in the dict.
    """
    if not missing_skills:
        return []

    level_tip = LEVEL_TIPS.get(experience_level, LEVEL_TIPS["beginner"])
    roadmap = []

    for idx, skill in enumerate(missing_skills, start=1):
        skill_lower = skill.strip().lower()
        priority = get_skill_priority(skill)

        if skill_lower in SKILL_ROADMAPS:
            steps = list(SKILL_ROADMAPS[skill_lower])
        else:
            steps = [
                f"Research {skill} fundamentals — read official docs and beginner guides",
                f"Complete a hands-on tutorial or course on {skill}",
                f"Build a mini project applying {skill} to solidify understanding",
            ]

        steps.append(level_tip)

        roadmap.append({
            "week": idx,
            "skill": skill,
            "steps": steps,
            "priority": priority,
        })

    return roadmap


# ═══════════════════════════════════════════════════════════════════
# MAIN FUNCTION (AI + FALLBACK)
# ═══════════════════════════════════════════════════════════════════

def generate_roadmap(
    missing_skills: list[str],
    experience_level: str = "beginner",
    target_role: str = "Software Engineer",
    simulate_failure: bool = False,
) -> tuple[list[dict], str, str]:
    """
    Main roadmap generation — tries AI first, falls back to rule-based.

    Robust behavior:
      - When simulate_failure=False: ALWAYS prioritizes AI with 3 retries
        and JSON repair. Only falls back on true critical failures
        (network down, API key invalid).
      - When simulate_failure=True: Forces fallback mode.

    Args:
        missing_skills: Skills the user needs to learn.
        experience_level: "beginner", "intermediate", or "advanced".
        target_role: The user's target job role (for AI context).
        simulate_failure: If True, skip AI to demo fallback.

    Returns:
        (roadmap, method, error_message)
    """
    if not missing_skills:
        return [], "N/A", ""

    error_msg = ""

    if simulate_failure:
        logger.info("[Roadmap] Simulate failure ON — using fallback.")
        roadmap = generate_roadmap_fallback(missing_skills, experience_level)
        method = "Fallback"
        error_msg = "AI was intentionally skipped (simulate failure mode)."
    else:
        try:
            roadmap = generate_roadmap_ai(missing_skills, target_role, experience_level)
            method = "AI"
            logger.info(f"[Roadmap] ✅ AI roadmap successful. {len(roadmap)} weeks.")
        except Exception as e:
            logger.error(f"[Roadmap] ❌ AI failed after all retries: {e}. Switching to fallback.")
            roadmap = generate_roadmap_fallback(missing_skills, experience_level)
            method = "Fallback"
            err_str = str(e)
            if "429" in err_str or "rate" in err_str.lower():
                error_msg = "Groq API rate limit after retries — using pre-defined roadmap steps."
            elif "api_key" in err_str.lower() or "invalid" in err_str.lower() or "authentication" in err_str.lower():
                error_msg = "Invalid Groq API key. Check your .env file."
            elif "network" in err_str.lower() or "connection" in err_str.lower():
                error_msg = "Network error — could not reach Groq API."
            else:
                error_msg = f"AI roadmap generation failed after {MAX_RETRIES} retries: {type(e).__name__}"

    return roadmap, method, error_msg

