import pytest

from matching import (
    calculate_skill_score,
    calculate_experience_score,
    calculate_trait_score,
    calculate_availability_score,
    calculate_match,
    rank_candidates_for_job,
    rank_jobs_for_candidate,
)

@pytest.fixture
def candidate():
    return {
        "name": "Sherlock H.",
        "skills": [
            "deduction",
            "pattern-recognition",
            "forensics",
        ],
        "experience_years": 8,
        "availability": "Immediate",
        "traits": ["analytical", "blunt"],
        "quirk": "Solves problems by eliminating the impossible.",
    }


@pytest.fixture
def job():
    return {
        "title": "Backend Detective",
        "required_skills": [
            "deduction",
            "pattern-recognition",
            "forensics",
        ],
        "min_experience_years": 3,
        "culture_keywords": ["analytical", "autonomous"],
        "tagline": "We have a bug. We have no leads. We have you.",
    }


def test_all_required_skills_match(candidate, job):
    score, matched = calculate_skill_score(candidate, job)

    assert score == 100
    assert len(matched) == 3


def test_partial_skill_overlap(candidate, job):
    candidate["skills"] = ["deduction"]

    score, matched = calculate_skill_score(candidate, job)

    assert score == pytest.approx(100 / 3)
    assert matched == ["deduction"]


def test_experience_meets_minimum(candidate, job):
    assert calculate_experience_score(candidate, job) == 100


def test_experience_below_minimum(candidate, job):
    candidate["experience_years"] = 2

    assert calculate_experience_score(candidate, job) == 0


def test_trait_alignment(candidate, job):
    score, matched = calculate_trait_score(candidate, job)

    assert score == 50
    assert matched == ["analytical"]


def test_empty_culture_keywords(candidate, job):
    job["culture_keywords"] = []

    score, matched = calculate_trait_score(candidate, job)

    assert score == 0
    assert matched == []


def test_immediate_availability(candidate):
    assert calculate_availability_score(candidate) == 100


def test_no_skill_overlap_is_ineligible(candidate, job):
    candidate["skills"] = ["woodworking", "minimalism"]

    result = calculate_match(candidate, job)

    assert result is None


def test_complete_match_score(candidate, job):
    result = calculate_match(candidate, job)

    assert result["score"] == 92.5
    assert result["skill_score"] == 100
    assert result["experience_score"] == 100
    assert result["trait_score"] == 50
    assert result["availability_score"] == 100
    assert "deduction" in result["explanation"]


def test_candidates_are_ranked_by_score():
    matches = rank_candidates_for_job(1)

    scores = [match["score"] for match in matches]

    assert scores == sorted(scores, reverse=True)


def test_sherlock_ranks_for_backend_detective():
    matches = rank_candidates_for_job(1)

    sherlock = next(
        match for match in matches
        if match["candidate_name"] == "Sherlock H."
    )

    assert sherlock["score"] == 92.5
    assert matches[0]["candidate_name"] == "Sherlock H."


def test_jobs_are_ranked_by_score_for_sherlock():
    matches = rank_jobs_for_candidate(1)

    scores = [match["score"] for match in matches]

    assert scores == sorted(scores, reverse=True)
    assert matches[0]["job_title"] == "Backend Detective"
