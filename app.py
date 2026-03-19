"""
Skill-Bridge Career Navigator — Main Streamlit App
====================================================
Run with:  streamlit run app.py

Architecture:
  1. User enters skills (comma-separated) or pastes resume text + selects target role.
  2. Skills extracted using AI (LLaMA 3.1 via Groq) with rule-based fallback.
  3. Post-processing filters noise (names, emails, sentences) via skill whitelist.
  4. Gap analysis compares user skills vs. role requirements with priority levels.
  5. Readiness summary + Next-step guidance + Skill-specific roadmap generated.
"""

import json
import os
import streamlit as st
import streamlit.components.v1 as components
from utils.skill_extractor import extract_skills
from utils.gap_analyzer import (
    analyze_gap,
    get_readiness_summary,
    get_prioritized_skills,
    get_next_step_guidance,
    detect_experience_level,
)
from utils.roadmap_generator import generate_roadmap

# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="Skill-Bridge Career Navigator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Force Sidebar Expanded (override browser cache) ─────────────────
components.html(
    """
    <script>
        // Force sidebar to expanded state on load
        function expandSidebar() {
            const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
            if (sidebar && sidebar.getAttribute('aria-expanded') === 'false') {
                sidebar.setAttribute('aria-expanded', 'true');
                sidebar.style.width = '21rem';
                sidebar.style.minWidth = '21rem';
                sidebar.style.transform = 'none';
            }
            // Also click the expand button if sidebar is collapsed
            const expandBtn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
            if (expandBtn) {
                expandBtn.click();
            }
        }
        // Run immediately and after a short delay (for slow renders)
        expandSidebar();
        setTimeout(expandSidebar, 300);
        setTimeout(expandSidebar, 800);
    </script>
    """,
    height=0,
)

# ── Load Dataset ────────────────────────────────────────────────────
DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset.json")


@st.cache_data
def load_dataset() -> dict:
    """Load the job roles dataset from JSON."""
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


data = load_dataset()
roles = {role["title"]: role["skills"] for role in data["roles"]}
all_known_skills = sorted(
    set(skill for skills in roles.values() for skill in skills)
)

