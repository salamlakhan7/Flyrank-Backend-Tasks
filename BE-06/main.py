from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from celery.result import AsyncResult

from celery_app import celery_app
from tasks import ping, ai_call

app = FastAPI()


class JobRequest(BaseModel):
    prompt: str


@app.get("/")
def read_root():
    return {"message": "Hello, FlyRank BE-06!"}


@app.get("/ping-worker")
def ping_worker():
    """Sends a trivial task to the worker and returns its task id
    immediately, without waiting for the worker to finish. This is
    the core pattern the whole assignment is built on."""
    result = ping.delay()
    return {"task_id": result.id}


@app.post("/jobs", status_code=202)
def create_job(job: JobRequest):
    """Accepts the request and returns instantly with a job id.
    The actual (slow) AI call happens separately in the worker -
    the client is never made to wait for it here."""
    task = ai_call.delay(job.prompt)
    return {"job_id": task.id, "status": "accepted"}


@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """Lets the client check back later. Celery tracks job state in
    Redis under the hood - PENDING while queued or running, SUCCESS
    with the result once done, or FAILURE if it ran out of retries."""
    result = AsyncResult(job_id, app=celery_app)

    if result.state == "PENDING":
        return {"job_id": job_id, "status": "pending"}
    elif result.state == "SUCCESS":
        return {"job_id": job_id, "status": "success", "result": result.result}
    elif result.state == "FAILURE":
        return {"job_id": job_id, "status": "failed", "error": str(result.result)}
    else:
        return {"job_id": job_id, "status": result.state.lower()}