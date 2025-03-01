from scapy.all import ARP, Ether, srp

# Create ARP request packet
arp_request = ARP(pdst="192.168.1.0/24")
broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
packet = broadcast/arp_request

# Send packet and capture responses
result = srp(packet, timeout=3, verbose=0)[0]

# Display results
print("IP\t\t\tMAC Address")
print("-----------------------------------------")
for sent, received in result:
    print(f"{received.psrc}\t\t{received.hwsrc}")