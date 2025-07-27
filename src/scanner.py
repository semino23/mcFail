import ipaddress
import random
from ipaddress import IPv4Network
import mcstatus
import sqlite3
from mcstatus.responses import JavaStatusPlayers
DATABASE = "test.sqlite"


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
    cur = sqlite3.connect(DATABASE).cursor()
    cur.execute("""
   create table IF NOT EXISTS `players` (
  `uuid` TEXT not null,
  `name` TEXT not null,
  primary key (`uuid`)
);""")

    cur.execute("""create table IF NOT EXISTS `servers` (
  `address` TEXT not null,
  `slots` INTEGER not null,
  `online` INTEGER not null,
  `version` TEXT not null,
  `description` TEXT not null,
  `motd` TEXT not null,
   primary key (`address`)  
  );""")

    cur.execute("""
create table IF NOT EXISTS`player_log` (
  `player_id` TEXT not null,
  `server_id` INTEGER not null,
  `time` DATETIME not null default current_time
);""")




def insert_player_if_not_exists(log_data:JavaStatusPlayers , db_conn:sqlite3.Connection):
        player_data = [(player.name , player.uuid) for player in log_data.sample]
        print(player_data)
        db_conn.cursor().executemany("INSERT INTO players (name , uuid) VALUES (? , ?)", player_data)
        db_conn.commit()


def insert_server_if_not_exists(log_data:mcstatus.server.JavaServer , db_conn:sqlite3.Connection):
        server_status = log_data.status()

        server_data = (
            server_status.players.max,
            server_status.players.online,
            str(server_status.version),
            str(log_data.address),
            str(server_status.motd.parsed),
            str(server_status.description)
        )

        print(server_data)
        db_conn.cursor().execute("INSERT INTO servers (slots , online , version , address , motd , description) VALUES ( ? , ?, ? , ? , ? , ?)" , server_data)
        db_conn.commit()


def log(log_data: mcstatus.JavaServer ,db_conn:sqlite3.Connection):
        insert_player_if_not_exists(log_data.status().players, db_conn)

        session_log_data = [(player.uuid , log_data.address) for player in log_data.status().players.sample]
        db_conn.cursor().executemany("INSERT INTO player_log (player_id , server_id) (?,?)" , session_log_data)
        db_conn.commit()






def scan(ip_range: IPv4Network):
    ips = ip_range.hosts()
    print(f"scan: {ips}")
    for target in ips:
        try:
            res: mcstatus.JavaServer = mcstatus.JavaServer.lookup(str(target), 5)

            con = sqlite3.connect(DATABASE)
            insert_server_if_not_exists(res, con)
            if res.status().players.sample:
                log(res, con)

        except Exception as e:
            print(e)

