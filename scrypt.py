import ipaddress
import random
from ipaddress import IPv4Network
import mcstatus
import sqlite3


class IpGenerator:
    excluded_networks: list[ipaddress.IPv4Network] = [
        # 🔒 Loopback (localhost only)
        ipaddress.IPv4Network("127.0.0.0/8"),
        # 🏠 Private network ranges (RFC 1918)
        ipaddress.IPv4Network("10.0.0.0/8"),  # Class A private network
        ipaddress.IPv4Network("172.16.0.0/12"),  # Class B private networks
        ipaddress.IPv4Network("192.168.0.0/16"),  # Class C private networks
        # 🔌 Link-local (self-assigned when DHCP fails)
        ipaddress.IPv4Network("169.254.0.0/16"),
        # 🧪 Reserved for software/experimental use
        ipaddress.IPv4Network("0.0.0.0/8"),  # "This" network
        ipaddress.IPv4Network("240.0.0.0/4"),  # Reserved for future use
        # 📡 Multicast addresses (used for streaming, routing protocols, etc.)
        ipaddress.IPv4Network("224.0.0.0/4"),
        # 🌐 Public DNS servers (don't waste scanning these)
        ipaddress.IPv4Network("8.8.8.8/32"),  # Google DNS
        ipaddress.IPv4Network("8.8.4.4/32"),  # Google secondary
        ipaddress.IPv4Network("1.1.1.1/32"),  # Cloudflare DNS
        ipaddress.IPv4Network("1.0.0.1/32"),  # Cloudflare secondary
        ipaddress.IPv4Network("9.9.9.9/32"),  # Quad9 DNS
        # ☁️ Cloud metadata services (AWS, Azure, GCP)
        ipaddress.IPv4Network("169.254.169.254/32"),  # Metadata service for cloud VMs
        # 🧱 Internet infrastructure / non-game hosts (optional)
        ipaddress.IPv4Network("4.2.2.1/32"),  # Level3 DNS
        ipaddress.IPv4Network("4.2.2.2/32"),
        ipaddress.IPv4Network("4.2.2.3/32"),
        ipaddress.IPv4Network("4.2.2.4/32"),
        ipaddress.IPv4Network("4.2.2.5/32"),
        ipaddress.IPv4Network("4.2.2.6/32"),
    ]

    @staticmethod
    def is_excluded(generated_subnet: str) -> bool:
        target = ipaddress.IPv4Network(generated_subnet)
        return any(target.subnet_of(excl) for excl in IpGenerator.excluded_networks)

    @staticmethod
    def generate_ips() -> list[str]:
        ips: list[str] = []
        for i in range(255):
            for y in range(255):
                ip = f"{i}.{y}.0.0/16"
                if not IpGenerator.is_excluded(ip):
                    ips.append(ip)
        random.shuffle(ips)
        return ips


def prepare_database():
    cur = sqlite3.connect(":memory:").cursor()
    cur.execute("""
   create table `players` (
  `uuid` TEXT not null,
  `name` TEXT not null,
  primary key (`uuid`)
);""")

    cur.execute("""create table `server` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT not null,
  `slots` INTEGER null,
  `version` TEXT null);""")

    cur.execute("""
create table `player_log` (
  `player_id` TEXT not null,
  `server_id` INTEGER not null,
  `column_3` DATETIME not null default current_time
);""")


def log_occurance(server: mcstatus.responses.JavaStatusResponse):
    print(f"found server:\t{server.players}")
    if server.players.sample:
        print(f"with players:\t{server.players.sample}")
    else:
        print("with no Player")


def scan(ip_range: IPv4Network):
    ips = ip_range.hosts()
    print(f"scan: {ips}")
    for target in ips:
        try:
            res: mcstatus.JavaServer = mcstatus.JavaServer.lookup(str(target), 5)
            log_occurance(res.status())
        except:
            pass
            # print(e)
            # print(type(res))


if __name__ == "__main__":
    prepare_database()
    # generated_ips = IpGenerator.generate_ips()

    scan(IPv4Network("127.0.0.1/32"))
