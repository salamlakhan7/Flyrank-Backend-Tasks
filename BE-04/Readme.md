# BE-04 — Containerize your stack

Postgres running in Docker, connected to the app via a repository that
implements the exact same interface as the original in-memory store.
Swapping backends means changing one environment variable — no route
or service code changes.

## Architecture

- `repository.py` — `ItemRepository` interface, `InMemoryRepository`
  (the original A2-style store), and `PostgresRepository` (BE-04's
  required backend). Both implement `create`, `get_all`, `get_by_id`.
- `main.py` — picks `PostgresRepository` if `DATABASE_URL` is set,
  otherwise falls back to `InMemoryRepository`. Routes never branch on
  which backend is active.
- `docker-compose.yml` — starts Postgres (with a named volume) and the
  app together with one command.
- `init.sql` — creates the `items` table on first Postgres startup.

## Run (tested on Play with Docker — no local install needed)

```bash
git clone https://github.com/salamlakhan7/Flyrank-Backend-Tasks.git
cd Flyrank-Backend-Tasks/BE-04
docker compose up
```

App available at `http://localhost:8000` (or the PWD-forwarded port).

## Test

```bash
curl -X POST http://localhost:8000/items -H "Content-Type: application/json" -d '{"name":"first item","description":"testing persistence"}'
curl http://localhost:8000/items
```

## Proof of persistence

1. Ran `docker compose up`, created two items via the POST endpoint above.
2. Confirmed both rows returned from `GET /items`.
3. Restarted just the app container: `docker compose restart app`
   (data survives because it lives in Postgres, not app memory).
4. Restarted the whole stack: `docker compose down` then
   `docker compose up` again — rows still returned by `GET /items`
   because `pgdata` is a named Docker volume, not container-local storage.

Screenshots of each step are in `Screenshots/`.

## Notes

- `.env` is gitignored; `.env.example` is committed as the template.
- Connection string points at the `db` service name (Docker's internal
  DNS), not `localhost` — required since app and db run in separate
  containers on the same compose network.