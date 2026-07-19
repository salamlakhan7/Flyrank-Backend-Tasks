import os
from typing import Optional

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from celery.result import AsyncResult

from celery_app import celery_app
from tasks import ping, ai_call

app = FastAPI()

# Separate Redis connection just for tracking idempotency keys - a small,
# deliberate use of Redis as a plain key-value store, distinct from its
# job as Celery's broker/result backend.
redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379/0"), decode_responses=True
)

IDEMPOTENCY_KEY_TTL_SECONDS = 24 * 60 * 60  # keys expire after a day


class JobRequest(BaseModel):
    prompt: str
    idempotency_key: Optional[str] = None


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
    the client is never made to wait for it here.

    If an idempotency_key is provided and we've already created a job
    for it, we return that existing job instead of starting a new one -
    this is what keeps a retried request from running the AI call
    twice."""
    if job.idempotency_key:
        redis_key = f"idempotency:{job.idempotency_key}"
        existing_job_id = redis_client.get(redis_key)
        if existing_job_id:
            return {
                "job_id": existing_job_id,
                "status": "accepted",
                "idempotent_replay": True,
            }

    task = ai_call.delay(job.prompt)

    if job.idempotency_key:
        redis_key = f"idempotency:{job.idempotency_key}"
        redis_client.set(redis_key, task.id, ex=IDEMPOTENCY_KEY_TTL_SECONDS)

    return {"job_id": task.id, "status": "accepted", "idempotent_replay": False}


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