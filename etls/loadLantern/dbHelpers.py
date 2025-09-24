import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


def createEngine():
    # Get database details and create engine
    load_dotenv()
    username = os.getenv('NPD_DB_USER')
    password = os.getenv('NPD_DB_PASSWORD')
    instance = os.getenv('NPD_DB_HOST')
    db = os.getenv('NPD_DB_NAME')
    port = os.getenv('NPD_DB_PORT')
    engine = create_engine(
        f"postgresql+psycopg2://{username}:{password}@{instance}:{port}/{db}")
    return engine
