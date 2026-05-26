import os
from dotenv import load_dotenv
import boto3
from langchain_aws import ChatBedrock

load_dotenv()


class Settings:
    def __init__(self):
        # DB connection
        self.db_port     = os.getenv("DB_PORT","5432")
        self.db_host     = os.getenv("DB_HOST","localhost")
        self.db_name     = os.getenv("DB_NAME")
        self.db_username = os.getenv("DB_USERNAME", "postgres")
        self.db_password = os.getenv("DB_PASSWORD", "Admin123")

        # aws service
        self.region = os.getenv("REGION")
        self.model_id=os.getenv("MODEL_ID")
        self.provider=os.getenv("PROVIDER")
        self.aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
settings = Settings()
