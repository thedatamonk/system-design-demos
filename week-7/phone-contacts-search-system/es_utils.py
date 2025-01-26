from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../../.env", override=True)

es_username = os.getenv("ES_LOCAL_USERNAME")
es_password = os.getenv("ES_LOCAL_PASSWORD")


def get_es_client():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}], basic_auth=(es_username, es_password))
    return es