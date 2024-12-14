from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
print("DAG parsing sys.path", sys.path)
sys.path.append('/opt/airflow/src')

from data_mining.html_scraper import HTML_Scraper
from data_processing.data_transformation import Transformer

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def scrape_data():
    scraper = HTML_Scraper()
    scraper.run_crawler()


def clean_data():
    transformer = Transformer()
    transformer.run_transformer()


with DAG(
        dag_id='html_crawler_pipeline',
        default_args=default_args,
        description='Running the HTML crawler and uploading to MinIO and PostgreSQL',
        schedule_interval=None,  # Trigger manually
        start_date=datetime(2023, 1, 1),
        catchup=False,
        tags=['mining', 'minio', 'postgres'],
) as dag:
    crawling_task = PythonOperator(
        task_id='run_crawler',
        python_callable=scrape_data
    )

    cleaning_task = PythonOperator(
        task_id='clean_and_upload_data',
        python_callable=clean_data()
    )

    crawling_task >> cleaning_task
