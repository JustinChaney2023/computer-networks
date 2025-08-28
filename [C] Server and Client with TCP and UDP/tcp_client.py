import socket

# Create a socket object. This time, connection oriented!
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('127.0.0.1', 12345)
client_socket.connect(server_address)

try:
    while True:
        message = input("Enter a message to send to the server (or '.' to quit): ")
        
        if message == '.':
            break  # Exit and close the connection
        
        # Encode and send the message to the server
        client_socket.sendall(message.encode())

        # Receive the response from the server
        data = client_socket.recv(1024)
        print("Received from server: {}".format(data.decode()))

except Exception as e:
    print("Error: {}".format(e))

finally:
    # Clean up the connection
    client_socket.close()
