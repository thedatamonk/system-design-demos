# this code will read the `on_msg_unsent` event and then process it
# in this case, the process will be to update the unread message counter value

import pika
import json
import redis
from typing import List
import requests

BASE_URL = "http://127.0.0.1:8000"
# create redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)


async def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f" [x] Received {message}")

    # now here we have to write the logic to update the counter
    # for any new message from any sender, this function will be called.
    # these are micro writes to the DB.
    # TODO: We will also have to keep buffering new messages somewhere and avoid any micro-reads
    # for v1, we will do microreads
    url = f"{BASE_URL}/users/update_unread_msg_count"
    params = {"user_id": message['to'], "new_sender_ids": list(message['from'])}

    # I am using await since I don't want to wait for the request to complete.
    response = await requests.post(url, params=params)
    return response


#############################
###### Event consumers ######
#############################

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()


# fanout exchange broadcasts the messages it receives to all the queues it knows
channel.exchange_declare(exchange='whatsapp', exchange_type='fanout')

# we declare a quue called `chats`
channel.queue_declare(queue='chats', durable=True)

# now we need to bind the exchange with the queue
channel.queue_bind(exchange='whatsapp', queue='chats')

print (f" [*] Waiting for messages. To exit press CTRL+C")

# Start consuming messages
# auto_ack = True acknowledges as soon as messages are received. no explicity acknowledgement is required from teh consumer
channel.basic_consume(queue='chats', on_message_callback=callback, auto_ack=True)


try:
    channel.start_consuming()
except KeyboardInterrupt:
    print (f" [*] Exiting...")
    channel.stop_consuming()
finally:
    connection.close()

