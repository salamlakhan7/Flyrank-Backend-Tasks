import os
from groq import Groq
from celery_app import celery_app


@celery_app.task(name="ping")
def ping():
    """Trivial task with no real work - just proves the worker
    picks up tasks from Redis and executes them."""
    return "pong"


@celery_app.task(name="ai_call")
def ai_call(prompt: str) -> str:
    """The slow operation this whole assignment is built around.
    A real Groq LLM call - genuinely slow enough (compared to a
    normal HTTP request) to justify moving it into the background
    instead of making the client wait for it."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content