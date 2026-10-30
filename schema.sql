CREATE TABLE IF NOT EXISTS candidates(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    skills TEXT NOT NULL,
    experience_years INTEGER NOT NULL CHECK (experience_years >= 0),
    availability TEXT NOT NULL,
    traits TEXT NOT NULL,
    quirk TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    min_experience_years INTEGER NOT NULL CHECK (min_experience_years >= 0),
    culture_keywords TEXT NOT NULL,
    tagline TEXT NOT NULL
);