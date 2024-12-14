from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
import os

load_dotenv()

minio_url = os.getenv("MINIO_URL")
access_key = os.getenv("MINIO_USER")
secret_key = os.getenv("MINIO_PASSWORD")


class MinIO:
    minio_client: Minio

    def __init__(self):
        print(f"Connecting to MinIO with {minio_url} as url and {access_key} as user with password {secret_key}")
        self.minio_client = Minio(minio_url, access_key=access_key, secret_key=secret_key, secure=False)

    def create_bucket(self, bucket_name: str):
        try:
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)
                print("Bucket", bucket_name, "created successfully")
            else:
                print("Bucket", bucket_name, "already exists")
        except S3Error as e:
            print(f"An error occurred: {e}")

    def upload_file_to_minio(self, bucket: str, file_name: str, file_path: str):
        try:
            if not self.minio_client.bucket_exists(bucket):
                self.create_bucket(bucket)
            self.minio_client.fput_object(bucket, file_name, file_path)
            print("File", file_name, "uploaded to bucket", bucket, "successfully")
        except S3Error as e:
            print(f"An error occurred: {e}")

    def upload_df_to_minio(self, bucket: str, file_name: str, df: pd.DataFrame):
        try:
            if not self.minio_client.bucket_exists(bucket):
                self.create_bucket(bucket)

            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False, sep='^', encoding='utf-8')
            csv_buffer.seek(0)
            self.minio_client.put_object(bucket_name=bucket, object_name=file_name, data=csv_buffer,
                                         length=len(csv_buffer.getvalue()), content_type="text/csv")
            print("File", file_name, "created from dataframe uploaded to bucket", bucket, "successfully")
        except S3Error as e:
            print(f"An error occurred: {e}")

    def download_csv_file_from_minio(self, bucket: str, file_name: str):
        try:
            response = self.minio_client.get_object(bucket_name=bucket, object_name=file_name)
            csv_data = BytesIO(response.read())

            return csv_data
        except S3Error as e:
            print(f"An error occurred: {e}")
