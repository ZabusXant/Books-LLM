from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import os
load_dotenv()

minio_url = os.getenv("MINIO_URL")
access_key = os.getenv("MINIO_USER")
secret_key = os.getenv("MINIO_PASSWORD")


class MinIO:
    minio_client: Minio

    def __init__(self):
        minio_client = Minio(minio_url, access_key=access_key, secret_key=secret_key, secure=False)

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
