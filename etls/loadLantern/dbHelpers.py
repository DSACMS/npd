import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


def createEngine(source_or_target):
    # Get database details and create engine
    load_dotenv()
    username = os.getenv(f'{source_or_target}_DB_USER')
    password = os.getenv(f'{source_or_target}_DB_PASSWORD')
    instance = os.getenv(f'{source_or_target}_DB_HOST')
    db = os.getenv(f'{source_or_target}_DB_NAME')
    port = os.getenv(f'{source_or_target}_DB_PORT')
    engine = create_engine(
        f"postgresql+psycopg2://{username}:{password}@{instance}:{port}/{db}")
    return engine
