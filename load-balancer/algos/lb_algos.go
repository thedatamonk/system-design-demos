package algos

import (
	"sync"
	"errors"
	"math/rand"
)


type LoadBalancer interface {
	SelectServer() (string, error)
	AddServer(server string)
	RemoveServer(server string)
}

// Round Robin strategy

type RoundRobin struct {
	servers []string
	index   int
	mu      sync.Mutex
}

func NewRoundRobin(servers []string) *RoundRobin {
	return &RoundRobin{servers: servers, index: 0}
}

func (rr *RoundRobin) SelectServer() (string, error) {
	rr.mu.Lock()
	defer rr.mu.Unlock()
	if len(rr.servers) == 0 {
		return "", errors.New("no servers available")
	}
	server := rr.servers[rr.index]
	rr.index = (rr.index + 1) % len(rr.servers)
	return server, nil
}

func (rr *RoundRobin) AddServer(server string) {
	rr.mu.Lock()
	defer rr.mu.Unlock()
	rr.servers = append(rr.servers, server)
}

func (rr *RoundRobin) RemoveServer(server string) {
	rr.mu.Lock()
	defer rr.mu.Unlock()
	for i, s := range rr.servers {
		if s == server {
			rr.servers = append(rr.servers[:i], rr.servers[i+1:]...)
			break
		}
	}
}

// Random server strategy

type RandomLB struct {
	servers []string
	mu      sync.Mutex
}

func NewRandomLB(servers []string) *RandomLB {
	return &RandomLB{servers: servers}
}

func (r *RandomLB) SelectServer() (string, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if len(r.servers) == 0 {
		return "", errors.New("no servers available")
	}
	index := rand.Intn(len(r.servers))
	return r.servers[index], nil
}

func (r *RandomLB) AddServer(server string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.servers = append(r.servers, server)
}

func (r *RandomLB) RemoveServer(server string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	for i, s := range r.servers {
		if s == server {
			r.servers = append(r.servers[:i], r.servers[i+1:]...)
			break
		}
	}
}

type LBStrategy string

const (
	RoundRobinStrategy LBStrategy = "round_robin"
	RandomStrategy     LBStrategy = "random"
)

func NewLoadBalancer(strategy LBStrategy, servers []string) LoadBalancer {
	switch strategy {
	case RoundRobinStrategy:
		return NewRoundRobin(servers)
	case RandomStrategy:
		return NewRandomLB(servers)
	default:
		return nil
	}
}


