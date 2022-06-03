# Import MinIO library.
from dotenv import load_dotenv
from minio import Minio
import os

load_dotenv()

access_key = os.getenv("MINIO_SERVER_ACCESS_KEY")
secret_key = os.getenv("MINIO_SERVER_SECRET_KEY")

# Initialize minioClient with an endpoint and access/secret keys.
minioClient = Minio(
    "minio:9000", access_key=access_key, secret_key=secret_key, secure=False,
)
