--Question 1:Job postings that are open with recruiter names
SELECT
    jp.id AS job_id,
    jp.title AS job_title,
    r.name AS recruiter_name
FROM job_postings AS jp
INNER JOIN recruiters AS r
    ON jp.recruiter_id = r.id
WHERE jp.status = 'open'
ORDER BY jp.id;

--Question 2: For each job posting, count applicants who reached Final stage.
SELECT
    jp.id AS job_id,
    jp.title AS job_title,
    COUNT(DISTINCT i.applicant_id) AS final_stage_applicants
FROM job_postings AS jp
LEFT JOIN interviews AS i
    ON i.job_posting_id = jp.id
    AND i.stage = 'Final'
GROUP BY jp.id, jp.title
ORDER BY jp.id;

--Question 3: Applicants who have applied to more than one job posting
SELECT
    MIN(a.full_name) AS person_name,
    LOWER(TRIM(a.email)) AS normalized_email,
    COUNT(DISTINCT i.job_posting_id) AS distinct_job_postings
FROM applicants AS a
INNER JOIN interviews AS i
    ON a.id = i.applicant_id
WHERE a.email IS NOT NULL
GROUP BY LOWER(TRIM(a.email)) 
HAVING COUNT(DISTINCT i.job_posting_id) > 1
ORDER BY normalized_email;

--Question 4: Final-stage conversion rate per recruiter, requiring at least 3 finals.
SELECT
    r.id AS recruiter_id,
    r.name AS recruiter_name,
    COUNT(i.id) AS total_final_interviews,
    SUM(
        CASE
            WHEN i.outcome = 'passed' THEN 1
            ELSE 0
        END
    ) AS passed_final_interviews,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN i.outcome = 'passed' THEN 1
                ELSE 0
            END
        ) / COUNT(i.id),
        2
    ) AS conversion_rate_percent
FROM recruiters AS r
INNER JOIN job_postings AS jp
    ON r.id = jp.recruiter_id
INNER JOIN interviews AS i
    ON jp.id = i.job_posting_id
    AND i.stage = 'Final'
GROUP BY r.id, r.name
HAVING COUNT(i.id) >= 3
ORDER BY conversion_rate_percent DESC;

--Question 5: Window function to rank recruiters by most successful placements per department
WITH recruiter_placements AS (
SELECT
    jp.department,
    r.id AS recruiter_id,
    r.name AS recruiter_name,
    COUNT(i.id) AS successful_placements
FROM recruiters AS r
INNER JOIN job_postings AS jp
    ON r.id = jp.recruiter_id
LEFT JOIN interviews AS i
    ON jp.id = i.job_posting_id
    AND i.stage = 'Final'
    AND i.outcome = 'passed'
GROUP BY jp.department, r.id, r.name),

ranked_placements AS (
    SELECT
        department,
        recruiter_id,
        recruiter_name,
        successful_placements,
        RANK() OVER (
            PARTITION BY department
            ORDER BY successful_placements DESC
        ) AS placement_rank
    FROM recruiter_placements
)
SELECT
    department,
    recruiter_name,
    successful_placements
FROM ranked_placements
WHERE placement_rank = 1
ORDER BY department;