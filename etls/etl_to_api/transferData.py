from .dbHelpers import createEngine
import pandas as pd

source_db_engine = createEngine('SOURCE')
target_db_engine = createEngine('TARGET')


class SimpleDataTransfer:
    def __init__(self, source_db_engine, source_schema, source_table, target_db_engine, target_schema, target_table, mapping):
        self.source_db_engine = source_db_engine
        self.source_schema = source_schema
        self.source_table = source_table
        self.target_db_engine = target_db_engine
        self.target_schema = target_schema
        self.target_table = target_table
        self.mapping = mapping

    def getSourceData(self):
        source_data = pd.read_sql(
            f'select * from {self.source_table}', con=self.source_db_engine, schema=self.source_schema)
        return source_data

    def getTargetData(self):
        target_data = pd.read_sql(
            f'select * from {self.target_table}', con=self.target_db_engine, schema=self.target_schema)
        return target_data
