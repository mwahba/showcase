# Layer 4: Transport Layer
# Manages end-to-end communication between hosts and data flow control,
# handling port numbers and data integrity.
#
# Architecture: Implments ports, connection handling, flow control, and error recovery.
#
# Protocols: TCP, UDP; others: SCTP, DCCP

# To run:
# 1. From `networking` folder after creating conda environment: `conda activate networking_env`   
# 2. Start Server: `python -c "import layer4_transport; layer4_transport.start_tcp_server(host='127.0.0.1', port=12345)"`
# 3. In another CLI window, start Client: `python -c "import layer4_transport; layer4_transport.tcp_client(host='127.0.0.1', port=12345, message='Hello, server')"`
# 5. Check server and client output for messages

# TCP Server
import socket

def start_tcp_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    
    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection from {address}")
        data = client_socket.recv(1024)
        if data:
            print(f"Received: {data.decode('utf-8')}")
            client_socket.send(b"Message received: " + data)
        client_socket.close()

# TCP Client
def tcp_client(host='127.0.0.1', port=12345, message="Hello, server!"):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        client_socket.send(message.encode('utf-8'))
        response = client_socket.recv(1024)
        print(f"Response: {response.decode('utf-8')}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()