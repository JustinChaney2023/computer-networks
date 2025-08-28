import socket

# Create a UDP socket.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address and port
server_address = ('localhost', 12345)

while True:
    message = input("Enter a message to send to the server (or '.' to quit): ")
    
    if message == '.':
        break      # Exit and close the connection

    # Encode and send the message to the server
    client_socket.sendto(message.encode(), server_address)

    # Receive the response from the server
    response, serv_address = client_socket.recvfrom(1024)
    print(f"Received response from server {serv_address}: {response.decode()}")

# Close the socket
client_socket.close()
