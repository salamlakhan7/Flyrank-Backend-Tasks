# BE-06 — Your First Background Job

A slow operation (a real Groq LLM call, standing in for A6's AI call)
moved out of the request path and into a background job. The endpoint
answers instantly with `202 Accepted`, a Celery worker does the actual
work, and a status endpoint reports the result once it's ready.

## The pattern

The professional pattern for anything slow: accept fast, work in the
background, report status.

- **Accept fast** — `POST /jobs` never waits for the AI call. It hands
  the work to Celery and returns a `job_id` immediately.
- **Work in the background** — a separate Celery worker container picks
  the job up from Redis and does the actual (slow) work.
- **Report status** — `GET /jobs/{job_id}` lets the client check back
  later: pending, running, succeeded (with the result), or failed.

## Architecture

- `main.py` — FastAPI app: `POST /jobs` and `GET /jobs/{job_id}`.
- `celery_app.py` — Celery configuration, using Redis as both the
  message broker and the result backend.
- `tasks.py` — `ai_call` (the real Groq task), plus two demo-only tasks
  (`flaky_call`, `always_fails`) used purely to prove the retry and
  alert logic actually fires, since the real Groq API is stable enough
  that it won't fail on demand for testing.
- `alerts.py` — a Celery signal handler that logs a clear `ALERT` line
  the moment any task fails permanently, after exhausting all retries.
- `docker-compose.yml` — three services: `redis`, `app` (FastAPI), and
  `worker` (Celery), all wired together with one command.

## The three non-negotiables

**Jobs will run twice (idempotency).** If a client retries the same
submission (network blip, duplicate click), `POST /jobs` accepts an
optional `idempotency_key`. If that key has been seen before, the
existing `job_id` is returned instead of starting a second Groq call —
proven by submitting the same key twice and getting back the same
`job_id`, with the second response marked `idempotent_replay: true`.

**Jobs will fail (retries).** `ai_call` is wrapped with retry logic:
up to 3 attempts, with exponential backoff (2s, 4s, 8s) between them,
so a struggling API isn't hit harder while it's recovering. Proven with
`flaky_call`, a demo task that deliberately fails twice before
succeeding on the third attempt.

**Someone must find out (alerts).** A `task_failure` signal handler in
`alerts.py` logs a loud, clearly-labeled `ALERT:` line at `ERROR` level
the moment a job exhausts every retry and fails for good — so a failed
job never just sits quietly in Redis waiting to be noticed. Proven with
`always_fails`, a demo task that never succeeds, showing the alert fire
right after its final retry is exhausted.

## Run

```bash
docker compose up --build
```

Requires a `.env` file (gitignored) with:
```
GROQ_API_KEY=your_real_key_here
REDIS_URL=redis://redis:6379/0
```

## Test the core flow

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a haiku about backend engineering"}'

curl http://localhost:8000/jobs/<job_id_from_above>
```

## Test idempotency

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Say hello in 3 words","idempotency_key":"test-key-1"}'

# run the exact same request again - same job_id comes back both times
```

## Screenshots

1. Worker, app, and Redis all start together and correctly discover the `ping` task.

   ![Worker pipeline confirmed](./Screenshots/0%20worker_pipeline_confirmed.JPG)

2. The API responds instantly with a task id, before any real work has happened.

   ![API responded instantly with a task id](./Screenshots/1%20API%20responded%20instantly%20with%20a%20task%20id.JPG)

3. The real Groq call runs end-to-end through Celery for the first time.

   ![Groq call works end-to-end through Celery](./Screenshots/2%20Grok_responded_%26_call%20genuinely%20works%20end-to-end%20through%20Celery.JPG)

4. A direct test confirming Groq's actual response content comes back correctly.

   ![Groq succeeded with a real response](./Screenshots/3%20Grok_succeeded%20in_Hello%2C%20it%20is%20very%20nice.JPG)

5. `time curl` proof: the `POST /jobs` response comes back in ~0.1s while the Groq call itself takes far longer in the background.

   ![Instant 202 response](./Screenshots/4%20instant_202_response.JPG)

6. The status endpoint correctly reports `success` with the actual result once the job finishes.

   ![Status endpoint](./Screenshots/5%20status_endpoint.JPG)

7. Submitting the same idempotency key twice returns the same job id both times.

   ![Idempotency](./Screenshots/6%20idempotency.JPG)

8. `flaky_call` failing twice, backing off, then succeeding on the third attempt.

   ![Retry with backoff](./Screenshots/7%20retry_backoff.JPG)

9. `always_fails` exhausting its retries, triggering the `ALERT:` log line.

   ![Alert on permanent failure](./Screenshots/8%20alert_on_failure.JPG)

## Notes

- `flaky_call` and `always_fails` are demo-only tasks, not part of the
  real API surface - they exist purely because the actual Groq API is
  reliable enough that its retry/failure paths can't be reliably
  witnessed on demand during testing.
- Redis's port is intentionally **not** exposed to the host in
  `docker-compose.yml`. Only the `app` and `worker` containers need to
  reach it, over Docker's internal network - an earlier test with the
  port exposed publicly on Codespaces attracted an automated scan
  attempt against Redis within seconds, which is what a real "polite
  by default" infrastructure choice looks like in practice.
- The Celery worker currently runs as root inside its container
  (visible as a startup warning). That's acceptable for this practice
  environment but would need a dedicated non-root user in a real
  production deployment.