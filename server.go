package main

import (
	"crypto/tls"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"golang.org/x/net/http2"
)

var (
	requestTimes     []int64
	mu               sync.Mutex
	lastRequestTime  int64
	firstRequestTime int64 = -1
	requestNum       int64 = 0
)

func handler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" || r.URL.Path != "/api/data" {
		http.NotFound(w, r)
		return
	}

	bodyBytes, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "error reading body", http.StatusInternalServerError)
		return
	}

	body := string(bodyBytes)

	if firstRequestTime == -1 {
		firstRequestTime = time.Now().UnixMilli()
	}

	timestamp := time.Now().UnixMilli()
	lastRequestTime = timestamp
	requestNum++

	params, err := url.ParseQuery(body)
	if err != nil {
		http.Error(w, "invalid form data", http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	fmt.Fprintf(w, "Received a=%s", params.Get("a"))
}

func saveRequestTimes() {
	mu.Lock()
	defer mu.Unlock()
	if requestNum == 0 {
		log.Println("No requests recorded.")
		return
	}

	first := firstRequestTime
	last := lastRequestTime
	elapsed := last - first

	log.Printf("Number of requests: %d", requestNum)
	log.Printf("Elapsed time: %d ms", elapsed)
}

func main() {
	cert, err := tls.LoadX509KeyPair(
		"server.crt",
		"server.key",
	)
	if err != nil {
		log.Fatal(err)
	}

	server := &http.Server{
		Addr:    ":443",
		Handler: http.HandlerFunc(handler),
		TLSConfig: &tls.Config{
			Certificates: []tls.Certificate{cert},
			NextProtos:   []string{"h2"},
		},
		ErrorLog: log.New(os.Stdout, "http: ", log.LstdFlags),
	}

	http2Server := &http2.Server{
		MaxConcurrentStreams: 90000000,
	}

	if err := http2.ConfigureServer(server, http2Server); err != nil {
		log.Fatal(err)
	}

	sigs := make(chan os.Signal, 1)
	signal.Notify(
		sigs,
		syscall.SIGINT,
		syscall.SIGTERM,
	)
	go func() {
		<-sigs

		log.Println("Shutting down...")

		saveRequestTimes()

		os.Exit(0)
	}()

	log.Println("HTTP/2 server running on https://0.0.0.0:443")
	log.Println("MaxConcurrentStreams =", http2Server.MaxConcurrentStreams)

	log.Fatal(server.ListenAndServeTLS("", ""))
}
