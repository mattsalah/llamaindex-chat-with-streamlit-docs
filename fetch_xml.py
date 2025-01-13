from dotenv import find_dotenv, load_dotenv
import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup
from loguru import logger

load_dotenv(find_dotenv(), override=True)
user = os.getenv('USER')
secret = os.getenv('SECRET')
ecs_endpoint = os.getenv('ECS_ENDPOINT')
here = Path(__file__).resolve().parent

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
            return True
        else:
            return False
    else:
        return True