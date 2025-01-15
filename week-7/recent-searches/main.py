from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../../.env", override=True)

username = os.getenv("ES_LOCAL_USERNAME")
password = os.getenv("ES_LOCAL_PASSWORD")

# utility to ingest docs in Elasticsearch
def ingest_docs_in_es():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
                       basic_auth=(username, password)
    )   
    
    # Dummy data
    docs = [
        {"title": "Document 1", "content": "This is the content of document 1"},
        {"title": "Document 2", "content": "This is the content of document 2"},
        {"title": "Document 3", "content": "This is the content of document 3"},
    ]
    
    for i, doc in enumerate(docs):
        es.index(index='documents', id=i+1, body=doc)

# utility to deal with searching of docs in Elasticsearch
def search(query):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
                       basic_auth=(username, password)
    )

    # exact match
    response = es.search(
        index='documents',
        body={
            "query": {
                "multi_match": {
                    'query': query,
                    'fields': ['title', 'content']
                }
            }
        }
    )


    return response['hits']['hits']

# utility to log all searches in Elasticsearch
# this logging can happen synchronously or asynchronously
# synchronous logging will happen before the search is executed
# asynchronous logging will happen after the search is executed - for this we will use pub-sub model with rabbitmq
def log_search():
    pass

# utility to store last N recent searches in Redis as KV pairs
def store_recent_searches():
    pass


if __name__ == "__main__":
    # ingest_docs_in_es()
    query1 = 'Document'
    results = search(query=query1)
    for result in results:
        print(result['_source'])
    
    # log_search()
    # store_recent_searches()