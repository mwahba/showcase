# Layer 7: Application Layer
# Provides network services directly to end-users and applications.
# Protocols: HTTP/HTTPS, FTP, SMTP/POP3/MAP, DNS, DHCP, Telnet, SSH, others
#
# Architecture: Implements specific application-level protocols, data exchange, and user interfaces.

# HTTP Request and Response
# To run:
# 1. Within `networking` folder after creating conda environment: `conda activate networking_env`
# 2. Run: `python -c "import layer7_application; layer7_application.http_request_example()"`
# 3. Check output for response details

import requests

def http_request_example():
    # Simple GET request
    response = requests.get('https://api.github.com/users/mwahba')
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    # Parse JSON response
    data = response.json()
    print(f"Username: {data['login']}")
    print(f"Followers: {data['followers']}")
    
    # POST request with data
    post_response = requests.post(
        'https://httpbin.org/post',
        data={'key': 'value'},
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    print(f"POST Status: {post_response.status_code}")
    print(f"POST Response: {post_response.json()}")