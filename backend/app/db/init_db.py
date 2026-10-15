"""
AgriSense-AI: Database Schema Initialization.
Creates SQLite tables and indexes if they do not exist.
"""

import logging
from sqlalchemy import Engine
from .session import engine, Base
from . import models  # Ensures models are imported and registered on Base

logger = logging.getLogger("agrisense.init_db")

def init_db(target_engine: Engine = engine) -> None:
    """
    Initializes database tables and triggers SQLite schema setup.
    Safe to call multiple times (idempotent).
    """
    try:
        logger.info("Initializing database schema...")
        Base.metadata.create_all(bind=target_engine)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
