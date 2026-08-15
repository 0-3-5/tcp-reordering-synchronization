# TCP Reordering Synchronization

Experimental framework for studying TCP packet reordering and synchronization effects in HTTP/2.

The project combines a custom HTTP/2 client, packet interception with NetfilterQueue/Scapy, and a Go HTTP/2 server to control packet delivery and measure request timing.

The client sends multiple HTTP/2 requests, intentionally delays selected TCP segments, and then releases them to observe how packet reordering affects synchronization and request processing.

## Project Structure

* `synchronization.py` — generates HTTP/2 requests and controls TCP packet delivery.
* `server.go` — HTTPS/HTTP/2 test server and request timing measurements.
* `results.csv` — experimental results.
* `packet_reordering.pdf` — research notes.

## Requirements

* Linux
* Python 3
* Go
* NetfilterQueue
* Scapy
* `h2spacex` - https://github.com/nxenon/h2spacex