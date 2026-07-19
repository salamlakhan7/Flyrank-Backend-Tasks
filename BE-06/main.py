from fastapi import FastAPI
from pydantic import BaseModel

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