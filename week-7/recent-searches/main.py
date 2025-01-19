from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import pika
import json
import redis

load_dotenv(dotenv_path="../../.env", override=True)

username = os.getenv("ES_LOCAL_USERNAME")
password = os.getenv("ES_LOCAL_PASSWORD")

# Initialize Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
# utility to ingest docs in Elasticsearch
def ingest_docs_in_es():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
                       basic_auth=(username, password)
    )   
    
    # Dummy data
    docs = [
        {"title": "Document 1", "content": "This is the content of document 1. And it's very boring."},
        {"title": "Document 2", "content": "This is the content of document 2. And it's very interesting."},
        {"title": "Document 3", "content": "This is the content of document 3. And I haven't even read it."},
        {"title": "Doc 4", "content": "This is the content of doc 4"}
    ]
    
    for i, doc in enumerate(docs):
        es.index(index='documents', body=doc)

# utility to deal with searching of docs in Elasticsearch
def search(query, user_id, synchronous_logging=True):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
                       basic_auth=(username, password)
    )
    
    ##########################################
    #### Search for docs in Elasticsearch ####
    ##########################################

    response = es.search(
        index='documents',
        body={
            "query": {
                "bool": {
                    "should": [
                        {"match_phrase_prefix": {"title": query}},
                        {"match_phrase_prefix": {"content": query}}
                    ]
                }
            }
        }
    )

    ##################################
    # Store recent searches in Redis #
    ##################################
    store_recent_searches(user_id, query)



    ##################################
    #### Logging the search query ####
    ##################################
    # synchronous logging
    if synchronous_logging:
        log_search(query)
    else:
        # asynchronous logging
        # here we're going to publish an 'log-search' event in the queue
        # this event will be picked up by the consumer and the search query will be logged in Elasticsearch
        publish_log_search_event(query)

    return response['hits']['hits']

# Utility to log all searches in Elasticsearch synchronously
# logging will happen before the search results are returned
def log_search(query):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
                       basic_auth=(username, password)
    )

    log_entry = {
        'query': query,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

    # log the entry in the search-logs index
    es.index(index='search-logs', body=log_entry)

# Utility to log all searches asynchronously
# logging will happen after the search results are returned asynchronously
# for this we will use pub-sub model with rabbitmq
# When we implement asynchronous logging, we will have to generate an event and publish it in the queue
# From there it will be picked up and this function will be invoked
def publish_log_search_event(query):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='search-logs')

    log_entry = {
        'query': query,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

    print (f"Sending search event to log in Elasticsearch: {log_entry}")
    channel.basic_publish(exchange='', routing_key='search-logs', body=json.dumps(log_entry))

    connection.close()

# utility to store last N recent searches in Redis as KV pairs
def store_recent_searches(user_id, query):
    print (f"Storing query {query} in Redis for user {user_id}...")
    key = f"recent-searches:{user_id}"
    redis_client.lpush(key, query)
    redis_client.ltrim(key, 0, 9) # Keep only the last 10 searches

if __name__ == "__main__":
    # ingest_docs_in_es()


    queries = ['Content', 'interesting', 'Borings', 'boring']

    for user_query in queries:
        # This search function can later be invoked by a search API
        # to return search results to the user
        # Currently, it performs full text search on the title and content fields
        # But later, it can be modified to include more complex search algorithms
        user_id = "rohil-pal"
        search_results = search(query=user_query, user_id=user_id, synchronous_logging=False)
        print(f"Search results for query: {user_query}")
        for result in search_results:
            print(result['_source'])
        print ("***"*40)

    
    # log_search()
    # store_recent_searches()