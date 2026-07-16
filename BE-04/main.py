import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from repository import InMemoryRepository, PostgresRepository

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

# Same interface either way — routes below never change based on this choice.
if DATABASE_URL:
    repo = PostgresRepository(DATABASE_URL)
else:
    repo = InMemoryRepository()


class ItemIn(BaseModel):
    name: str
    description: str = ""


@app.get("/")
def read_root():
    backend = "postgres" if DATABASE_URL else "in-memory"
    return {"message": "Hello, FlyRank!", "backend": backend}


@app.post("/items")
def create_item(item: ItemIn):
    return repo.create(item.name, item.description)


@app.get("/items")
def list_items():
    return repo.get_all()


@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item