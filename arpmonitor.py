import os
import ipaddress
from tqdm import tqdm

def scan():
    hosts = []
    found = 0
    not_found = 0
    interfaces = os.popen('ip link show').read().strip().split('\n')
    interfaces_list = []
    for index, interface in enumerate(interfaces):
        if interface and not interface.startswith(' '):
            interface_name = interface.split(':')[1].strip()
            ip_info = os.popen(f'ip addr show {interface_name} | grep inet').read().strip()
            if ip_info:
                ip = ip_info.split()[1].split('/')[0]
                interfaces_list.append((index,interface_name,ip))
    interfaces_list = [i for i in interfaces_list if i[1].startswith("eth") or i[1].startswith("wl") or i[1].startswith("t")]
    if interfaces_list:
        print("List of identified interfaces:")
        for index, interface, ip in interfaces_list:
            print(f"{interface} - {ip}")
        interface_name = input("Choose the name of the interface you want to scan: ")
        interface_to_scan = [i for i in interfaces_list if i[1] == interface_name][0]
        ip = interface_to_scan[2]
        network = ipaddress.IPv4Network((ip+"/24"), strict=False)
        print(f"Scanned Network: {network}")
        for host in tqdm(network.hosts(), desc="Scanning", unit="host"):
            ip_to_check = str(host)
            # Send ARP request
            response = os.popen(f'arping -I {interface_name} -c 1 {ip_to_check}').read()
            if "bytes from" in response:
                # Extract the MAC address
                mac = response.split("at ")[1].split(" ")[0]
                hosts.append((ip_to_check, mac))
                found += 1
                print("\033[92m"+ip_to_check+"\033[0m") # Print the IP in green
            else:
                not_found += 1
        print("\033[92mFound :",found,"\033[0m")
        print("\033[91mNot Found :",not_found,"\033[0m")
    return hosts

print(scan())



