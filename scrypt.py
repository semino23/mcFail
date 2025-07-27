from ipaddress import IPv4Network

from src.scanner import scan, IpGenerator

ips = IpGenerator.generate_ips()

#while False:
    # continuous scan

#for i in ips:
#    scan(i)

scan(IPv4Network("127.0.0.1/32"))