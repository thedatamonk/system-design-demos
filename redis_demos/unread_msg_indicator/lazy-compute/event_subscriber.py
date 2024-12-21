# this code will read the `on_msg_unsent` event and then process it
# in this case, the process will be to update the unread message counter value
# Now we need to test this whole system properly
# TODO: Test the whole system properly and write the test cases and also think about how different componets will scale


import aio_pika
import json
import redis
from typing import List, Dict
import asyncio
import aiohttp
from collections import defaultdict


BASE_URL = "http://127.0.0.1:8000"
NUM_QUEUES = 10

# create redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Buffer to store messages
message_buffer: Dict[int, List[int]] = defaultdict(list)


async def flush_buffer():
    while True:
        print (f" [x] Flushing buffer...")
        await asyncio.sleep(10)  # Flush every 10 seconds
        for user_id, sender_ids in message_buffer.items():
            if sender_ids:
                print(f" [x] Updating unread message count for user_id: {user_id} with sender_ids: {sender_ids}")
                await update_unread_msg_count(user_id, sender_ids)
                message_buffer[user_id] = []  # Clear the buffer for the user


async def update_unread_msg_count(user_id: int, sender_ids: List[int]):
    url = f"{BASE_URL}/users/update_unread_msg_count"
    data = {"new_sender_ids": sender_ids}

    # I am using await to wait for the request to complete.
    # async version
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params={"user_id":user_id}, json=data) as response:
            return await response.json()

# def callback(ch, method, properties, body):
#     message = json.loads(body)
#     print(f" [x] Received {message}")
#     user_id = message['to']
#     sender_id = message['from']
#     message_buffer[user_id].append(sender_id)
#     print (f" [x] Buffer: {message_buffer}")

async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        message_body = json.loads(message.body)
        print(f" [x] Received {message_body}")
        user_id = message_body['to']
        sender_id = message_body['from']
        message_buffer[user_id].append(sender_id)
        print(f" [x] Buffer: {message_buffer}")


#############################
###### Event consumers ######
#############################
# async def archive_main():

#     # start the buffer flushing task
#     asyncio.create_task(flush_buffer())

#     # setup RabbitMQ connection
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
#     channel = connection.channel()


#     # fanout exchange broadcasts the messages it receives to all the queues it knows
#     channel.exchange_declare(exchange='whatsapp', exchange_type='fanout')

#     # we declare a quue called `chats`
#     channel.queue_declare(queue='chats', durable=True)

#     # now we need to bind the exchange with the queue
#     channel.queue_bind(exchange='whatsapp', queue='chats')

#     print (f" [*] Waiting for messages. To exit press CTRL+C")

#     # Start consuming messages
#     # auto_ack = True acknowledges as soon as messages are received. no explicity acknowledgement is required from teh consumer
#     channel.basic_consume(queue='chats', on_message_callback=callback, auto_ack=True)


#     try:
#         channel.start_consuming()
#     except KeyboardInterrupt:
#         print (f" [*] Exiting...")
#         channel.stop_consuming()
#     finally:
#         connection.close()

async def main():
    # Start the buffer flushing task
    asyncio.create_task(flush_buffer())

    # Setup RabbitMQ consumer
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=1)

    exchange = await channel.declare_exchange('whatsapp', aio_pika.ExchangeType.FANOUT)

    queue = await channel.declare_queue('chats', durable=True)
    
    await queue.bind(exchange)
    await queue.consume(on_message)

    print(f" [*] Waiting for messages. To exit press CTRL+C")

    await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())