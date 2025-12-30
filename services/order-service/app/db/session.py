# app/db/session.py
"""
Session management cho PyMySQL connection
"""

from app.db.mysql_connection import MySQLConnection
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

# Global connection instance
mysql_connection = MySQLConnection()

@asynccontextmanager
async def get_db_session():
    """
    Async context manager cho database session
    """
    connection = None
    try:
        connection = await mysql_connection.get_connection()
        yield connection
    except Exception as e:
        logger.error(f"Database session error: {e}")
        if connection:
            await connection.rollback()
        raise
    finally:
        if connection:
            await mysql_connection.release_connection(connection)

# Compatibility alias
Session = get_db_session

# Dependency cho FastAPI
async def get_db():
    """
    Dependency cho FastAPI routes
    """
    async with get_db_session() as session:
        yield session