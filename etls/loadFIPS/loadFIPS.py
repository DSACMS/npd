import requests
import os
import time
import pandas as pd
import logging

from typing import Optional
from io import StringIO
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FIPSCountyETL:
    def __init__(self, table_name: str = "fips_county"):
        self.table_name = table_name
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))

    def handle_request(self, url: str) -> Optional[requests.Response]:
        for attempt in range(self.max_retries):
            try:
                # important to note that we get responses back as .txt and not .json
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                return response
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    logger.error(f"404 Error for URL: {url}")
            except requests.Timeout as e:
                logger.error(
                    f"Timeout error has occured after waiting 30 seconds.")
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to fetch after 3 attempts: {e}")
                    return None
                else:
                    sleep = 2 ** attempt
                    logger.warning(
                        f"Attempt {attempt} failed so retrying in {sleep} seconds.")

                    time.sleep(sleep)
            except Exception as e:
                logger.error(
                    f"Something went wrong with handling a request: {e}")
                raise
        return None

    def validate_data(self, df: pd.DataFrame) -> None:
        required_columns = ["STATEFP", "COUNTYFP", "COUNTYNAME"]
        STATEFP_regex = r'^\d{2}$'
        COUNTYFP_regex = r'^\d{3}$'

        for column in required_columns:
            if column not in df.columns:
                raise ValueError(f"Missing required column: {column}")

        if df.empty:
            raise ValueError("DataFrame is empty!")
        if not df["STATEFP"].str.match(STATEFP_regex).all():
            raise ValueError("STATEFP should be a 2 digit code")
        if not df["COUNTYFP"].str.match(COUNTYFP_regex).all():
            raise ValueError("COUNTYFP should be a 3 digit code")

    def extract(self) -> str:
        url = "https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt"

        response = self.handle_request(url)
        raw_data = response.text

        logger.info("Phase 1 - Extraction has finished")
        return raw_data

    def transform(self) -> pd.DataFrame:
        raw_data = self.extract()

        try:
            df = pd.read_csv(StringIO(raw_data), delimiter="|", dtype=str)

            self.validate_data(df)

            df = df[["STATEFP", "COUNTYFP", "COUNTYNAME"]].copy()

            df["id"] = df["STATEFP"] + df["COUNTYFP"]
            df["name"] = df["COUNTYNAME"]
            df["fips_state_id"] = df["STATEFP"]

            df = df[["id", "name", "fips_state_id"]].drop_duplicates()

        except Exception as e:
            logger.error(
                f"Something went wrong transforming the raw data: {e}")
            raise

        logger.info("Phase 2 - Transformation has finished")
        # df.to_csv("output.csv", index=False)

        return df

    def load(self):
        transformed_data = self.transform()

        connection_string = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
            f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

        engine = create_engine(connection_string)

        try:
            with engine.begin() as con:
                transformed_data.to_sql(
                    name=self.table_name,
                    con=con,
                    if_exists="append",
                    index=False,
                    method="multi",
                    schema='npd'
                )

            logger.info("Phase 3 - Loading has finished")
            logger.info(
                f"  Successfully loaded {len(transformed_data)} records to {self.table_name} table!")

        except Exception as e:
            logger.error(
                f"Something went wrong loading the transformed data: {e}")
            raise
        finally:
            engine.dispose()

    def run_pipeline(self):
        try:
            logger.info("Starting FIPS County ETL pipeline!")
            self.load()
            logger.info("Pipeline completed successfully!")

        except Exception as e:
            logger.error(f"Something went wrong with the pipeline: {e}")
            raise


def main():
    pipeline = FIPSCountyETL()
    pipeline.run_pipeline()


if __name__ == "__main__":
    main()
