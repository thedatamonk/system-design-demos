import redis
from redis.cache import CacheConfig
from faker import Faker
import time

# create a redis instance
# redis_conn = redis.Redis(host='localhost', port=6379, protocol=3, cache_config=CacheConfig(), decode_responses=True)
# create a redis connection pool
redis_pool = redis.ConnectionPool().from_url("redis://localhost")

# Initialize Faker instance
fake = Faker()

# Generate a list of user dictionaries
users = []
for _ in range(5):
    user = {
        "name": fake.first_name(),
        "surname": fake.last_name(),
        "company": fake.company(),
        "age": fake.random_int(min=20, max=65)
    }
    users.append(user)

for i, user in enumerate(users):
    session_id = f"session-{i+1}"
    print (f"Creating session for user {i+1}...")
    redis_conn = redis.Redis().from_pool(redis_pool)
    print (f"Acquired connection: {redis_conn.info()}...")
    redis_conn.hset(session_id, mapping=user)
    print (f"Closed connection: {redis_conn.info()}...")
    redis_conn.close()

redis_pool.close()
# # print (f'---'*80)
# # print (redis_conn.hgetall('session-9'))
# s1 = time.perf_counter()
# for o 
# attempt1 = redis_conn.hgetall('session-1')
# print (f"Attempt 1 execution time: {time.perf_counter() - s1}")

# s2 = time.perf_counter()
# attempt1 = redis_conn.hgetall('session-1')
# print (f"Attempt 2 execution time: {time.perf_counter() - s2}")

