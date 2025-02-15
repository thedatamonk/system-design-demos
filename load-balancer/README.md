# What this project contains?

- Golang implementation of a load balancer
- demonstrate various features of a typical load balancer
- easy to setup - *Need to work on this*

## Features
1. API endpoint to add more servers in case of increase in traffic.
    - *Autoscaling*
        - define a load metric - request per second
        - scale up - if load metric exceeds a certain thresholds- 
            - then start a new server and register it
        - scale down - if load metric drop below a certain threshold for a defined period (say load drops below 20 RPS and stays like that continuously for 10 mins),
            - then remove a server
            - of course, we should not remove the server, if it's handling requests.
            
2. Remove unhealthy servers - unhealthy is defined by a `threshold`. If a server is not responding continously for `threshold` amount of time, then this server will automatically be removed.
3. Retry mechanism - if a server fails to respond to a request sent by the load balancer, then the load balancer tries to send the same request to another server.
4. Round robin strategy implementation
5. Rate limiting the load balancer

