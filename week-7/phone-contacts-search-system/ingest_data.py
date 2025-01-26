from faker import Faker
import logging
from elasticsearch import helpers
from dotenv import load_dotenv
from es_utils import get_es_client
import os


# initalise logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# elasticsearch client
es = get_es_client()

# faker initialisation
fake = Faker()

def generate_contact():
    contact = {
        "name": fake.name(),
        "phone": fake.phone_number(),
        "occupation": fake.job(),
        "location": f"{fake.city()}, {fake.country()}"
    }
    logger.debug(f"Generated contact: {contact}")
    return contact

    

def generate_contacts(num_contacts):
    contacts = []
    for _ in range(num_contacts):
        contacts.append(generate_contact())
    logger.info(f"Generated {num_contacts} contacts")
    return contacts


def index_contacts(contacts, es_index_name):
    actions = [
        {
            "_index": es_index_name,
            "_source": contact
        }
        for contact in contacts
    ]
    # Bulk indexing
    helpers.bulk(es, actions)
    logger.info(f"Indexed {len(contacts)} contacts into Elasticsearch index '{es_index_name}'")

if __name__ == "__main__":
    num_contacts = 1000
    index_name = 'contacts'
    
    logger.info(f"Starting to generate {num_contacts} contacts")
    contacts = generate_contacts(num_contacts)

    logger.info(f"Starting to index contacts into Elasticsearch index '{index_name}'")
    index_contacts(contacts, index_name)

    logger.info(f"Completed indexing {num_contacts} contacts into Elasticsearch")