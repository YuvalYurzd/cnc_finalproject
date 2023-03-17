import socket
import time

# Define ip, ports, max packet size and congestion control variables
server_Port = 20159
ip = "127.0.0.1"
client_Port = 30175
max_Size = 1024
timeout = 15
max_Retries = 3

print("\n    SQL Client with reliabe UDP;  Copyright (C) 2023  Roy Simanovich and Yuval Yurzdichinsky\n"
		 "This program comes with ABSOLUTELY NO WARRANTY.\n"
		 "This is free software, and you are welcome to redistribute it\n"
		 "under certain conditions; see `LICENSE' for details.\n\n")

# Create a UDP socket to connect to the server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, client_Port))

# "Handshake" with the server
message = "Handshake"
sock.sendto(message.encode('utf-8'), (ip, server_Port))

# Receive list of queries from the server
while True:
    try:
        data, server_address = sock.recvfrom(max_Size)
        print(f"Received from server {server_address}: {data.decode('utf-8')}")
        sock.sendto("ACK".encode("utf-8"), (ip, server_Port))
        break
    except socket.timeout:
        print("Timeout while waiting for queries")

# Send queries to the server
query_num = 1  # Query serial number
while True:
    query_name = input("Choose query to use, or type nothing to stop: ")
    query_name = query_name + "|" + str(query_num)
    retries = 0
    while retries < max_Retries:
        start_time = time.time()  # Measure the start time of transmission
        sock.sendto("ACK".encode("utf-8"), (ip, server_Port))
        sock.sendto(query_name.encode('utf-8'), (ip, server_Port))
        try:
            if "nothing" in query_name:
                sock.sendto("ACK".encode("utf-8"), (ip, server_Port))
                print("Closing connection...")
                sock.close()
                exit()
            data, address = sock.recvfrom(max_Size)
            data = data.decode('utf-8')
            if data == "ACK":
                result_received = False
                while not result_received:
                    try:
                        if retries > 0: # Resend message
                            print("Retrying to send...")
                            sock.sendto("ACK".encode("utf-8"), (ip, server_Port))
                            sock.sendto(query_name.encode('utf-8'), (ip, server_Port))
                        sock.settimeout(timeout)
                        result, address = sock.recvfrom(max_Size)
                        result = result.decode("utf-8")
                        sock.sendto("ACK".encode("utf-8"), (ip, server_Port))
                        result_received = True
                    except socket.timeout:
                        print(f"Timeout while waiting for query result #{query_num}")
                        retries += 1
                        if retries == max_Retries:
                            print(f"Maximum number of retries reached while waiting for query result #{query_num}, "
                                  f"closing connection...")
                            sock.close()
                            exit()
            elif data == "Timed out":
                print("Server timed out, closing connection...")
                sock.close()
                exit()
        except socket.timeout:
            retries += 1  # increase retries counter by 1
            print(f"timeout #{retries}, trying again")
            pass  # Retry if timeout occurs

        if data != "Timed out":
            print(f"Received from server {server_address}: {result}, {data}")
            end_time = time.time()  # Measure the end time of transmission
            rtt = end_time - start_time  # Calculate the RTT
            if rtt < 0.5 * timeout:
                timeout *= 0.9  # Increase the transmission rate
            else:
                timeout *= 1.2  # Decrease the transmission rate
            break

    if retries == max_Retries:
        print(f"Maximum number of retries reached while trying to send query #{query_num}, closing connection...")
        exit()
    query_num += 1

sock.close()