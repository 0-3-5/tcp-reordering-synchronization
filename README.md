# TCP Reordering Synchronization

Experimental framework for studying **TCP packet reordering and synchronization effects in HTTP/2**.

The project combines a custom HTTP/2 client, packet interception with NetfilterQueue/Scapy, and a Go HTTP/2 server to control packet delivery and measure request timing.

## Project Structure

* `synchronization.py` — generates HTTP/2 requests and controls TCP packet delivery.
* `server.go` — HTTPS/HTTP/2 test server and request timing measurements.
* `results.csv` — experimental results.
* `packet_reordering.pdf` — research notes / experiment documentation.

## Experiment

The client sends multiple HTTP/2 requests, intentionally delays selected TCP segments, and then releases them to observe how packet reordering affects synchronization and request processing.

## Requirements

* Linux
* Python 3
* Go
* HTTP/2 support
* NetfilterQueue
* Scapy
* `h2spacex`

Root/network privileges may be required for packet interception.

## Status

**Research / experimental code.** Results and implementation may change as experiments are refined.
