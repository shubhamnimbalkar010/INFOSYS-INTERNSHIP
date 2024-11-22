# config.py
class Config:
    # SQLite database URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///projects.db'  # This will use SQLite as the database engine
    SQLALCHEMY_TRACK_MODIFICATIONS = False
