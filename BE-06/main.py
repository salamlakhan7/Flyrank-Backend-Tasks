from fastapi import FastAPI

from tasks import ping

app = FastAPI()


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