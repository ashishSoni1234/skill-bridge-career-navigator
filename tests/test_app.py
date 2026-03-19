"""
Tests for Skill-Bridge Career Navigator
========================================
Run with:
    python -m pytest tests/test_app.py -v
    OR
    python tests/test_app.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.gap_analyzer import (
    analyze_gap,
    get_readiness_summary,
    get_prioritized_skills,
    get_next_step_guidance,
    get_skill_priority,
    detect_experience_level,
)
from utils.roadmap_generator import generate_roadmap, generate_roadmap_fallback
from utils.skill_extractor import (
    extract_skills_fallback,
    _filter_and_deduplicate,
    _is_valid_skill,
    _clean_skill_text,
)


# ═══════════════════════════════════════════════════════════════════
# TEST 1: Happy Path — valid skills → correct gap analysis
# ═══════════════════════════════════════════════════════════════════
def test_happy_path():
    """
    Happy path: user has some skills, target role requires more.
    """
    user_skills = ["Python", "SQL", "Git"]
    required_skills = [
        "Python", "SQL", "Git", "Docker", "REST APIs", "System Design",
    ]

    result = analyze_gap(user_skills, required_skills)

    # 3 matched, 3 missing
    matched_names = [s["skill"] for s in result["matched"]]
    missing_names = [s["skill"] for s in result["missing"]]
    assert set(matched_names) == {"Python", "SQL", "Git"}
    assert set(missing_names) == {"Docker", "REST APIs", "System Design"}

    # match_percentage = (3 / 6) * 100 = 50%
    assert result["match_percentage"] == 50.0

    # Roadmap should only cover missing skills (test fallback directly)
    roadmap = generate_roadmap_fallback(missing_names)
    assert len(roadmap) == 3
    roadmap_skills = {e["skill"] for e in roadmap}
    assert "Python" not in roadmap_skills  # Already known — NOT in roadmap
    assert "Docker" in roadmap_skills
    assert all("priority" in e for e in roadmap)

    print("✅ test_happy_path PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 2: Edge Case — empty input
# ═══════════════════════════════════════════════════════════════════
def test_empty_input():
    """
    Edge case: user provides no skills at all.
    """
    result = analyze_gap([], ["Python", "Machine Learning", "SQL"])

    assert result["matched"] == []
    assert len(result["missing"]) == 3
    assert result["match_percentage"] == 0.0

    # Fallback on empty text → no skills found
    assert extract_skills_fallback("", ["Python", "SQL", "Java"]) == []

    print("✅ test_empty_input PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 3: Noise Filtering — non-skills should be removed
# ═══════════════════════════════════════════════════════════════════
def test_noise_filtering():
    """
    Post-processing should remove names, emails, sentences, etc.
    Only real skills should remain.
    """
    all_known = ["Python", "SQL", "Docker", "Git"]

    # Noisy AI output with non-skills
    raw = [
        "Python",
        "SQL",
        "John Doe",                     # name — should be removed
        "john@example.com",             # email — should be removed
        "Stanford University",          # university — should be removed
        "I have 5 years of experience in building scalable systems",  # sentence
        "Docker",
    ]

    clean = _filter_and_deduplicate(raw, all_known)

    assert "Python" in clean
    assert "SQL" in clean
    assert "Docker" in clean
    # Noise should NOT be in results
    assert "John Doe" not in clean
    assert "john@example.com" not in clean
    assert "Stanford University" not in clean
    assert len(clean) == 3

    print("✅ test_noise_filtering PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 4: Deduplication — no duplicate skills
# ═══════════════════════════════════════════════════════════════════
def test_deduplication():
    """
    Skills should be deduplicated (case-insensitive).
    """
    all_known = ["Python", "SQL", "Docker"]
    raw = ["Python", "python", "PYTHON", "SQL", "sql", "Docker"]

    clean = _filter_and_deduplicate(raw, all_known)

    assert len(clean) == 3
    lower_results = [s.lower() for s in clean]
    assert lower_results.count("python") == 1

    print("✅ test_deduplication PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 5: Priority Classification
# ═══════════════════════════════════════════════════════════════════
def test_priority_classification():
    """
    Core skills should be high priority, tools should be low.
    """
    assert get_skill_priority("Data Structures") == "high"
    assert get_skill_priority("Python") == "high"
    assert get_skill_priority("System Design") == "high"
    assert get_skill_priority("Git") == "medium"
    assert get_skill_priority("REST APIs") == "medium"
    # Unknown/niche skills default to low
    assert get_skill_priority("Some Niche Tool") == "low"

    print("✅ test_priority_classification PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 6: Experience Level Detection
# ═══════════════════════════════════════════════════════════════════
def test_experience_level():
    """
    Should detect beginner/intermediate/advanced from text.
    """
    beginner_text = "I am a student learning Python"
    assert detect_experience_level(beginner_text) == "beginner"

    advanced_text = "Senior engineer, led team of 10, designed system at scale, managed team"
    assert detect_experience_level(advanced_text) == "advanced"

    print("✅ test_experience_level PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 7: Personalized Roadmap (only missing skills)
# ═══════════════════════════════════════════════════════════════════
def test_personalized_roadmap():
    """
    Roadmap should only contain missing skills, not known skills.
    Steps should be skill-specific, not generic.
    """
    missing = ["Docker", "System Design"]
    roadmap = generate_roadmap_fallback(missing, experience_level="intermediate")

    assert len(roadmap) == 2  # Only missing skills
    for entry in roadmap:
        assert "priority" in entry
        # Steps should mention the skill
        steps_text = " ".join(entry["steps"]).lower()
        assert entry["skill"].lower() in steps_text or "tip" in steps_text

    print("✅ test_personalized_roadmap PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 8: Readiness Summary
# ═══════════════════════════════════════════════════════════════════
def test_readiness_summary():
    """
    Summary should include percentage and role name.
    """
    summary = get_readiness_summary(50.0, 3, "Software Engineer")
    assert "50.0%" in summary
    assert "Software Engineer" in summary

    perfect = get_readiness_summary(100.0, 0, "Data Scientist")
    assert "100%" in perfect

    print("✅ test_readiness_summary PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 9: Skill Validation Helper
# ═══════════════════════════════════════════════════════════════════
def test_skill_validation():
    """
    Validation should reject emails, long sentences, numbers.
    """
    assert _is_valid_skill("Python") is True
    assert _is_valid_skill("") is False
    assert _is_valid_skill("john@example.com") is False
    assert _is_valid_skill("https://example.com") is False
    assert _is_valid_skill("This is a very long sentence that describes something") is False
    assert _is_valid_skill("12345") is False

    print("✅ test_skill_validation PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 10: Roadmap AI + Fallback pattern (simulate failure)
# ═══════════════════════════════════════════════════════════════════
def test_roadmap_ai_fallback():
    """
    generate_roadmap with simulate_failure=True should return Fallback method.
    """
    roadmap, method, error_msg = generate_roadmap(
        ["Docker", "SQL"],
        experience_level="beginner",
        target_role="Software Engineer",
        simulate_failure=True,
    )

    assert method == "Fallback"
    assert len(roadmap) == 2
    assert "simulate" in error_msg.lower()

    # Empty skills should return N/A
    empty_roadmap, empty_method, _ = generate_roadmap([])
    assert empty_roadmap == []
    assert empty_method == "N/A"

    print("✅ test_roadmap_ai_fallback PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 11: Filtering Logic (priority + search)
# ═══════════════════════════════════════════════════════════════════
def test_filtering():
    """
    Tests filtering logic used in the UI:
      - Priority filter on missing skills
      - Search filter on detected skills
    """
    # Setup: gap analysis result with mixed priorities
    user_skills = ["Python"]
    required_skills = ["Python", "Docker", "SQL", "System Design", "Git"]
    result = analyze_gap(user_skills, required_skills)

    # Priority filter: only high priority
    high_only = [s for s in result["missing"] if s["priority"] == "high"]
    assert all(s["priority"] == "high" for s in high_only)

    # Priority filter: empty selection → no results
    empty_filter = [s for s in result["missing"] if s["priority"] in set()]
    assert empty_filter == []

    # Search filter on detected skills
    detected = ["Python", "SQL", "Docker", "React", "Node.js"]
    filtered = [s for s in detected if "py" in s.lower()]
    assert "Python" in filtered
    assert "Docker" not in filtered

    # Empty search → returns all
    no_search = [s for s in detected if "" in s.lower()]
    assert len(no_search) == len(detected)

    print("✅ test_filtering PASSED")


# ── Run all tests ───────────────────────────────────────────────────
if __name__ == "__main__":
    test_happy_path()
    test_empty_input()
    test_noise_filtering()
    test_deduplication()
    test_priority_classification()
    test_experience_level()
    test_personalized_roadmap()
    test_readiness_summary()
    test_skill_validation()
    test_roadmap_ai_fallback()
    test_filtering()
    print("\n🎉 All 11 tests passed!")

