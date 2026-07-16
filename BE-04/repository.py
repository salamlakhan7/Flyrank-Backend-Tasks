from abc import ABC, abstractmethod
from typing import Optional
import psycopg2
import psycopg2.extras


class ItemRepository(ABC):
    """Common interface. Both storage backends implement this exactly,
    so main.py never needs to know which one is running underneath."""

    @abstractmethod
    def create(self, name: str, description: str) -> dict:
        ...

    @abstractmethod
    def get_all(self) -> list[dict]:
        ...

    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[dict]:
        ...


class InMemoryRepository(ItemRepository):
    """Original A2-style store. Data lives only in process memory —
    lost on every restart. Kept here to show the exact interface
    the Postgres repository below had to match."""

    def __init__(self):
        self._items: dict[int, dict] = {}
        self._next_id = 1

    def create(self, name: str, description: str) -> dict:
        item = {"id": self._next_id, "name": name, "description": description}
        self._items[self._next_id] = item
        self._next_id += 1
        return item

    def get_all(self) -> list[dict]:
        return list(self._items.values())

    def get_by_id(self, item_id: int) -> Optional[dict]:
        return self._items.get(item_id)


class PostgresRepository(ItemRepository):
    """Real backend for BE-04. Same interface as InMemoryRepository above —
    main.py swaps between them with zero changes to routes or service logic."""

    def __init__(self, database_url: str):
        self.database_url = database_url

    def _connect(self):
        return psycopg2.connect(self.database_url)

    def create(self, name: str, description: str) -> dict:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id, name, description;",
                    (name, description),
                )
                row = cur.fetchone()
                conn.commit()
                return dict(row)

    def get_all(self) -> list[dict]:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, name, description FROM items ORDER BY id;")
                return [dict(row) for row in cur.fetchall()]

    def get_by_id(self, item_id: int) -> Optional[dict]:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, name, description FROM items WHERE id = %s;",
                    (item_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None