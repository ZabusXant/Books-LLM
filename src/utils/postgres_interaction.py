import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')


class Database:
    engine: Engine

    def __init__(self):
        self.engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')

    def upload_df_to_table(self, table_name: str, data: pd.DataFrame):
        data.to_sql(table_name, self.engine, if_exists='replace', index=False)
        print("Data has been loaded into table", table_name, "successfully")
