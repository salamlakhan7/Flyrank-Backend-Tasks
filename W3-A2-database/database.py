from sqlmodel import SQLModel, create_engine, Session

# SQLite file — created automatically on first run, in the project's working directory
DATABASE_URL = "sqlite:///tasks.db"

# check_same_thread=False is required for SQLite when used with FastAPI,
# since FastAPI can handle requests on different threads.
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables():
    """Creates the tasks table if it doesn't already exist. Safe to call every startup."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency — yields a DB session per request, closes it automatically after."""
    with Session(engine) as session:
        yield session