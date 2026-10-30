from fastapi import FastAPI , HTTPException
from matching import rank_candidates_for_job , rank_jobs_for_candidate
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the recruitor-bot"}

@app.get("/job/{job_id}/matches")
def get_job_matches(job_id: int):
    try:
        matches = rank_candidates_for_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"job_id": job_id, "matches": matches}

@app.get("/candidate/{candidate_id}/matches")
def get_candidate_matches(candidate_id: int):
    try:
        matches = rank_jobs_for_candidate(candidate_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"candidate_id": candidate_id, "matches": matches}
