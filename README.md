# TCP Reordering Synchronization

Experimental framework for studying TCP packet reordering, transport-layer synchronization, and request timing in HTTP/2 race-condition testing.

This project builds upon Ryotak's First Sequence Sync technique, extending the underlying TCP-level synchronization concept to a TLS-enabled HTTP/2 environment. Rather than relying exclusively on application-layer request synchronization, the framework explores how deliberate manipulation of TCP segment ordering can influence when fragmented HTTP/2 requests become available to the server.

The system combines a custom HTTP/2 client, a packet interception and manipulation layer using NetfilterQueue and Scapy, and a Go-based HTTP/2 server for controlled experimentation and timing measurement.

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