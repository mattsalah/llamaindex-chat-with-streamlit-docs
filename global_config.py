import os, boto3
from loguru import logger
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


class ConfigENV():
    global running_on, aws_region, access_key, secret_key
    
    running_on = os.getenv("ENVIRONMENT")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    SSM_ENV = os.getenv("SSM_ENV")
    secret_key = os.getenv("ACCESS_SECRET")
    access_key = os.getenv("ACCESS_KEY")

    logger.info(f"running on: {running_on}")
    logger.info(f"SSM ENV: {SSM_ENV}")
            
    if running_on == "SERVER":
            
        ssm_client = boto3.client("ssm", region_name=aws_region)
        s3_client = boto3.client("s3", region_name=aws_region)

        DB_HOST = ssm_client.get_parameter(Name=f"/{SSM_ENV}/DB_ENDPOINT", WithDecryption=True)["Parameter"]["Value"]
        DB_NAME = ssm_client.get_parameter(Name=f"/{SSM_ENV}/DATABASE", WithDecryption=True)["Parameter"]["Value"]
        DB_PASS = ssm_client.get_parameter(Name=f"/{SSM_ENV}/DB_PASS", WithDecryption=True)["Parameter"]["Value"]
        DB_USER = ssm_client.get_parameter(Name=f"/{SSM_ENV}/DB_USER_NAME_PYTHON", WithDecryption=True)["Parameter"]["Value"]
        DB_PORT = ssm_client.get_parameter(Name=f"/{SSM_ENV}/DB_PORT", WithDecryption=True)["Parameter"]["Value"]
        EXIST_COMMUNICATION_SERVICE = ssm_client.get_parameter(Name=f"/{SSM_ENV}/EXIST_COMMUNICATION_SERVICE", WithDecryption=True)["Parameter"]["Value"]
        EXIST_AUTH_USER = ssm_client.get_parameter(Name=f"/{SSM_ENV}/EXIST_AUTH_USER", WithDecryption=True)["Parameter"]["Value"]
        EXIST_AUTH_SECRET = ssm_client.get_parameter(Name=f"/{SSM_ENV}/EXIST_AUTH_SECRET", WithDecryption=True)["Parameter"]["Value"]
        REFDATA_URL = ssm_client.get_parameter(Name=f"/{SSM_ENV}/REFDATA_URL", WithDecryption=True)["Parameter"]["Value"]
        S3_BUCKET = ssm_client.get_parameter(Name=f"/{SSM_ENV}/S3_BUCKET", WithDecryption=True)["Parameter"]["Value"]
        USERNAME = ssm_client.get_parameter(Name=f"/{SSM_ENV}/USERNAME", WithDecryption=True)["Parameter"]["Value"]
        AES_SALT = ssm_client.get_parameter(Name=f"/{SSM_ENV}/AES_SALT", WithDecryption=True)["Parameter"]["Value"]
        AWS_STORAGE_BUCKET_NAME = ssm_client.get_parameter(Name=f"/{SSM_ENV}/AWS_STORAGE_BUCKET_NAME", WithDecryption=True)["Parameter"]["Value"]
        
        REDIS_HOST = ssm_client.get_parameter(Name=f"/{SSM_ENV}/REDIS_HOST", WithDecryption=True)["Parameter"]["Value"]
        REDIS_PORT = ssm_client.get_parameter(Name=f"/{SSM_ENV}/REDIS_PORT", WithDecryption=True)["Parameter"]["Value"]
        S3_BUCKET_PRODUCION = ssm_client.get_parameter(Name=f"/{SSM_ENV}/PROD_S3_BUCKET", WithDecryption=True)["Parameter"]["Value"]
        NOTIFICATION_SERVICE = ssm_client.get_parameter(Name=f"/{SSM_ENV}/NOTIFICATION_SERVICE", WithDecryption=True)["Parameter"]["Value"]
        SHIPMENT_EMAILS = ssm_client.get_parameter(Name=f"/{SSM_ENV}/SHIPMENT_EMAILS", WithDecryption=True)["Parameter"]["Value"]
        PYTHON_USER_EMAILS = ssm_client.get_parameter(Name=f"/{SSM_ENV}/PYTHON_USER_EMAILS", WithDecryption=True)["Parameter"]["Value"]

    else:
        session = boto3.Session(
            aws_access_key_id=os.getenv("ACCESS_KEY"),
            aws_secret_access_key=os.getenv("ACCESS_SECRET"),
            region_name= aws_region
        )

        ssm_client = session.client("ssm")
        s3_client = session.client("s3")

        DB_HOST = os.getenv("DB_ENDPOINT")
        DB_NAME = os.getenv("DATABASE")
        DB_PASS = os.getenv("DB_PASS")
        DB_USER = os.getenv("DB_USER_NAME_PYTHON")
        DB_PORT = os.getenv("DB_PORT", 5432)
        EXIST_COMM_SERVICE_URL = os.getenv('EXIST_COMM_SERVICE_URL')
        EXIST_AUTH_USER = os.getenv('EXIST_AUTH_USER')
        EXIST_AUTH_SECRET = os.getenv('EXIST_AUTH_SECRET')
        EXIST_GET_DOC_URL = EXIST_COMM_SERVICE_URL+"/documents"+"?user="+EXIST_AUTH_USER+"=&secret="+EXIST_AUTH_SECRET+"&documentPath="
        REFDATA_GAZETTEER_URL = os.getenv("REFDATA_GAZETTEER_URL", "http://localhost:8182/refdata/gazetteer")
        S3_BUCKET = os.getenv("S3_BUCKET")
        USERNAME = os.getenv('USERNAME',"internal@infraclear.com")
        AES_SALT = os.getenv('AES_SALT')
        AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
        GPT4_COST_PER_INPUT_TOKEN = float(os.getenv("GPT-4_COST_PER_INPUT_TOKEN"))
        GPT4_COST_PER_OUTPUT_TOKEN = float(os.getenv("GPT-4_COST_PER_OUTPUT_TOKEN"))
        GPT3_COST_PER_INPUT_TOKEN = float(os.getenv("GPT-3.5_COST_PER_INPUT_TOKEN"))
        GPT3_COST_PER_OUTPUT_TOKEN = float(os.getenv("GPT-3.5_COST_PER_OUTPUT_TOKEN"))
        ELASTIC_USER = os.getenv('ELASTIC_USER')
        ELASTIC_ENV = os.getenv('ELASTIC_ENV')
        ELASTIC_PW = os.getenv('ELASTIC_PW')
        ELASTIC_FINGERPRINT = os.getenv('ELASTIC_FINGERPRINT')
        ELASTIC_API_KEY = os.getenv('ELASTIC_API_KEY')
        ELASTIC_API_KEY_ID = os.getenv('ELASTIC_API_KEY_ID')
        ES_ENDPOINT = os.getenv('ES_ENDPOINT')
    
    def set_elastic_env(self, value):
        logger.info(f"rotating elastic_env from {self.ELASTIC_ENV} to {value}")
        
        self.ELASTIC_ENV = value
        
        self.ELASTIC_USER = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/ELASTIC_USER_NAME", 
                                                WithDecryption=True)["Parameter"]["Value"]
        self.ELASTIC_PW = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/ELASTIC_PASS", 
                                                WithDecryption=True)["Parameter"]["Value"]
        self.ELASTIC_FINGERPRINT = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/ELASTIC_FINGERPRINT", 
                                                WithDecryption=True)["Parameter"]["Value"]
        self.ELASTIC_API_KEY = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/ELASTIC_API_KEY", 
                                                WithDecryption=True)["Parameter"]["Value"]
        self.ELASTIC_API_KEY_ID = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/ELASTIC_API_KEY_ID", 
                                                WithDecryption=True)["Parameter"]["Value"]
        self.ES_HOST = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/ELASTIC_HOST", 
                                                WithDecryption=True)["Parameter"]["Value"]
        self.ES_PORT = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/ELASTIC_PORT", 
                                                WithDecryption=True)["Parameter"]["Value"]
        self.ES_ENDPOINT = f"https://{self.ES_HOST}:{self.ES_PORT}"
        self.KIBANA_URL = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/KIBANA_URL", 
                                                    WithDecryption=True)["Parameter"]["Value"]
        self.IC_APP_URL = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/IC_APP_URL", 
                                                    WithDecryption=True)["Parameter"]["Value"]
        # self.REDIS_HOST = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/REDIS_HOST", WithDecryption=True)["Parameter"]["Value"]
        # self.REDIS_PORT = self.ssm_client.get_parameter(Name=f"/{self.ELASTIC_ENV}/REDIS_PORT", WithDecryption=True)["Parameter"]["Value"]
        
        # Recreate elastic engine
        from utils.elastic_engine import recreate_engine
        recreate_engine()
    
        logger.info("completed elastic_env rotation")
