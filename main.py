import logging
from dotenv import load_dotenv
load_dotenv() # Load env vars from .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Auto-initialize SQLite/PostgreSQL tables on boot
from database.connection import engine, Base
import database.models
from sqlalchemy import text

try:
    logging.info("Synching PostgreSQL application database schemas...")
    Base.metadata.create_all(bind=engine)
    logging.info("Database schemas synced successfully.")
    
    # Run self-healing schema migration
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE hardware_contexts ADD COLUMN framework VARCHAR;"))
            logging.info("Added 'framework' column to 'hardware_contexts'.")
        except Exception:
            pass # Already exists
        try:
            conn.execute(text("ALTER TABLE hardware_contexts ADD COLUMN compiler VARCHAR;"))
            logging.info("Added 'compiler' column to 'hardware_contexts'.")
        except Exception:
            pass # Already exists
        try:
            conn.execute(text("ALTER TABLE hardware_contexts ADD COLUMN board VARCHAR;"))
            logging.info("Added 'board' column to 'hardware_contexts'.")
        except Exception:
            pass # Already exists
        try:
            conn.execute(text("ALTER TABLE hardware_contexts ADD COLUMN platformio_env VARCHAR;"))
            logging.info("Added 'platformio_env' column to 'hardware_contexts'.")
        except Exception:
            pass # Already exists
except Exception as e:
    logging.error(f"Error synchronization database schemas: {e}")

# Import router
from api.routes import router

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("pinmind.main")

app = FastAPI(title="PinMind - Firmware Intelligence Workspace API")

# Configure CORS targeting Vite development server port 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)