import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')
table_name = 'cleaned_data'

filepath = "../data/processed_data.csv"

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')
data = pd.read_csv(filepath, dtype='str', sep='^', encoding='utf-8')
data.to_sql(table_name, engine, if_exists='replace', index=False)

print("Processed data has been loaded into table cleaned_data successfully")
