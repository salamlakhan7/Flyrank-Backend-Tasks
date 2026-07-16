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

## Run (tested on GitHub Codespaces — no local install needed)

```bash
git clone https://github.com/salamlakhan7/Flyrank-Backend-Tasks.git
cd Flyrank-Backend-Tasks/BE-04
docker compose up
```

App available at `http://localhost:8000`.

## Test

```bash
curl -X POST http://localhost:8000/items -H "Content-Type: application/json" -d '{"name":"first item","description":"testing persistence"}'
curl http://localhost:8000/items
```

## Proof of persistence

1. Ran `docker compose up` — Postgres and the app started together.

   ![Compose up: docker and postgres starting together](./Screenshots/4%20Compose%20up%28docker%2Bpostgres%29.JPG)

2. Created two items via the POST endpoint, confirmed both returned by `GET /items`.

   ![Both items created and listed](./Screenshots/1%20items_1st_2nd_item.JPG)

3. Restarted just the app container (`docker compose restart app`) — data survived because it lives in Postgres, not app memory.

   ![Items still present after app-only restart](./Screenshots/2%20fter_app_restart.JPG)

4. Restarted the whole stack (`docker compose down` then `docker compose up`) — Postgres logged "database directory appears to contain a database, skipping initialization," and `GET /items` still returned both items, proving the named volume (`pgdata`) survived the containers being fully destroyed and recreated.

   ![Items still present after full stack restart](./Screenshots/3%20docker_compose_restart_app.JPG)

5. Confirmed the root endpoint also works from a browser, via the Codespaces-forwarded port 8000 URL, not just curl.

   ![Root endpoint tested in browser on port 8000](./Screenshots/5%20browser_test_port_8000.JPG)

## Notes

- `.env` is gitignored; `.env.example` is committed as the template.
- Connection string points at the `db` service name (Docker's internal
  DNS), not `localhost` — required since app and db run in separate
  containers on the same compose network.