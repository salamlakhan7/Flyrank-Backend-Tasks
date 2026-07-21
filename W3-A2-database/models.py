from typing import Optional
from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """
    Maps directly to the 'tasks' table in tasks.db.
    Columns: id (primary key), title (text), done (boolean).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    done: bool = False