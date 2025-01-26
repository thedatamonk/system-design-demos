from es_utils import get_es_client

es = get_es_client()

def full_text_search(query, index_name):
    response = es.search(
        index = index_name,
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name", "phone", "occupation", "location"]
                }
            }
        }
    )

    return response['hits']['hits']

def fuzzy_match_search(query, index_name):
    response = es.search(
        index = index_name,
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name", "phone", "occupation", "location"],
                    "fuzziness": "AUTO"
                }
            }
        }
    )

    return response['hits']['hits']

def spell_correction(query, index_name):
    response = es.search(
        index = index_name,
        body = {
            'query': {
                "multi_match": {
                    "query": query,
                    "fields": ["name", "phone", "occupation", "location"],
                    "fuzziness": "AUTO"
                }
            },
            "suggest": {
                "text": query,
                "name_suggest": {
                    "phrase": {
                        "field": "name",
                        "size": 3,
                        "gram_size": 5,
                        "direct_generator": [
                            {
                                "field": "name",
                                "suggest_mode": 'missing'
                            }
                        ],
                        "highlight": {
                            "pre_tag": "<b>",
                            "post_tag": "</b>"
                        }
                    }
                }
            }
        }
    )

    # get the search query results
    results = response['hits']['hits']

    # get the spelling corrections of the query
    suggestions = response['suggest']['name_suggest'][0]['options']

    return results, suggestions

def synonymic_query_expansion():
    pass

def phonetic_search():
    pass
