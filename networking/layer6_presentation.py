# Layer 6: Presentation Layer
# Translates data between application and network formats, handling encryption and compression.
# Protocols: SSL/TLS, MIME (JPEG, MPEG, etc.), Data compression formats
#
# Architecture: Manages data transformation, encryption, and character encoding

# SSL/TLS implementation
# To run:
# 1. Within `networking` folder after creating conda environment: `conda activate networking_env`
# 2. Run: `python -c "import layer6_presentation; layer6_presentation.secure_client()"`
# 3. Check output for connection details and response

import ssl
import socket

def secure_client(response_output_limit=650):
    # Create a standard socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Wrap with SSL/TLS
    context = ssl.create_default_context()
    secure_sock = context.wrap_socket(sock, server_hostname='example.com')
    
    try:
        # Connect to secure server
        secure_sock.connect(('example.com', 443))
        
        # Get certificate info
        cert = secure_sock.getpeercert()
        print(f"Connected to: {secure_sock.server_hostname}")
        print(f"Using cipher: {secure_sock.cipher()}")
        print(f"Certificate expires: {cert['notAfter']}")
        
        # Send HTTP request
        request = "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
        secure_sock.send(request.encode())
        
        # Get response
        response = secure_sock.recv(4096)
        print(f'{response.decode()[:response_output_limit]}\n...')
    finally:
        secure_sock.close()