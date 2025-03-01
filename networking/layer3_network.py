import subprocess
from scapy.all import traceroute

# Layer 3: Network Layer
# Routes data between different networks, handling logical addressing.
# Protocols: IPv4/IPv6, ICMP, ARP, OSPF routing, BGP routing

def ping_host(host):
    """Ping a host and return True if it responds, False otherwise."""
    # Option params: -c count, -W timeout in seconds
    command = ['ping', '-c', '1', '-W', '1', host]
    
    try:
        output = subprocess.check_output(command).decode('utf-8')
        if "1 received" in output:
            return True, output
        return False, output
    except subprocess.CalledProcessError:
        return False, "Host unreachable"

# Test a host
success, result = ping_host("8.8.8.8")
print(f"Success: {success}")
print(result)

def trace_route(destination):
    """Trace the route to a destination and return the hops."""
    # Option params: -n numeric, -q max hops, -w timeout in seconds
    # command = ['tracert', '-n', '-q', '1', '-w', '1', destination]
    
    try:
        output = traceroute(destination, maxttl=30, verbose=0)
        # output = subprocess.check_output(command).decode('utf-8')
        return True, output
    except subprocess.CalledProcessError:
        return False, "Unable to trace route"
    
# Test a destination
success, result = trace_route("8.8.8.8")
print(f"Success: {success}")
print(result)
