import random
import string
from main import search

# List of common English words
common_words = [
    "document", "content", "interesting", "boring", "example", "search", "query", "result", "test", "data",
    "information", "text", "analysis", "index", "title", "description", "random", "generate", "user", "system"
]

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_usernames_and_queries(num_users=10, num_queries_per_user=5):
    users_queries = {}
    for _ in range(num_users):
        username = generate_random_string()
        queries = [random.choice(common_words) for _ in range(num_queries_per_user)]
        users_queries[username] = queries
    return users_queries


if __name__ == "__main__":
    # generate random usernames and queries
    users_queries = generate_usernames_and_queries(num_users=10, num_queries_per_user=100)

    for user_id, queries in users_queries.items():
        for user_query in queries:
            search_results = search(query=user_query, user_id=user_id, synchronous_logging=False)
            print(f"Search results for user: {user_id}, query: {user_query}")
            for result in search_results:
                print(result['_source'])
            print ("\n")
        print("***" * 40)
        