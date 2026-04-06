from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # Replace with the actual name of the file where the models are defined

# Step 1: Set up the database URL
# Use SQLite for local development; replace with your desired database URL if using PostgreSQL, MySQL, etc.
DATABASE_URL = "sqlite:///ai_interview_bot.db"  # This will create an SQLite database file in the current directory

# Step 2: Create the engine
engine = create_engine(DATABASE_URL)

# Step 3: Create the tables
Base.metadata.create_all(engine)

print("Database initialized and tables created!")