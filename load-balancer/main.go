package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"reflect"
	"sync"
	"sync/atomic"
	"time"
)

type LoadBalancer struct {
	Current			int
	Mutex			sync.Mutex
	servers			[]*Server
	failureCount 	map[string]int
	removeAfter		int
	healthCheckInterval time.Duration
	num_requests			int64
}


// define a method for LoadBalancer struct type
func (lb *LoadBalancer) allocateServer(servers []*Server) *Server {
	// this function returns a pointer to one of the servers
	// this is the round robin technique
	lb.Mutex.Lock()
	defer lb.Mutex.Unlock()

	for i := 0; i < len(servers); i++ {

		// TODO: Do we need to make the next line atomic.
		// This might be required when our load balancer is not just a single machine
		// but is present on multiple machines.
		// for now, we will assume that the load balancer resides on a single machine
		idx := lb.Current % len(servers)
		nextServer := servers[idx]
		lb.Current++

		nextServer.Mutex.Lock()
		IsHealthy := nextServer.IsHealthy
		nextServer.Mutex.Unlock()

		if IsHealthy {
			return nextServer
		}
	}

	return nil
}

// this function is called by load balancer when we need to add a server
// in case of surge in traffic
// the criterion of when will this function be called can vary
// but this function doesn't reallly cares about that
func (lb *LoadBalancer) addServer(server_addr string) {
	lb.Mutex.Lock()
	defer lb.Mutex.Unlock()

	u, _ := url.Parse(server_addr)
	server := &Server{URL: u, IsHealthy: true}
	lb.servers = append(lb.servers, server)
	log.Printf("Added new server @ %s", server_addr)
}

// this function is called by load balancer when we need to remove an unhealthy
// server
func (lb *LoadBalancer) removeServer(server_addr string) {
	lb.Mutex.Lock()
	defer lb.Mutex.Unlock()

	// iterate over all the servers that the load balancer has visibility over
	// to find the server at server_addr
	// TODO: Once we remove a server, we also need to ensure that the health check
	// should not happen for that server
	// I think currently it's happening
	for i, server := range lb.servers {
		if server.URL.String() == server_addr {
			lb.servers = append(lb.servers[:i], lb.servers[i+1:]...)
			delete(lb.failureCount, server_addr)		// delete entry from failure count mapping
			log.Printf("Removed server @ %s", server_addr)
			return
		}
	}
}


func (lb *LoadBalancer) monitorTraffic() {
	// monitors traffic every 10 seconds, and add/remove servers depending upon RPS (requests per second)
	for range time.Tick(time.Second * 10) {
		num_requests := atomic.LoadInt64(&lb.num_requests)
		atomic.StoreInt64(&lb.num_requests,  0)

		if num_requests > 100 {
			lb.addServer("http://localhost:9100")		// TODO: What server to add?
		}

		// Note: We wont be removing any servers because removal of servers
		// is handled by healthCheck()
	}
}

func (lb *LoadBalancer) healthCheck() {
	for range time.Tick(lb.healthCheckInterval) {
		for _, server := range lb.servers {
			res, err := http.Head(server.URL.String())
			server.Mutex.Lock()
			if err != nil || res.StatusCode != http.StatusOK {
				fmt.Printf("%s is down\n", server.URL)
				server.IsHealthy = false
				lb.failureCount[server.URL.String()]++
				fmt.Printf("Server %s down (%d/%d failures)\n", server.URL.String(), lb.failureCount[server.URL.String()], lb.removeAfter)
			
				if lb.failureCount[server.URL.String()] >= lb.removeAfter {
					lb.removeServer(server.URL.String())
				}
			} else {
				server.IsHealthy = true
				lb.failureCount[server.URL.String()] = 0
			}
			server.Mutex.Unlock()
		}
		
	}
}

type Server struct {
	URL			*url.URL
	IsHealthy	bool
	Mutex		sync.Mutex
}

func (server *Server) ReverseProxy() *httputil.ReverseProxy {
	return httputil.NewSingleHostReverseProxy(server.URL)
}


type Config struct {
	Port 					string		`json:"port"`
	HealthCheckInterval		string		`json:"healthCheckInterval"`
	Servers					[]string 	`json:"servers"`
	LbAlgo					string		`json:"lbAlgo"`
	MaxRetries				int			`json:"maxRetries"`
}

