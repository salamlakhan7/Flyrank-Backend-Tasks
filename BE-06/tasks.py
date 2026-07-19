from celery_app import celery_app


@celery_app.task(name="ping")
def ping():
    """Trivial task with no real work - just proves the worker
    picks up tasks from Redis and executes them."""
    return "pong"