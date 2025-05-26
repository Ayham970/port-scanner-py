#!/usr/bin/env python3

import socket
import sys
import threading
import argparse
import ipaddress
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3306, 3389, 8080]

def get_args():
    parser = argparse.ArgumentParser(description="Multithreaded Port Scanner with Banner Grabbing")
    parser.add_argument("target", help="Target IP address")
    parser.add_argument("-s", "--start", type=int, help="Start port")
    parser.add_argument("-e", "--end", type=int, help="End port")
    parser.add_argument("-c", "--common", action="store_true", help="Scan only common ports")
    return parser.parse_args()

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def grab_banner(target, port):
    try:
        with socket.socket() as s:
            s.settimeout(1)
            s.connect((target, port))
            banner = s.recv(1024).decode().strip()
            return banner
    except:
        return None

def scan_port(target, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            result = sock.connect_ex((target, port))
            if result == 0:
                print(Fore.GREEN + f"[+] Port {port} is OPEN")
                banner = grab_banner(target, port)
                if banner:
                    print(Fore.YELLOW + f"    Banner: {banner}")
    except Exception:
        pass

def run_scanner(target, ports):
    print(f"\nScanning {target} on {len(ports)} ports...\n")
    threads = []
    for port in ports:
        t = threading.Thread(target=scan_port, args=(target, port))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def main():
    args = get_args()

    if not validate_ip(args.target):
        print(Fore.RED + "[-] Invalid IP address.")
        sys.exit()

    if args.common:
        ports_to_scan = COMMON_PORTS
    else:
        if args.start is None or args.end is None:
            print(Fore.RED + "[-] You must specify --start and --end or use --common.")
            sys.exit()
        if not (0 <= args.start <= 65535) or not (0 <= args.end <= 65535) or args.start > args.end:
            print(Fore.RED + "[-] Invalid port range.")
            sys.exit()
        ports_to_scan = list(range(args.start, args.end + 1))

    try:
        run_scanner(args.target, ports_to_scan)
    except KeyboardInterrupt:
        print(Fore.RED + "\n[-] Scan interrupted by user.")
        sys.exit()

if __name__ == "__main__":
    main()
