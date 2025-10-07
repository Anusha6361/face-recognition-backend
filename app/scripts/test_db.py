# scripts/test_db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found. Did you create the .env file?")
else:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("✅ Connection successful!")
    except Exception as e:
        print("❌ Connection failed:", e)
