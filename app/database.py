from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
from .config import settings

db_host = settings.db_host
db_port = settings.db_port
db_user = settings.db_user
db_password = settings.db_password
db_name = settings.db_name

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create SQLAlchemy session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create SQLAlchemy base class
Base = declarative_base()


# dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ANOTHER WAY TO CONNECT TO THE DATABASE USING THE PSYCOPG DRIVER
# import psycopg
# import time

# Database Connection
# Connect to the database using the psycopg library
# while True:
#     try:
#         conn = psycopg.connect(
#             host=db_host,
#             port=db_port,
#             user=db_user,
#             password=db_password,
#             dbname="fastapi",
#             row_factory=psycopg.rows.dict_row,
#         )
#         print("Connected to the database")
#         cursor = conn.cursor()
#         break
#     except Exception as e:
#         print("Error: ", e)
#         print("Retrying in 5 seconds")
#         time.sleep(5)
