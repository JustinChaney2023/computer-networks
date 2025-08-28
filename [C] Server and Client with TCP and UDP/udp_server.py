import socket

# Create a UDP socket 
# AF_INET indicates IPv4 addresses can be used.
# SOCK_DGRAM: with connectionless service for datagrams
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to a specific address and port
server_address = ('localhost', 12345)
server_socket.bind(server_address)

print("UDP server is waiting for incoming connections...")

while True:
    # Receive data from the client, up to a maximum of 1024 Bytes (i.e., 1 KB).
    data, client_address = server_socket.recvfrom(1024)

    # Decode the received data, format with the variables involved, and display the string.
    print(f"Received data from {client_address}: {data.decode()}")
    
    # Create an acknowledgment.
    ack = "Hey, this is the server acknowledging the receipt of your data: " + data.decode()

    # Encode the acknowledgment and send to client.
    server_socket.sendto(ack.encode(), client_address)
