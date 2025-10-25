from src.utils.s3_manager import S3Manager
from src.utils.s3_client import S3Client

s3_client = S3Client()
s3_manager = S3Manager(s3_client=s3_client)