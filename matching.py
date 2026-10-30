#The main business logic , i.e. the matching algorithm, is implemented in this file.
import json
import sqlite3

def calculate_skill_score(candidate, job):
    candidate_skills = set(candidate["skills"])
    required_skills = set(job["required_skills"])

    if not required_skills:
        raise ValueError("Job must have at least one required skill.") #handles the case where a job has no required skills and further creates division by zero 
    matched_skills = candidate_skills & required_skills
    score = len(matched_skills) / len(required_skills) * 100
    return score, sorted(matched_skills)


def calculate_experience_score(candidate, job):
    candidate_experience = candidate["experience_years"]
    minimum_experience = job["min_experience_years"]

    if candidate_experience >= minimum_experience:
        return 100
    else:
        return 0

def calculate_trait_score(candidate, job):
    candidate_traits = set(candidate["traits"])
    culture_keywords = set(job["culture_keywords"])

    if not culture_keywords:
        return 0, []
    
    matched_traits = candidate_traits & culture_keywords
    score = len(matched_traits) / len(culture_keywords) * 100
    return score, sorted(matched_traits)


def calculate_availability_score(candidate):
    availability_scores = {
        "Immediate": 100,
        "2 weeks": 70,
        "Not looking": 20
    }

    availability = candidate["availability"]
    return availability_scores.get(availability, 0)


def calculate_match(candidate, job, weights=None):
    if weights is None:
        weights = {
            "skills": 50,
            "experience": 25,
            "traits": 15,
            "availability": 10
        }

    if sum(weights.values()) != 100:
        raise ValueError("Weights must add up to 100.")

    # Calculate skill overlap first
    skill_score, matched_skills = calculate_skill_score(candidate, job)

    # Reject candidates with no matching required skills
    if not matched_skills:
        return None

    # Calculate the remaining components
    experience_score = calculate_experience_score(candidate, job)
    trait_score, matched_traits = calculate_trait_score(candidate, job)
    availability_score = calculate_availability_score(candidate)

    # Calculate the weighted total
    final_score = (
        skill_score * weights["skills"]
        + experience_score * weights["experience"]
        + trait_score * weights["traits"]
        + availability_score * weights["availability"]
    ) / 100

    # Build an explanation from the actual evidence
    explanation_parts = []

    explanation_parts.append(
    f"Matched {len(matched_skills)} of "
    f"{len(job['required_skills'])} required skills: "
    + ", ".join(matched_skills)
    )

    if experience_score == 100:
        explanation_parts.append(
            f"meets the minimum experience of "
            f"{job['min_experience_years']} years"
        )
    else:
        explanation_parts.append(
            f"falls below the minimum experience of "
            f"{job['min_experience_years']} years"
        )

    if matched_traits:
        explanation_parts.append(
            "matches culture keywords: " + ", ".join(matched_traits)
        )

    explanation_parts.append(
        f"availability: {candidate['availability']}"
    )

    return {
        "score": round(final_score, 2),
        "skill_score": round(skill_score, 2),
        "experience_score": experience_score,
        "trait_score": round(trait_score, 2),
        "availability_score": availability_score,
        "matched_skills": matched_skills,
        "matched_traits": matched_traits,
        "explanation": "; ".join(explanation_parts) + "."
    }

def get_candidates():
    conn = sqlite3.connect("recruiter.db")
    conn.row_factory = sqlite3.Row

    try:
        rows = conn.execute(
            "SELECT * FROM candidates"
        ).fetchall()

        candidates = []

        for row in rows:
            candidate = dict(row)

            candidate["skills"] = json.loads(candidate["skills"])
            candidate["traits"] = json.loads(candidate["traits"])

            candidates.append(candidate)

        return candidates

    finally:
        conn.close()


def get_jobs():
    conn = sqlite3.connect("recruiter.db")
    conn.row_factory = sqlite3.Row

    try:
        rows = conn.execute(
            "SELECT * FROM jobs"
        ).fetchall()

        jobs = []

        for row in rows:
            job = dict(row)

            job["required_skills"] = json.loads(
                job["required_skills"]
            )
            job["culture_keywords"] = json.loads(
                job["culture_keywords"]
            )

            jobs.append(job)

        return jobs

    finally:
        conn.close()


def rank_candidates_for_job(job_id, weights=None):
    # Load all jobs and find the requested job
    jobs = get_jobs()

    job = next(
        (job for job in jobs if job["id"] == job_id),
        None
    )

    if job is None:
        raise ValueError(f"Job with ID {job_id} not found.")

    # Load all candidates
    candidates = get_candidates()

    ranked_matches = []

    # Score every candidate against this job
    for candidate in candidates:
        match = calculate_match(candidate, job, weights)

        # Skip candidates with no matching required skills
        if match is None:
            continue

        # Store candidate identity along with the score details
        ranked_matches.append({
            "candidate_id": candidate["id"],
            "candidate_name": candidate["name"],
            **match
        })

    # Sort by score, then apply deterministic tie-breakers
    ranked_matches.sort(
        key=lambda item: (
            -item["score"],
            -item["skill_score"],
            -item["experience_score"],
            -item["availability_score"],
            item["candidate_name"].casefold()
        )
    )

    return ranked_matches


def rank_jobs_for_candidate(candidate_id, weights=None):
    # Find the requested candidate
    candidates = get_candidates()

    candidate = next(
        (c for c in candidates if c["id"] == candidate_id),
        None
    )

    if candidate is None:
        raise ValueError(
            f"Candidate with ID {candidate_id} not found."
        )

    # Load all jobs
    jobs = get_jobs()

    ranked_matches = []

    # Score this candidate against every job
    for job in jobs:
        match = calculate_match(candidate, job, weights)

        # Skip jobs with no matching required skills
        if match is None:
            continue

        ranked_matches.append({
            "job_id": job["id"],
            "job_title": job["title"],
            **match
        })

    # Sort by score and apply tie-breakers
    ranked_matches.sort(
        key=lambda item: (
            -item["score"],
            -item["skill_score"],
            -item["experience_score"],
            -item["availability_score"],
            item["job_title"].casefold()
        )
    )

    return ranked_matches
