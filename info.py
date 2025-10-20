from sqlalchemy import create_engine
# from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

from urllib.parse import quote_plus

USER = os.getenv("user") or "postgres"
PASSWORD = os.getenv("password") or "MFG3103@gmail"
HOST = os.getenv("host") or "db.ufnmqxyvrfionysjeiko.supabase.co"
PORT = os.getenv("port") or "5432"
DBNAME = os.getenv("dbname") or "postgres"

# Escapa caracteres especiales en la contraseña
PASSWORD_ESC = quote_plus(PASSWORD)

DATABASE_URL = f"postgresql://{USER}:{PASSWORD_ESC}@{HOST}:{PORT}/{DBNAME}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
# If using Transaction Pooler or Session Pooler, we want to ensure we disable SQLAlchemy client side pooling -
# https://docs.sqlalchemy.org/en/20/core/pooling.html#switching-pool-implementations
# engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Test the connection
try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")