func loadConfig(file string) (Config, error) {
	var config Config
	data, err := os.ReadFile(file)
	if err != nil {
		return config, err
	}

	err = json.Unmarshal(data, &config)
	if err != nil {
		return config, err
	}

	return config, nil
}


func printStructFields(s interface{}) {
	val := reflect.ValueOf(s)
	typ := reflect.TypeOf(s)

	for i := 0; i < val.NumField(); i++ {
		fmt.Printf("%s: %v\n", typ.Field(i).Name, val.Field(i).Interface())
	}
}


func forwardRequest(server *Server, w http.ResponseWriter, r *http.Request) error {
	recorder := &ResponseRecorder{ResponseWriter: w, statusCode: http.StatusOK}
	server.ReverseProxy().ServeHTTP(recorder, r)

	// If response is a server error (5xx), return error
	if recorder.statusCode >= 500 {
		return fmt.Errorf("server returned %d", recorder.statusCode)
	}
	return nil
}

// Custom Response Recorder to capture status code
type ResponseRecorder struct {
	http.ResponseWriter
	statusCode int
}

func (r *ResponseRecorder) WriteHeader(code int) {
	r.statusCode = code
	// r.ResponseWriter.WriteHeader(code)
}

func main() {
	// load server config
	config, err := loadConfig("config.json")
	if err != nil {
		log.Fatalf("Error loading configuration: %s", err.Error())
	}

	// pretty print the config
	printStructFields(config)

	// get the health check duration from the config
	healthCheckInterval, err := time.ParseDuration(config.HealthCheckInterval)
	if err != nil {
		log.Fatalf("Invalid health check interval: %s", err.Error())
	}

	// initialise backend servers specified as per the config
	var servers []*Server
	for _, serverUrl := range config.Servers {
		u, _ := url.Parse(serverUrl)
		server := &Server{URL: u, IsHealthy: true}
		servers = append(servers, server)
	}

	// instantiate load balancer and initiate health check module between load balancer and each backend server
	// current indicates the index of the currently active server
	lb := LoadBalancer{
						Current: 0,
						servers: servers,
						failureCount: make(map[string]int),
						removeAfter: 30,
						healthCheckInterval: healthCheckInterval,
					}

	// will have to run the health cheeck in a separate thread
	// go lb.healthCheck()

	// monitor traffic and accordingly add servers from pool
	// go lb.monitorTraffic()
	
	maxRetries := config.MaxRetries

	// handler function to handle request to the load balancer
	// insides this handler function, we will call the allocateServer method that will return the server that needs to server this request
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request){
		
		var lastErr error
		for attempt := 1; attempt <= maxRetries; attempt++ {
			// find the next server using the specified load balancing strategy
			// for now we are implementing round-robin strategy
			server := lb.allocateServer(servers)
		
			// TODO: Why no error message is being displayed on the terminal
			// when no servers are avavilable
			if server == nil {
				http.Error(w, "No healthy server available", http.StatusServiceUnavailable)
				return
			}

			// if we found a valid server
			w.Header().Add("X-Forwarded-Server", server.URL.String())

			// try processing the request
			err := forwardRequest(server, w, r)

			if err == nil {
				return
			}
			
			// Log failure & retry
			lastErr = err
			fmt.Printf("Attempt %d failed for server %s: %v. Retrying...\n", attempt, server.URL.String(), err)

			// Optional: Add small delay before retrying (exponential backoff possible)
			time.Sleep(100 * time.Millisecond)

		}

		// If all retries fail, return error response
		fmt.Printf("Request failed after %d retries: %v", maxRetries, lastErr)
		
	})

	// DEMO: add a new server after 2 minutes delay
	// time.AfterFunc(2 * time.Minute, func() {
	// 	log.Printf("Current time: %s", time.Now().Format("2006-01-02 15:04:05"))
	// 	lb.addServer("http://localhost:5900")
	// })


	// // DEMO: remove a server after 3 mins delay
	// time.AfterFunc(3 * time.Minute, func() {
	// 	log.Printf("Current time: %s", time.Now().Format("2006-01-02 15:04:05"))
	// 	lb.removeServer("http://localhost:5001")
	// })

	log.Println("Starting load balancer on port", config.Port)
	err = http.ListenAndServe(config.Port, nil)
	if err != nil {
		log.Fatalf("Error starting load balancer: %s\n", err.Error())
	}

}