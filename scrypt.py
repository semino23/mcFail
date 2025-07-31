from ipaddress import IPv4Network
from time import sleep
from src.scanner import scan, IpGenerator

ips = IpGenerator.generate_ips()

while True:
    for ipRange in ips:
        scan(ipRange)
    # sleeps 20 minutes before another scan
    sleep(20 * 60)

