1. GET /images/{image_id}
2. POST /images/new

Some numbers- 
1. 1400 images per second uploaded by different clients from anywhere in the world
2. serve images efficiently.
3. provide analytics about how images are requested by the clients
4. bandwith consumption should be near optimal


I think first let's understand the requirements by asking from chatgpt
- then detail down the requirements and start implementation

Load balancer - rewrite and package the load balancer so that you can use it here.


*Questions*
1. What is an API Gateway? 
    - it's not required here for the demo as looks like it's main purpose here is to route requests between different services


**Services needed**

1. upload service
    - from user device to the queue
2. storing service
    - from the queue to the cloud storage
    - the storing service also stores the meta data about teh iamge besides just saivng the image

3. processing service
    - it can happen in the background
4. cdn service
    - not really sure if we need a service, but we definitely need to setup a CDN
    - need to find out a free CDN if available - bunnyCDN



*I genuinely feel that we can use golang here since there is a lot of multithreaded programming happenning here*


