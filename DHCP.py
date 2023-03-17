import socket

# Define parameters for ports and packet maximum size
max_Size = 1024
server_DHCPPort = 67
client_DHCPPort = 68

# Define variables for MAC address
C_mac_part1 = [0x08, 0x00, 0x27, 0x80]
C_mac_part2 = [0xd5, 0x8a, 0x00, 0x00]


class DHCP_server(object):
    def server(self):
        print("\n    DHCP Server;  Copyright (C) 2023  Roy Simanovich and Yuval Yurzdichinsky\n"
		 "This program comes with ABSOLUTELY NO WARRANTY.\n"
		 "This is free software, and you are welcome to redistribute it\n"
		 "under certain conditions; see `LICENSE' for details.\n\n")
            
        print("[DHCP] DHCP server starting...\n")

        # Create a socket for the server to connect to the client
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('0.0.0.0', server_DHCPPort))
        destination = ('255.255.255.255', client_DHCPPort)

        while 1:
            try:
                print("[DHCP] Waiting for a DHCP discovery...")
                data, address = s.recvfrom(max_Size)
                print("[DHCP] Received a DHCP discovery.")

                print("[DHCP] Sending a DHCP offer...")
                data = DHCP_server.offer_get()
                s.sendto(data, destination)
                while 1:
                    try:
                        print("[DHCP] Waiting for a DHCP request...")
                        data, address = s.recvfrom(max_Size)
                        print("[DHCP] Received DHCP request.")

                        print("[DHCP] Sending a DHCP ACK... \n")
                        data = DHCP_server.pack_get()
                        s.sendto(data, destination)
                        break
                    except:
                        raise
            except:
                raise

    def offer_get():
        op_Code = bytes([0x02])                                 # Type - Response (1 byte)
        hw_Type = bytes([0x01])                                 # Hardware type - Ethernet (1 byte)
        hw_Len = bytes([0x06])                                  # Hardware address length - 6 bytes
        hops = bytes([0x00])                                    # Hops - 0
        XID = bytes([0x39, 0x03, 0xF3, 0x26])                   # Transaction ID - 4 bytes
        secs = bytes([0x00, 0x00])                              # Seconds elapsed - 2 bytes
        flags = bytes([0x00, 0x00])                             # Flags - 2 bytes
        ciaddr = bytes([0, 0, 0, 0])                            # Client IP address - 4 bytes
        yiaddr = bytes([10, 0, 12, 2])                          # Your (client) IP address - 4 bytes
        siaddr = bytes([10, 0, 12, 1])                          # Server IP address - 4 bytes
        giaddr = bytes([10, 0, 12, 1])                          # Gateway IP address - 4 bytes
        c_Hwaddr1 = bytes(C_mac_part1)                          # Client hardware address (4 bytes)
        c_Hwaddr2 = bytes(C_mac_part2)                          # Client hardware address (4 bytes)
        c_Hwaddr3 = bytes(4)                                    # Client hardware address (4 bytes) - Unused
        c_Hwaddr4 = bytes(4)                                    # Client hardware address (4 bytes) - Unused
        c_Hwaddr5 = bytes(192)                                  # Zero padding (192 bytes)
        magic_Cookie = bytes([0x63, 0x82, 0x53, 0x63])          # Magic cookie - 4 bytes
        DHCP_Options1 = bytes([53, 1, 2])                       # DHCP message type - Offer (1 byte)
        DHCP_Options2 = bytes([1, 4, 255, 255, 255, 0])         # Subnet mask - 4 bytes
        DHCP_Options3 = bytes([3, 4, 10, 0, 12, 1])             # Router - 4 bytes
        DHCP_Options4 = bytes([51, 4, 0x00, 0x01, 0x51, 0x80])  # IP address lease time - 4 bytes (1 day)
        DHCP_Options5 = bytes([54, 4, 10, 0, 12, 1])            # Server identifier - 4 bytes
        END_packet = bytes([255])                               # End option - 1 byte

        pack = op_Code + hw_Type + hw_Len + hops + XID + secs + flags + ciaddr + yiaddr + siaddr + giaddr + c_Hwaddr1 + c_Hwaddr2 + c_Hwaddr3 + c_Hwaddr4 + c_Hwaddr5 + magic_Cookie + DHCP_Options1 + DHCP_Options2 + DHCP_Options3 + DHCP_Options4 + DHCP_Options5 + END_packet

        return pack

    def pack_get():
        op_Code = bytes([0x02])                                 # Type - Response (1 byte)
        hw_Type = bytes([0x01])                                 # Hardware type - Ethernet (1 byte)
        hw_Len = bytes([0x06])                                  # Hardware address length - 6 bytes
        hops = bytes([0x00])                                    # Hops - 0
        XID = bytes([0x39, 0x03, 0xF3, 0x26])                   # Transaction ID - 4 bytes
        secs = bytes([0x00, 0x00])                              # Seconds elapsed - 2 bytes
        flags = bytes([0x00, 0x00])                             # Flags - 2 bytes
        ciaddr = bytes([0, 0, 0, 0])                            # Client IP address - 4 bytes
        yiaddr = bytes([10, 0, 12, 2])                          # Your (client) IP address - 4 bytes
        siaddr = bytes([10, 0, 12, 1])                          # Server IP address - 4 bytes
        giaddr = bytes([10, 0, 12, 1])                          # Gateway IP address - 4 bytes
        c_Hwaddr1 = bytes(C_mac_part1)                          # Client hardware address (4 bytes)
        c_Hwaddr2 = bytes(C_mac_part2)                          # Client hardware address (4 bytes)
        c_Hwaddr3 = bytes(4)                                    # Client hardware address (4 bytes) - Unused
        c_Hwaddr4 = bytes(4)                                    # Client hardware address (4 bytes) - Unused
        c_Hwaddr5 = bytes(192)                                  # Zero padding (192 bytes)
        magic_Cookie = bytes([0x63, 0x82, 0x53, 0x63])          # Magic cookie - 4 bytes
        DHCP_Options1 = bytes([53, 1, 5])                       # DHCP message type - ACK (1 byte)
        DHCP_Options2 = bytes([1, 4, 255, 255, 255, 0])         # Subnet mask - 4 bytes
        DHCP_Options3 = bytes([3, 4, 10, 0, 12, 1])             # Router - 4 bytes
        DHCP_Options4 = bytes([51, 4, 0x00, 0x01, 0x51, 0x80])  # IP address lease time - 4 bytes (1 day)
        DHCP_Options5 = bytes([54, 4, 10, 0, 12, 1])            # Server identifier - 4 bytes
        END_packet = bytes([255])                               # End option - 1 byte

        pack = op_Code + hw_Type + hw_Len + hops + XID + secs + flags + ciaddr + yiaddr + siaddr + giaddr + c_Hwaddr1 + c_Hwaddr2 + c_Hwaddr3 + c_Hwaddr4 + c_Hwaddr5 + magic_Cookie + DHCP_Options1 + DHCP_Options2 + DHCP_Options3 + DHCP_Options4 + DHCP_Options5 + END_packet

        return pack


if __name__ == '__main__':
    # Starts the DHCP server
    dhcp_server = DHCP_server()
    dhcp_server.server()
