
2. monitor metrics of the load balancer - 
    - note down the metrics
    - implement them
3. can we incorporate rate limiting at the load balancer level?
    - need to read about it.
    - should we apply rate limiter at the load balancer or at each individual backend server
4. implement other load balancing strategies
    - read about the different strategies
    - implement some of the common ones.
5. I need to package the project in such a way so that it's easy to build, run and test it.
6. Implement test setup.
7. Complete the load balancer and push to github. Forget about the UI part of it right now.
8. Then complete the image server part. I would say do not focus on the UI part as of now.


## Important commands
1. *Start a HTTP server at port 8000*
```
python -m http.server 8000
```

2. *Send a request to a server @ `localhost:8000`*
```
curl -s -i http://localhost:8000
```
