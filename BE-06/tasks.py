import os
from groq import Groq
from celery_app import celery_app


@celery_app.task(name="ping")
def ping():
    """Trivial task with no real work - just proves the worker
    picks up tasks from Redis and executes them."""
    return "pong"


@celery_app.task(name="ai_call", bind=True, max_retries=3)
def ai_call(self, prompt: str) -> str:
    """The slow operation this whole assignment is built around.
    A real Groq LLM call - genuinely slow enough (compared to a
    normal HTTP request) to justify moving it into the background
    instead of making the client wait for it.

    Wrapped with retry logic since real API calls fail sometimes
    (rate limits, timeouts, transient network errors) - jobs *will*
    fail, and this is what a job doing something about it looks like.
    Backoff doubles each attempt (2s, 4s, 8s) instead of retrying
    instantly, so a struggling API isn't hit harder while it recovers.
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(name="flaky_call", bind=True, max_retries=3)
def flaky_call(self):
    """Demo-only task: deliberately fails the first two attempts and
    succeeds on the third. The real Groq API is stable enough that we
    can't easily witness ai_call's retry logic firing on demand - this
    task exists purely to prove the same retry mechanism actually
    works, without waiting for a genuine outage."""
    if self.request.retries < 2:
        raise self.retry(
            exc=Exception(f"Simulated transient failure (attempt {self.request.retries + 1})"),
            countdown=2 ** self.request.retries,
        )
    return "Succeeded after retries"


@celery_app.task(name="always_fails", bind=True, max_retries=2)
def always_fails(self):
    """Demo-only task: fails on every attempt, with no successful
    outcome. Once it exhausts its 2 retries, this is what a job that
    genuinely can't complete looks like - and it's the case the
    task_failure signal in alerts.py is watching for."""
    raise self.retry(
        exc=Exception(f"This task always fails (attempt {self.request.retries + 1})"),
        countdown=1,
    )