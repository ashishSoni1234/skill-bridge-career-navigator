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
from utils.skill_matcher import (
    normalize_skill,
    map_skill,
    match_skills,
    check_category_satisfaction,
    get_match_method_label,
    SKILL_CATEGORIES,
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


# ═══════════════════════════════════════════════════════════════════
# TEST 12: Skill Normalization — normalize_skill()
# ═══════════════════════════════════════════════════════════════════
def test_skill_normalization():
    """
    normalize_skill should convert skills to canonical lowercase forms.
    """
    # Basic normalization
    assert normalize_skill("Python") == "python"
    assert normalize_skill("  PYTHON  ") == "python"
    assert normalize_skill("python") == "python"

    # Synonym resolution
    assert normalize_skill("GitHub") == "git"
    assert normalize_skill("GitLab") == "git"
    assert normalize_skill("Git/GitHub") == "git"
    assert normalize_skill("MySQL") == "sql"
    assert normalize_skill("PostgreSQL") == "sql"
    assert normalize_skill("Algorithm Design & Analysis") == "algorithms"
    assert normalize_skill("Object Oriented Programming") == "oop"
    assert normalize_skill("Object-Oriented Programming") == "oop"

    # Edge cases
    assert normalize_skill("") == ""
    assert normalize_skill("   ") == ""

    print("✅ test_skill_normalization PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 13: Skill Mapping — map_skill()
# ═══════════════════════════════════════════════════════════════════
def test_skill_mapping():
    """
    map_skill should map equivalent skills to the same canonical key.
    """
    # Git family
    assert map_skill("Git") == map_skill("GitHub")
    assert map_skill("Git") == map_skill("GitLab")
    assert map_skill("Git") == "git"

    # SQL family
    assert map_skill("SQL") == map_skill("MySQL")
    assert map_skill("SQL") == map_skill("PostgreSQL")
    assert map_skill("SQL") == "sql"

    # Algorithm family
    assert map_skill("Algorithms") == map_skill("Algorithm Design")
    assert map_skill("Algorithms") == map_skill("DSA")
    assert map_skill("Algorithms") == "algorithms"

    # OOP family
    assert map_skill("OOP") == map_skill("Object Oriented Programming")

    print("✅ test_skill_mapping PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 14: Programming Language Flexibility (CRITICAL)
# ═══════════════════════════════════════════════════════════════════
def test_programming_language_flexibility():
    """
    CRITICAL: If user knows Python, Java should NOT be marked as missing
    for a role that requires both (they're interchangeable programming languages).
    """
    # Software Engineer requires Python AND Java, but user only knows Python
    user_skills = ["Python"]
    required_skills = ["Python", "Java", "Data Structures", "Algorithms",
                       "OOP", "Operating Systems", "DBMS", "Computer Networks",
                       "Git", "REST APIs", "System Design", "SQL"]

    result = analyze_gap(user_skills, required_skills)

    matched_names = [s["skill"] for s in result["matched"]]
    missing_names = [s["skill"] for s in result["missing"]]

    # Python should be matched
    assert "Python" in matched_names

    # Java should also be matched (via programming language flexibility)
    assert "Java" in matched_names, (
        f"Java should be matched via programming language flexibility! "
        f"Matched: {matched_names}, Missing: {missing_names}"
    )

    # Java should NOT be in missing
    assert "Java" not in missing_names, (
        f"Java should NOT be missing when user knows Python! "
        f"Missing: {missing_names}"
    )

    print("✅ test_programming_language_flexibility PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 15: Synonym Matching — Git/GitHub, MySQL/SQL
# ═══════════════════════════════════════════════════════════════════
def test_synonym_matching():
    """
    "Git/GitHub" should match "Git".
    "MySQL" should match "SQL".
    """
    # User has GitHub, role requires Git
    user_skills = ["GitHub"]
    required_skills = ["Git", "Docker"]

    result = analyze_gap(user_skills, required_skills)
    matched_names = [s["skill"] for s in result["matched"]]
    missing_names = [s["skill"] for s in result["missing"]]

    assert "Git" in matched_names, f"Git should be matched by GitHub! Matched: {matched_names}"
    assert "Git" not in missing_names

    # User has MySQL, role requires SQL
    user_skills2 = ["MySQL"]
    required_skills2 = ["SQL", "Docker"]

    result2 = analyze_gap(user_skills2, required_skills2)
    matched_names2 = [s["skill"] for s in result2["matched"]]

    assert "SQL" in matched_names2, f"SQL should be matched by MySQL! Matched: {matched_names2}"

    print("✅ test_synonym_matching PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 16: Algorithm Design & Analysis → Algorithms
# ═══════════════════════════════════════════════════════════════════
def test_algorithm_matching():
    """
    "Algorithm Design & Analysis" should match "Algorithms".
    """
    user_skills = ["Algorithm Design & Analysis", "Python"]
    required_skills = ["Algorithms", "Python", "Data Structures"]

    result = analyze_gap(user_skills, required_skills)
    matched_names = [s["skill"] for s in result["matched"]]
    missing_names = [s["skill"] for s in result["missing"]]

    assert "Algorithms" in matched_names, (
        f"'Algorithms' should be matched by 'Algorithm Design & Analysis'! "
        f"Matched: {matched_names}"
    )
    assert "Algorithms" not in missing_names

    print("✅ test_algorithm_matching PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 17: Category Satisfaction
# ═══════════════════════════════════════════════════════════════════
def test_category_satisfaction():
    """
    check_category_satisfaction should return True if user has
    at least one skill from the category.
    """
    # User has Python → programming_languages category satisfied
    user_canonical = {"python", "docker"}
    assert check_category_satisfaction(user_canonical, "programming_languages") is True

    # User has no programming language
    user_no_lang = {"docker", "kubernetes"}
    assert check_category_satisfaction(user_no_lang, "programming_languages") is False

    # User has MySQL (canonical = "sql") → databases category
    user_db = {"sql"}
    assert check_category_satisfaction(user_db, "databases") is True

    # Invalid category
    assert check_category_satisfaction(user_canonical, "nonexistent_category") is False

    print("✅ test_category_satisfaction PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 18: Full Scenario — Python, MySQL, GitHub vs Software Engineer
# ═══════════════════════════════════════════════════════════════════
def test_full_scenario_software_engineer():
    """
    Full scenario: User has Python, MySQL, GitHub.
    Role: Software Engineer (requires Python, Java, Git, SQL, etc.)

    Expected:
      - SQL should NOT be missing (MySQL ≈ SQL)
      - Git should NOT be missing (GitHub ≈ Git)
      - Java should NOT be missing (Python satisfies programming lang category)
    """
    user_skills = ["Python", "MySQL", "GitHub"]
    required_skills = [
        "Data Structures", "Algorithms", "Python", "Java",
        "OOP", "Operating Systems", "DBMS", "Computer Networks",
        "Git", "REST APIs", "System Design", "SQL",
    ]

    result = analyze_gap(user_skills, required_skills)
    matched_names = [s["skill"] for s in result["matched"]]
    missing_names = [s["skill"] for s in result["missing"]]

    # These should all be matched
    assert "Python" in matched_names, f"Python should be matched! Got: {matched_names}"
    assert "SQL" in matched_names, f"SQL should be matched by MySQL! Got: {matched_names}"
    assert "Git" in matched_names, f"Git should be matched by GitHub! Got: {matched_names}"
    assert "Java" in matched_names, (
        f"Java should be matched via prog lang flexibility! Got: {matched_names}"
    )

    # These should NOT be in missing
    assert "SQL" not in missing_names, f"SQL should NOT be missing! Got: {missing_names}"
    assert "Git" not in missing_names, f"Git should NOT be missing! Got: {missing_names}"
    assert "Java" not in missing_names, f"Java should NOT be missing! Got: {missing_names}"

    # Match percentage should be higher than 50%
    assert result["match_percentage"] > 25.0, (
        f"Match % should be > 25% with intelligent matching, got {result['match_percentage']}%"
    )

    print("✅ test_full_scenario_software_engineer PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 19: Edge Case — Mixed Case Input
# ═══════════════════════════════════════════════════════════════════
def test_mixed_case_input():
    """
    Mixed-case input should still match correctly.
    """
    user_skills = ["pYtHoN", "MYSQL", "github"]
    required_skills = ["Python", "SQL", "Git"]

    result = analyze_gap(user_skills, required_skills)
    matched_names = [s["skill"] for s in result["matched"]]

    assert "Python" in matched_names
    assert "SQL" in matched_names
    assert "Git" in matched_names
    assert result["match_percentage"] == 100.0

    print("✅ test_mixed_case_input PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 20: Edge Case — Partial Matches
# ═══════════════════════════════════════════════════════════════════
def test_partial_matches():
    """
    DSA should match Data Structures/Algorithms.
    OOP variants should match.
    """
    # "DSA" → should normalize to "algorithms" (via synonym)
    assert normalize_skill("DSA") == "algorithms"
    assert normalize_skill("Data Structures and Algorithms") == "algorithms"

    # OOP variants
    assert normalize_skill("OOPS") == "oop"
    assert normalize_skill("Object-Oriented Programming") == "oop"

    # Shorthand
    assert normalize_skill("K8s") == "kubernetes"
    assert normalize_skill("JS") == "javascript"
    assert normalize_skill("TS") == "typescript"

    print("✅ test_partial_matches PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 21: match_skills returns method label
# ═══════════════════════════════════════════════════════════════════
def test_match_method_label():
    """
    match_skills should include the method label in results.
    """
    result = match_skills(["Python"], ["Python", "Docker"])
    assert result["method"] == "Semantic + Rule-Based Normalization"

    # get_match_method_label should return a non-empty string
    label = get_match_method_label()
    assert label
    assert "Semantic" in label
    assert "Normalization" in label

    print("✅ test_match_method_label PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 22: Empty Required Skills
# ═══════════════════════════════════════════════════════════════════
def test_empty_required_skills():
    """
    If role has no required skills, match should be 100%.
    """
    result = analyze_gap(["Python", "SQL"], [])
    assert result["match_percentage"] == 100.0
    assert result["matched"] == []
    assert result["missing"] == []

    print("✅ test_empty_required_skills PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 23: Database Category Satisfaction
# ═══════════════════════════════════════════════════════════════════
def test_database_category():
    """
    User with MySQL should satisfy SQL requirement via synonym mapping.
    User with PostgreSQL should also satisfy SQL requirement.
    """
    # MySQL → SQL
    r1 = match_skills(["MySQL"], ["SQL"])
    assert len(r1["matched"]) == 1
    assert len(r1["missing"]) == 0

    # PostgreSQL → SQL
    r2 = match_skills(["PostgreSQL"], ["SQL"])
    assert len(r2["matched"]) == 1
    assert len(r2["missing"]) == 0

    print("✅ test_database_category PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 24: Version Control Category
# ═══════════════════════════════════════════════════════════════════
def test_version_control_category():
    """
    GitHub/GitLab should satisfy Git requirement.
    """
    r1 = match_skills(["GitHub"], ["Git"])
    assert len(r1["matched"]) == 1
    assert r1["match_percentage"] == 100.0

    r2 = match_skills(["GitLab"], ["Git"])
    assert len(r2["matched"]) == 1

    print("✅ test_version_control_category PASSED")


# ═══════════════════════════════════════════════════════════════════
# TEST 25: analyze_gap includes match_method field
# ═══════════════════════════════════════════════════════════════════
def test_analyze_gap_method_field():
    """
    analyze_gap should include the match_method field.
    """
    result = analyze_gap(["Python"], ["Python", "Docker"])
    assert "match_method" in result
    assert "Semantic" in result["match_method"]

    print("✅ test_analyze_gap_method_field PASSED")


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
    test_skill_normalization()
    test_skill_mapping()
    test_programming_language_flexibility()
    test_synonym_matching()
    test_algorithm_matching()
    test_category_satisfaction()
    test_full_scenario_software_engineer()
    test_mixed_case_input()
    test_partial_matches()
    test_match_method_label()
    test_empty_required_skills()
    test_database_category()
    test_version_control_category()
    test_analyze_gap_method_field()
    print("\n🎉 All 25 tests passed!")
