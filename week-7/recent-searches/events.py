
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import json
import pika

load_dotenv(dotenv_path="../../.env", override=True)

username = os.getenv("ES_LOCAL_USERNAME")
password = os.getenv("ES_LOCAL_PASSWORD")

def _event_log_search(ch, method, properties, body):
    """
    This function will be invoked when a search event is published in the queue
    It will log the search query in the search-logs index in Elasticsearch
    """
    print (f"Received search event: {body}")
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
                       basic_auth=(username, password)
    )

    # we will receive body from the queue as a string
    log_entry = json.loads(body)

    # log the entry in the search-logs index
    es.index(index='search-logs', body=log_entry)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def _start_consumers():
    """
    This function will start the consumers for the search-logs queue
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='search-logs')

    channel.basic_consume(queue='search-logs', on_message_callback=_event_log_search)
    print (f"Waiting for search events to log in Elasticsearch. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    _start_consumers()
    