import socket

max_Size = 1024  # Message max size
ip = "127.0.0.1"


print("\n    DNS Server;  Copyright (C) 2023  Roy Simanovich and Yuval Yurzdichinsky\n"
		 "This program comes with ABSOLUTELY NO WARRANTY.\n"
		 "This is free software, and you are welcome to redistribute it\n"
		 "under certain conditions; see `LICENSE' for details.\n\n")

print("[DNS] Starting dns server...")

# create a socket for the dns server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, 53))

domain_cache = {}

while True:
    print("[DNS] Waiting for client...")
    
    # Receive domain name from the client
    domain_name, client_address = sock.recvfrom(max_Size)
    domain_name = domain_name.decode('utf-8')

    # check if domain name is in cache (basic caching)
    if domain_name in domain_cache:
        print("[DNS] Domain name found in cache!")
        sock.sendto(domain_cache[domain_name].encode('utf-8'), client_address)
        continue

    # resolve domain name to its IP address using google's public DNS server, via TCP (port 53)
    try:
        address_info = socket.getaddrinfo(domain_name, 80, socket.AF_INET, socket.SOCK_STREAM)
        ip_address = address_info[0][4][0]
        domain_cache[domain_name] = ip_address
        sock.sendto(ip_address.encode('utf-8'), client_address)
        print("[DNS] Sent IP to client successfully!")
    except socket.gaierror:
        sock.sendto("Could not find IP address for this domain".encode('utf-8'), client_address)
