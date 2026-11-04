from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import config
from core.models import Base

# SQLite configuration with thread-safety for multi-threaded Streamlit
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

SessionFactory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
ScopedSession = scoped_session(SessionFactory)

def init_db():
    """Create all tables in the SQLite database if they don't exist."""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db_session():
    """Context manager for clean database transactions."""
    session = ScopedSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_session():
    """Return a raw session instance."""
    return ScopedSession()
