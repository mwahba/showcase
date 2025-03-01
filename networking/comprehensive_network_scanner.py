"""
Comprehensive Network Scanner

This comprehensive network scanner demonstrates how to analyze and troubleshoot 
multiple networking layers in a single application. It performs:

Layer 2 scanning with ARP to map devices
Layer 3 connectivity testing with ICMP pings
Layer 4 port scanning
Layer 7 application-level analysis

To run the scanner, ensure you have the necessary dependencies in your environment.

1. After creating a conda environment, activate it: `conda activate networking_env`
2. Run the script using sudo within the `networking` folder:
    `sudo $(which python) -m comprehensive_network_scanner`
"""
import socket
import subprocess
import ipaddress
import requests
import dns.resolver
import concurrent.futures
import time
from scapy.all import ARP, Ether, srp

class NetworkScanner:
    """A comprehensive network scanner that analyzes multiple networking layers."""
    
    def __init__(self, target_network):
        """Initialize scanner with target network in CIDR notation (e.g., '192.168.1.0/24')"""
        self.target_network = target_network
        self.network = ipaddress.ip_network(target_network)
        self.results = {
            'l2': {},  # MAC addresses and vendors
            'l3': {},  # IP connectivity
            'l4': {},  # Open ports
            'l7': {}   # Service identification
        }
    
    def scan_l2(self):
        """Scan Layer 2 (Data Link) - ARP scan to discover devices"""
        print(f"[+] Scanning Layer 2 (Data Link) on {self.target_network}")
        
        arp_request = ARP(pdst=self.target_network)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = broadcast/arp_request
        
        try:
            result = srp(packet, timeout=3, verbose=0)[0]
            
            for sent, received in result:
                self.results['l2'][received.psrc] = {
                    'mac_address': received.hwsrc,
                    'vendor': self._get_vendor(received.hwsrc)
                }
            
            print(f"[+] Layer 2 scan complete. Found {len(self.results['l2'])} devices")
        except Exception as e:
            print(f"[-] Layer 2 scan error: {e}")
    
    def scan_l3(self):
        """Scan Layer 3 (Network) - ICMP ping to check connectivity"""
        print(f"[+] Scanning Layer 3 (Network) on {self.target_network}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            ip_list = [str(ip) for ip in self.network.hosts()]
            future_to_ip = {executor.submit(self._ping_host, ip): ip for ip in ip_list}
            
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    is_alive = future.result()
                    if is_alive:
                        if ip not in self.results['l3']:
                            self.results['l3'][ip] = {'status': 'active'}
                except Exception as e:
                    print(f"[-] Error pinging {ip}: {e}")
        
        print(f"[+] Layer 3 scan complete. Found {len(self.results['l3'])} active hosts")
    
    def scan_l4(self, ports=None):
        """Scan Layer 4 (Transport) - TCP port scan"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 443, 445, 3306, 3389, 8080]
        
        print(f"[+] Scanning Layer 4 (Transport) for common ports: {ports}")
        
        active_ips = list(self.results['l3'].keys())
        if not active_ips:
            print("[-] No active hosts found at Layer 3. Run scan_l3() first.")
            return
        
        for ip in active_ips:
            self.results['l4'][ip] = {'open_ports': {}}
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                future_to_port = {executor.submit(self._check_port, ip, port): port for port in ports}
                
                for future in concurrent.futures.as_completed(future_to_port):
                    port = future_to_port[future]
                    try:
                        is_open = future.result()
                        if is_open:
                            self.results['l4'][ip]['open_ports'][port] = True
                    except Exception as e:
                        print(f"[-] Error checking {ip}:{port}: {e}")
        
        total_open = sum(len(host_data['open_ports']) for host_data in self.results['l4'].values())
        print(f"[+] Layer 4 scan complete. Found {total_open} open ports across all hosts")
    
    def scan_l7(self):
        """Scan Layer 7 (Application) - Basic service identification"""
        print(f"[+] Scanning Layer 7 (Application) services")
        
        for ip in self.results['l4']:
            self.results['l7'][ip] = {'services': {}}
            
            for port in self.results['l4'][ip]['open_ports']:
                service = self._identify_service(ip, port)
                if service:
                    self.results['l7'][ip]['services'][port] = service
        
        print(f"[+] Layer 7 scan complete")
    
    def run_dns_check(self, domain):
        """Check DNS resolution for a domain (Layer 7)"""
        print(f"[+] Checking DNS resolution for {domain}")
        
        try:
            answers = dns.resolver.resolve(domain, 'A')
            results = []
            
            for rdata in answers:
                ip = str(rdata)
                results.append(ip)
                
                # Add to Layer 3 results if in our target network
                if ipaddress.ip_address(ip) in self.network:
                    if ip not in self.results['l3']:
                        self.results['l3'][ip] = {'status': 'active'}
                    
                    if 'hostnames' not in self.results['l3'][ip]:
                        self.results['l3'][ip]['hostnames'] = []
                    
                    self.results['l3'][ip]['hostnames'].append(domain)
            
            print(f"[+] DNS resolution for {domain}: {', '.join(results)}")
            return results
        except Exception as e:
            print(f"[-] DNS resolution error for {domain}: {e}")
            return []
    
    def http_check(self, ip, port=80, use_ssl=False):
        """Check HTTP service (Layer 7)"""
        protocol = "https" if use_ssl else "http"
        url = f"{protocol}://{ip}:{port}"
        
        try:
            response = requests.get(url, timeout=3, verify=False)
            server = response.headers.get('Server', 'Unknown')
            
            if ip in self.results['l7'] and 'services' in self.results['l7'][ip]:
                self.results['l7'][ip]['services'][port] = {
                    'type': f"{protocol.upper()}",
                    'status_code': response.status_code,
                    'server': server,
                    'title': self._extract_title(response.text)
                }
            
            print(f"[+] HTTP check for {url}: {response.status_code} ({server})")
            return response
        except requests.exceptions.RequestException as e:
            print(f"[-] HTTP check error for {url}: {e}")
            return None
    
    def generate_report(self):
        """Generate a comprehensive network report"""
        print("\n===== NETWORK SCAN REPORT =====")
        print(f"Target Network: {self.target_network}")
        print(f"Scan Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("===============================\n")
        
        # Layer 2 Report
        print("--- LAYER 2 (Data Link) ---")
        if self.results['l2']:
            for ip, data in self.results['l2'].items():
                print(f"IP: {ip} | MAC: {data['mac_address']} | Vendor: {data['vendor']}")
        else:
            print("No Layer 2 data available")
        print("")
        
        # Layer 3 Report
        print("--- LAYER 3 (Network) ---")
        if self.results['l3']:
            for ip, data in self.results['l3'].items():
                host_info = f"IP: {ip} | Status: {data['status']}"
                if 'hostnames' in data:
                    host_info += f" | Hostnames: {', '.join(data['hostnames'])}"
                print(host_info)
        else:
            print("No Layer 3 data available")
        print("")
        
        # Layer 4 Report
        print("--- LAYER 4 (Transport) ---")
        if self.results['l4']:
            for ip, data in self.results['l4'].items():
                if data['open_ports']:
                    ports_str = ', '.join(str(port) for port in data['open_ports'])
                    print(f"IP: {ip} | Open Ports: {ports_str}")
                else:
                    print(f"IP: {ip} | No open ports")
        else:
            print("No Layer 4 data available")
        print("")
        
        # Layer 7 Report
        print("--- LAYER 7 (Application) ---")
        if self.results['l7']:
            for ip, data in self.results['l7'].items():
                if 'services' in data and data['services']:
                    print(f"IP: {ip}")
                    for port, service in data['services'].items():
                        if isinstance(service, dict):
                            service_str = ' | '.join(f"{k}: {v}" for k, v in service.items())
                            print(f"  - Port {port}: {service_str}")
                        else:
                            print(f"  - Port {port}: {service}")
                else:
                    print(f"IP: {ip} | No service information")
        else:
            print("No Layer 7 data available")
        print("")
    
    def _ping_host(self, ip):
        """Helper method to ping a host"""
        try:
            # Adjust command based on operating system
            param = '-n' if subprocess.call('which ping', shell=True, stdout=subprocess.PIPE) else '-c'
            command = ['ping', param, '1', '-W', '1', ip]
            
            return subprocess.call(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            ) == 0
        except:
            return False
    
    def _check_port(self, ip, port):
        """Helper method to check if a port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    
    def _identify_service(self, ip, port):
        """Basic service identification based on common ports"""
        common_ports = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            443: 'HTTPS',
            445: 'SMB',
            3306: 'MySQL',
            3389: 'RDP',
            8080: 'HTTP-Proxy'
        }
        
        if port in common_ports:
            # For HTTP/HTTPS, try to get more details
            if port in [80, 8080]:
                try:
                    self.http_check(ip, port)
                    return self.results['l7'][ip]['services'].get(port, common_ports[port])
                except:
                    pass
            elif port == 443:
                try:
                    self.http_check(ip, port, use_ssl=True)
                    return self.results['l7'][ip]['services'].get(port, common_ports[port])
                except:
                    pass
                    
            return common_ports[port]
        else:
            return "Unknown"
    
    def _get_vendor(self, mac):
        """Get vendor from MAC address (simplified)"""
        # In a real implementation, this would use a MAC vendor database
        return "Unknown Vendor"
    
    def _extract_title(self, html_content):
        """Extract title from HTML content"""
        try:
            start = html_content.find('<title>')
            end = html_content.find('</title>')
            if start != -1 and end != -1:
                return html_content[start+7:end].strip()
        except:
            pass
        return "No title"

# Example usage
if __name__ == "__main__":
    # Create scanner for local network
    scanner = NetworkScanner('192.168.4.0/24')
    
    # Run scans
    scanner.scan_l2()  # Data Link layer scan (ARP)
    scanner.scan_l3()  # Network layer scan (ICMP)
    scanner.scan_l4()  # Transport layer scan (TCP ports)
    scanner.scan_l7()  # Application layer scan (service identification)
    
    # Additional application layer checks
    scanner.run_dns_check('example.com')
    
    # Generate report
    scanner.generate_report()