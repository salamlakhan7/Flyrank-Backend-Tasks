from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from database import create_db_and_tables, get_session, engine
from models import Task


# ---- Request/response shapes -------------------------------------------
# Separate "create" and "update" schemas so clients can never set their own id,
# and so we can validate 'title' ourselves and return exactly the 400 the spec wants.

class TaskCreate(BaseModel):
    title: Optional[str] = None
    done: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ---- Startup: create table + seed example data --------------------------

def seed_example_tasks():
    with Session(engine) as session:
        existing = session.exec(select(Task)).first()
        if existing is None:
            example_tasks = [
                Task(title="Buy milk", done=False),
                Task(title="Write report", done=True),
                Task(title="Walk the dog", done=False),
            ]
            session.add_all(example_tasks)
            session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_example_tasks()
    yield


app = FastAPI(title="Tasks API", lifespan=lifespan)


# ---- Routes ---------------------------------------------------------------

@app.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()


@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate, session: Session = Depends(get_session)):
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    task = Task(title=payload.title, done=payload.done)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        task.title = payload.title

    if payload.done is not None:
        task.done = payload.done

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted"}


# ---- Optional extras (stats endpoint) --------------------------------------

@app.get("/stats")
def get_stats(session: Session = Depends(get_session)):
    total = session.exec(select(Task)).all()
    done_count = sum(1 for t in total if t.done)
    return {
        "total": len(total),
        "done": done_count,
        "pending": len(total) - done_count,
    }