# W2 · A1 — Task API (Python / FastAPI lane)

A small in-memory CRUD API for a to-do list, built with **FastAPI**. Data lives only in a Python list — nothing is persisted, and it resets every time the server restarts (that's intentional for this stage).

## Run it

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then visit:
- API: `http://localhost:8000/`
- Interactive docs (Swagger UI): `http://localhost:8000/docs`

## Endpoints

| Method | Path | Description | Success | Errors |
|---|---|---|---|---|
| GET | `/` | API info | 200 | — |
| GET | `/health` | Health check | 200 | — |
| GET | `/tasks` | List all tasks | 200 | — |
| GET | `/tasks/{id}` | Get one task | 200 | 404 |
| POST | `/tasks` | Create a task | 201 | 400 (empty/missing title) |
| PUT | `/tasks/{id}` | Replace title/done | 200 | 400, 404 |
| DELETE | `/tasks/{id}` | Delete a task | 204 | 404 |

## Example (curl -i)

```
$ curl -i http://localhost:8000/tasks/1

HTTP/1.1 200 OK
server: uvicorn
content-length: 45
content-type: application/json

{"id":1,"title":"Buy groceries","done":false}
```

```
$ curl -i http://localhost:8000/tasks/99

HTTP/1.1 404 Not Found
content-length: 29
content-type: application/json

{"error":"Task 99 not found"}
```

## Swagger UI

Full CRUD cycle (create → get → update → delete) exercised via `/docs → Try it out`:

`Screenshots/5 swagger_ui_task_created.JPG`, `5 swagger_ui_task_get.JPG`, `5 swagger_ui_task_put.JPG`, `5 swagger_ui_task_deleted.JPG`

---

## Assessment against the assignment spec

This checks the actual "Done means" / Requirements list from the assignment PDF, not general code-quality opinions.

| Requirement | Status | Notes |
|---|---|---|
| Server starts with one documented command | ✅ | `uvicorn main:app --reload` |
| Full CRUD on in-memory list | ✅ | All 5 task endpoints work, verified via `curl` (screenshots 2–4) and Swagger (screenshot 5) |
| Correct status codes (200/201/204/400/404) | ✅ | All verified live and in screenshots |
| Errors are JSON with an `error` message | ✅ *(fixed)* | Was `{"detail": ...}`; now returns `{"error": ...}` per spec — see changelog below |
| POST/PUT validate empty/missing title → 400 | ✅ | Confirmed in `3 create_with_validation.JPG` for both `{}` and `{"title":""}` |
| Swagger UI works, full CRUD via "Try it out" | ✅ | Screenshots 5 (create/get/put/delete) — **note:** screenshots still show the old `{"detail":...}` shape since they predate this fix; retake if resubmitting |
| Public GitHub repo, ≥6 commits, one per stage | ⚠️ | Commits exist for Stage 0–4 individually, plus one unlabeled commit adding the Swagger + browser screenshots. There's no commit explicitly named `Stage 5: Swagger UI` or `Stage 6: publish and docs`, and — until this file — **no README existed for this folder at all**, which Stage 6 requires |
| README: what/how-to-run/endpoint table/curl output/Swagger screenshot | ✅ (now) | This file. It didn't exist before. |

### Fixed in this pass

`main.py` was updated to close the one real spec gap:

```python
# before — FastAPI's default HTTPException shape
raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# after — matches the spec's { "error": "..." } requirement
return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
```

Applied to all three error sites (404 on GET/PUT/DELETE, 400 on POST/PUT). Also switched the `DELETE` handler to `Response(status_code=204)` instead of an implicit `None` return, so the 204 body is truly empty rather than serialized as `null`. And `title.strip()` is now applied before saving, so `"  Buy milk  "` is stored as `"Buy milk"` instead of keeping the whitespace.

Re-verified against every Stage 2–4 checkpoint in the spec (`curl -i` for 200/404/400/201/200/204) — all pass with the new response shape.

**Action needed:** the existing screenshots in `Screenshots/` were taken before this fix and still show `{"detail":...}`. If resubmitting, retake `2`, `3`, `4`, and the `5 swagger_ui_*` screenshots so they match the corrected code.

### Screenshot that doesn't belong in this folder

`5 browser_test_port_8000.JPG` shows `{"message":"Hello, FlyRank!","backend":"postgres"}`. This app has no such route and no Postgres dependency — it's a screenshot from a different assignment in the same repo (BE‑01/BE‑04, per the root README's Postgres/containerization description), likely copied in by mistake. Suggest replacing it with an actual browser screenshot of `http://localhost:8000/tasks` or `/docs` for this assignment.

### Not attempted (all optional, per spec)

- ★ Extras: query-param filtering (`?done=true`), search, `/stats`, `/reset`, the "mortality experiment" writeup.
- Stretch: pagination (`?limit=&offset=`).
- Stage 7 bonus: the "AI vs me" rematch section.

None of these are required for a passing submission — flagging only so it's clear they were skipped rather than missed.

## Recommendations, in priority order

1. ~~Fix the error response shape~~ — **done** in this pass (`error` key, trimmed titles, true-empty 204 body).
2. **Retake screenshots 2, 3, 4, and 5** so they reflect the corrected `{"error": ...}` responses — the current images in `Screenshots/` still show the old `{"detail": ...}` shape.
3. ~~Add the missing README~~ — **done**; commit it as `Stage 6: publish and docs`.
4. **Remove or replace the stray Postgres screenshot** so every image in the folder is actually evidence of this project.
5. **Add explicit `Stage 5` / `Stage 6` commits** so `git log` reads as one commit per stage, per the assignment's own commit convention.
6. *(Optional, for extra credit)* Pick one ★ extra — `/stats` or `/reset` are the fastest to add — and note the "mortality experiment" observation, since that's the one extra the assignment calls out as conceptually important (it's the seed for Week 3).
