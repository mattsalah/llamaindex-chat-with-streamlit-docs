from dotenv import find_dotenv, load_dotenv
import requests
import os
import boto3
from pathlib import Path
from bs4 import BeautifulSoup
from loguru import logger

load_dotenv(find_dotenv(), override=True)
user = os.getenv('USER')
secret = os.getenv('SECRET')
ecs_endpoint = os.getenv('ECS_ENDPOINT')
here = Path(__file__).resolve().parent
s3 = boto3.resource('s3')

def is_dummy_xml_content(xml_string: str) -> bool:
    soup = BeautifulSoup(xml_string, 'xml')
    text_element = soup.find('body')
    return (text_element.get('ana') == 'dummy' or len(text_element.text)<100)

def download_xml(xml_key) -> bool:
    outfile_path = here/'data'/xml_key.replace("/","_")
    if not os.path.exists(outfile_path):
        resp = requests.get(f"{ecs_endpoint}/actuator/documents?documentPath={xml_key}&user={user}&secret={secret}")
        if resp.status_code == 200:
            if is_dummy_xml_content(resp.text):
                logger.error(f'{xml_key} is a dummy xml, skipping')
                return False
            with open(outfile_path, 'w') as f:
                f.write(resp.text)
            return outfile_path
        else:
            return False
    else:
        return outfile_path
    

def download_s3_file(key, bucket, raise_exception=False):
    local_path = here/'data'/key.replace('/', '_')
    if not os.path.exists(local_path):
        if raise_exception:
            s3.Bucket(bucket).download_file(key, local_path)
            return local_path
        else:
            try:
                s3.Bucket(bucket).download_file(key, local_path)
            except Exception as e:
                logger.exception(e)
                return False
            return local_path
    else:
        return local_path
    
    
def download_data():
    xml_keys = [
        # "103/4358e331f543193440f7c1079da8340a/main.xml", ## this is just a letter
        # "101/a59d184cf9cc2cfecb331c7cd5a864fe/main.xml", ## very short agreement
        "1948/2ef55d9483753350b06babffe4398b1d/main.xml",
        # "2411/5aa58b4e43cde8bb9d30d5ae5d9df161/main.xml",
        # "316/bf55ae07c86b2ca8f77ffb1c73c5aeb7/main.xml",
        # "2411/650574620140779d010f0f0dd5d1e953/main.xml",
        # "95/7afc742ac66003fb5cf5ee0da30c49ce/main.xml"
    ]
    for xml_key in xml_keys:
        yield download_s3_file(xml_key.replace('main.xml', 'main_searchable.txt'), bucket='ppd2-scrape-processed', raise_exception=True)
        #download_xml(xml_key):