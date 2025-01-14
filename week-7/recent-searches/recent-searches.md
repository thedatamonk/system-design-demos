## Designing recent searches
*When you tap on the search bar on any web application or app, the list of items that are shown is the recent searches. These searches are the recent searches that the user has done.*

***Note:*** *this is different from popular searches*

**First, as a good engineer you should ask why recent searches are important??**

2 approaches

1. pre-computed - very fast
2. on-the-fly - very accurate but very slow (during heavy loads)


### Pre-computed
1. read path
    - this is eazy-peazy
    - store recent searches in fast KV stores like Redis.
    - good for fast access but not good for durability
    - here key is user and value is list of recent searches
2. write path
     - need to think about how to update the value

#### Things to do
1. setup elastic search

## Random notes
1. Elastic search stores data as JSON objects (documents)
2. Whether you have - 
    - structured / unstructured text,
    - numerical data,
    - geospatial data
    Elasticsearch efficiently stores and indexes it in a way that supports fast searches

3. indices we will need in elasticsearch - 
    - docs (1 or more of these will be returned when the user searches for something.)
    - search-logs ( whatever the user searches will be stored here)
4. redis will only be used for storing last 10 most recent searches
    - we will need to write some code that can update this in the redis key value store (write path)
    - we will also need to write an endpoint that returns the recent searches for a given user (read path)
