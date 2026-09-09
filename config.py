import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://battleship:battleship@localhost:5432/battleship")