# ── Custom Styling ──────────────────────────────────────────────────
st.markdown(
    """
<style>
    .main-title { text-align: center; padding: 1rem 0; }
    .skill-tag {
        display: inline-block;
        background: #e3f2fd; color: #1565c0;
        padding: 0.25rem 0.75rem; margin: 0.15rem;
        border-radius: 1rem; font-size: 0.9rem;
    }
    .skill-tag-missing { background: #fce4ec; color: #c62828; }
    .skill-tag-matched { background: #e8f5e9; color: #2e7d32; }
    .skill-tag-required { background: #fff3e0; color: #e65100; }
    .priority-high { border-left: 4px solid #d32f2f; }
    .priority-medium { border-left: 4px solid #f57f17; }
    .priority-low { border-left: 4px solid #388e3c; }
    .week-card {
        background: #f5f5f5; padding: 1rem;
        border-radius: 0.5rem; margin-bottom: 0.75rem;
    }
    .summary-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        padding: 1.5rem; border-radius: 1rem; margin: 1rem 0;
    }
    .next-step-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #e3f2fd 100%);
        padding: 1.5rem; border-radius: 1rem; margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ──────────────────────────────────────────────────────────
st.markdown(
    "<h1 class='main-title'>🚀 Skill-Bridge Career Navigator</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#666; font-size:1.1rem;'>"
    "Identify your skill gaps and get a personalized learning roadmap"
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── Sidebar ─────────────────────────────────────────────────────────
all_role_names = list(roles.keys())

with st.sidebar:
    # ── Role Explorer (sidebar-only search) ─────────────────
    st.header("📋 Explore Roles")
    st.caption("Search & browse required skills for any role.")

    explorer_search = st.text_input(
        "🔍 Search roles to explore:",
        placeholder="Type to filter... (e.g. Data, Machine, Design)",
        key="explorer_search",
    )
    # Filter explorer roles based on search — independent of main dropdown
    if explorer_search and explorer_search.strip():
        explorer_roles = [
            r for r in all_role_names
            if explorer_search.strip().lower() in r.lower()
        ]
    else:
        explorer_roles = all_role_names

    if not explorer_roles:
        st.info(f'No roles match "{explorer_search}" — showing all.')
        explorer_roles = all_role_names

    explorer_role = st.selectbox(
        "Select a role to explore:",
        options=explorer_roles,
        key="explorer_role",
    )
    if explorer_role:
        st.markdown(f"**Required skills for {explorer_role}:**")
        skills_html = " ".join(
            f"<span class='skill-tag'>{s}</span>" for s in roles[explorer_role]
        )
        st.markdown(skills_html, unsafe_allow_html=True)

    st.divider()

    # ── Filters ─────────────────────────────────────────────
    st.header("🎯 Filters")
    priority_filter = st.multiselect(
        "Filter missing skills by priority:",
        options=["🔴 High", "🟡 Medium", "🟢 Low"],
        default=["🔴 High", "🟡 Medium", "🟢 Low"],
        key="priority_filter",
    )
    priority_map = {"🔴 High": "high", "🟡 Medium": "medium", "🟢 Low": "low"}
    selected_priorities = {priority_map[p] for p in priority_filter}

    match_filter = st.radio(
        "Show skills:",
        options=["All", "✔ Matched", "❌ Missing"],
        index=0,
        key="match_filter",
        horizontal=True,
    )

    # Active filter indicator
    active_labels = [p.split(" ")[1] for p in priority_filter]  # ["High", "Medium", ...]
    st.caption(f"Active: {', '.join(active_labels) if active_labels else 'None'} | View: {match_filter}")

    st.divider()

    # ── Settings ────────────────────────────────────────────
    st.header("⚙️ Settings")
    simulate_failure = st.checkbox(
        "🧪 Simulate AI failure (demo fallback)",
        value=False,
        help="Toggle ON to force fallback mode. Toggle OFF to use AI.",
    )
    if simulate_failure:
        st.error("⚠️ AI is disabled — using rule-based fallback.")
    else:
        st.success("✅ AI mode active (LLaMA 3 via Groq)")

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: INPUT
# ═══════════════════════════════════════════════════════════════════
st.subheader("📝 Your Skills or Resume")
user_input = st.text_area(
    "Enter your skills (comma-separated) or paste your resume text:",
    placeholder="e.g. Python, SQL, Machine Learning, Docker\n\n"
    "OR paste your full resume text here for AI-powered skill extraction...",
    height=150,
)

st.subheader("🎯 Select or Search Target Role")
target_role = st.selectbox(
    "Select the role you're aiming for:",
    options=all_role_names,
    key="target_role",
    help="This dropdown always shows all roles. Use sidebar to explore roles separately.",
)

# ═══════════════════════════════════════════════════════════════════
# SECTION 2: REQUIRED SKILLS (shown BEFORE analysis for transparency)
# ═══════════════════════════════════════════════════════════════════
st.divider()
st.subheader(f"📌 Required Skills for {target_role}")
required_html = " ".join(
    f"<span class='skill-tag skill-tag-required'>{s}</span>"
    for s in roles[target_role]
)
st.markdown(required_html, unsafe_allow_html=True)
st.divider()

# ═══════════════════════════════════════════════════════════════════
# ANALYZE BUTTON
# ═══════════════════════════════════════════════════════════════════
analyze_clicked = st.button(
    "🔍 Analyze My Skills", type="primary", use_container_width=True
)

if analyze_clicked:
    # ── Input Validation ────────────────────────────────────────
    if not user_input or not user_input.strip():
        st.error("⚠️ Please enter your skills or paste your resume text.")
        st.stop()

    # ═══════════════════════════════════════════════════════════════
    # SKILL EXTRACTION (AI + Fallback + Post-Processing)
    # ═══════════════════════════════════════════════════════════════
    # try: AI (LLaMA 3.1 via Groq) → except: fallback (keyword matching)
    # Post-processing: whitelist filter + dedup + normalize
    with st.spinner("🧠 Extracting skills..."):
        detected_skills, method, error_msg = extract_skills(
            user_input.strip(),
            all_known_skills,
            simulate_failure=simulate_failure,
        )

    # Also parse comma-separated tokens (ensures manually typed skills are captured)
    manual_tokens = [s.strip() for s in user_input.split(",") if s.strip()]
    existing_lower = {s.lower() for s in detected_skills}
    for token in manual_tokens:
        token_clean = token.strip()
        if len(token_clean) <= 40 and token_clean.lower() not in existing_lower:
            # Only add if it looks like a skill and matches known skills
            if token_clean.lower() in {s.lower() for s in all_known_skills}:
                canonical = next(
                    (s for s in all_known_skills if s.lower() == token_clean.lower()),
                    token_clean,
                )
                detected_skills.append(canonical)
                existing_lower.add(token_clean.lower())

    # ── Extraction Method Indicator ────────────────────────────
    if method == "AI":
        st.success("⚙️ Extraction Method: **AI (LLaMA 3 via Groq)** with fallback support")
    else:
        if simulate_failure:
            st.warning("⚠️ Using **rule-based fallback** (AI intentionally disabled via toggle)")
        else:
            st.warning("⚠️ Using **rule-based fallback** (AI unavailable)")
        if error_msg:
            st.info(f"💡 Reason: {error_msg}")

    # ── Detect experience level ────────────────────────────────
    experience_level = detect_experience_level(user_input)

    # ═══════════════════════════════════════════════════════════════
    # GAP ANALYSIS
    # ═══════════════════════════════════════════════════════════════
    required_skills = roles[target_role]
    gap_result = analyze_gap(detected_skills, required_skills)

    st.divider()

    # ═══════════════════════════════════════════════════════════════
    # 2. SKILL SEARCH (filter detected skills)
    # ═══════════════════════════════════════════════════════════════
    skill_search = st.text_input(
        "🔍 Search detected skills:",
        placeholder="e.g. Python, Docker...",
        key="skill_search",
    )

    # Apply skill search filter
    if skill_search and skill_search.strip():
        filtered_detected = [
            s for s in detected_skills
            if skill_search.strip().lower() in s.lower()
        ]
    else:
        filtered_detected = detected_skills

    # Apply priority filter to missing skills
    filtered_missing = [
        s for s in gap_result["missing"]
        if s["priority"] in selected_priorities
    ]

    # Apply match filter — decide what to show
    show_matched = match_filter in ["All", "✔ Matched"]
    show_missing = match_filter in ["All", "❌ Missing"]

    # ── Filter Summary ─────────────────────────────────────────
    filter_parts = []
    if show_matched:
        filter_parts.append(f"**{len(filtered_detected)}** detected")
    if show_missing:
        filter_parts.append(f"**{len(filtered_missing)}** missing")
    active_labels_summary = [p.split(' ')[1] for p in priority_filter]
    st.caption(
        f"📊 Showing {' | '.join(filter_parts)} skill(s) • "
        f"Priority: {', '.join(active_labels_summary) if active_labels_summary else 'None'} • "
        f"View: {match_filter}"
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 3: DETECTED SKILLS (with Show More + search)
    # ═══════════════════════════════════════════════════════════════
    res_col1, res_col2 = st.columns(2)

    with res_col1:
        if show_matched:
            st.subheader(f"🟢 Detected Skills ({len(filtered_detected)})")
            if filtered_detected:
                SHOW_LIMIT = 10
                visible = filtered_detected[:SHOW_LIMIT]
                hidden = filtered_detected[SHOW_LIMIT:]

                tags = " ".join(
                    f"<span class='skill-tag'>{s}</span>" for s in visible
                )
                st.markdown(tags, unsafe_allow_html=True)

                if hidden:
                    with st.expander(f"+ Show {len(hidden)} more skills"):
                        more_tags = " ".join(
                            f"<span class='skill-tag'>{s}</span>" for s in hidden
                        )
                        st.markdown(more_tags, unsafe_allow_html=True)
            elif skill_search:
                st.info(f"No detected skills match \"{skill_search}\"")
            else:
                st.warning("No skills detected. Try adding more detail.")

    # ═══════════════════════════════════════════════════════════════
    # SECTION 4: MISSING SKILLS (with priority filter)
    # ═══════════════════════════════════════════════════════════════
    with res_col2:
        if show_missing:
            st.subheader(f"🔴 Missing Skills ({len(filtered_missing)})")
            if filtered_missing:
                high = [s for s in filtered_missing if s["priority"] == "high"]
                medium = [s for s in filtered_missing if s["priority"] == "medium"]
                low = [s for s in filtered_missing if s["priority"] == "low"]

                if high:
                    st.markdown("**🔴 High Priority (Core Skills)**")
                    tags = " ".join(
                        f"<span class='skill-tag skill-tag-missing'>{s['skill']}</span>"
                        for s in high
                    )
                    st.markdown(tags, unsafe_allow_html=True)

                if medium:
                    st.markdown("**🟡 Medium Priority**")
                    tags = " ".join(
                        f"<span class='skill-tag skill-tag-missing'>{s['skill']}</span>"
                        for s in medium
                    )
                    st.markdown(tags, unsafe_allow_html=True)

                if low:
                    st.markdown("**🟢 Low Priority (Nice to Have)**")
                    tags = " ".join(
                        f"<span class='skill-tag skill-tag-missing'>{s['skill']}</span>"
                        for s in low
                    )
                    st.markdown(tags, unsafe_allow_html=True)
            elif not selected_priorities:
                st.info("No priority levels selected. Use the sidebar filter.")
            else:
                st.balloons()
                st.success("🎉 You have all the required skills!")

    # ═══════════════════════════════════════════════════════════════
    # SECTION 5: SKILL MATCH % (progress bar)
    # ═══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("📊 Skill Match")

    match_col, pct_col = st.columns([3, 1])
    with match_col:
        st.progress(gap_result["match_percentage"] / 100)
    with pct_col:
        st.metric("Match", f"{gap_result['match_percentage']}%")

    if gap_result["matched"]:
        matched_tags = " ".join(
            f"<span class='skill-tag skill-tag-matched'>✔ {s['skill']}</span>"
            for s in gap_result["matched"]
        )
        st.markdown(f"**Matched:** {matched_tags}", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # SECTION 6: READINESS SUMMARY
    # ═══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("📊 Readiness Summary")

    summary = get_readiness_summary(
        gap_result["match_percentage"],
        len(gap_result["missing"]),
        target_role,
    )
    st.markdown(
        f"<div class='summary-box'>{summary}</div>",
        unsafe_allow_html=True,
    )

    # Show experience level detection
    level_emoji = {"beginner": "🌱", "intermediate": "📈", "advanced": "🚀"}
    st.markdown(
        f"**Detected Level:** {level_emoji.get(experience_level, '')} "
        f"{experience_level.title()} — roadmap is tailored accordingly."
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 7: NEXT STEP GUIDANCE
    # ═══════════════════════════════════════════════════════════════
    missing_list = [s["skill"] for s in gap_result["missing"]]
    prioritized = get_prioritized_skills(missing_list)

    if prioritized:
        st.subheader("🚀 Recommended Next Step")
        guidance = get_next_step_guidance(prioritized)
        st.markdown(
            f"<div class='next-step-box'>{guidance}</div>",
            unsafe_allow_html=True,
        )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 8: PERSONALIZED ROADMAP (only for missing skills!)
    # ═══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("🗺️ Personalized Learning Roadmap")

    if prioritized:
        st.caption(
            f"📌 This roadmap covers **only your missing skills** — "
            f"skills you already know are skipped. "
            f"Tailored for **{experience_level}** level."
        )

        # Generate roadmap: AI first → fallback to rule-based
        with st.spinner("🗺️ Generating personalized roadmap..."):
            roadmap, roadmap_method, roadmap_error = generate_roadmap(
                prioritized,
                experience_level=experience_level,
                target_role=target_role,
                simulate_failure=simulate_failure,
            )

        # Show roadmap generation method
        if roadmap_method == "AI":
            st.success("🗺️ Roadmap generated by **AI (LLaMA 3 via Groq) with Fallback Support**")
        elif roadmap_method == "Fallback":
            st.warning("🗺️ Roadmap generated using **pre-defined learning steps** (rule-based)")
            if roadmap_error:
                st.info(f"💡 Reason: {roadmap_error}")

        for entry in roadmap:
            priority = entry.get("priority", "medium")
            priority_class = f"priority-{priority}"
            priority_badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                priority, "🟡"
            )

            st.markdown(
                f"<div class='week-card {priority_class}'>"
                f"<strong>📅 Week {entry['week']}: {entry['skill']}</strong> "
                f"&nbsp;{priority_badge}"
                f"</div>",
                unsafe_allow_html=True,
            )
            for step in entry["steps"]:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;→ {step}")
            st.write("")
    else:
        st.info("No roadmap needed — you're already a great fit! 🎯")

# ── Footer ──────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Built with ❤️ using Streamlit • AI powered by LLaMA 3 (Groq) • "
    "Skill-Bridge Career Navigator"
)
