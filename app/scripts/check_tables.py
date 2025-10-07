# scripts/check_tables.py
from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("Tables in DB:", inspector.get_table_names())
