import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.exc import DatabaseError, OperationalError

from ..core.routines import update_stuck_courses
from ..db.database import engine
from ..db.models import db_user as user_model

scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)

def init_database_with_retry(max_retries=5, delay=2):
    """Initialize database tables with retry logic to handle concurrent DDL operations."""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to create database tables (attempt {attempt + 1}/{max_retries})...")
            user_model.Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully.")
            return
        except (DatabaseError, OperationalError) as e:
            if "concurrent DDL statement" in str(e) or "being modified" in str(e):
                if attempt < max_retries - 1:
                    logger.warning(f"Database table creation failed due to concurrent operation, retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    delay *= 1.5  # Exponential backoff
                else:
                    logger.error("Failed to create database tables after all retries.")
                    raise
            else:
                logger.error(f"Database error during table creation: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error during database initialization: {str(e)}")
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle including startup and shutdown events."""
    logger.info("Starting application...")
    
    try:
        # Initialize database tables with retry logic
        init_database_with_retry()
        
        # Start scheduler
        scheduler.add_job(update_stuck_courses, 'interval', hours=1)
        scheduler.start()
        logger.info("Scheduler started.")   

        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down application...")
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler stopped.")
        logger.info("Application shutdown complete.")
