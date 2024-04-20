import requests
import socket
import os
import yaml
import logging
import time
from retry import retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s;%(levelname)s;%(message)s")


def load_config() -> dict:
    app_dir = os.path.dirname(os.path.realpath(__file__))

    if not os.path.exists(f'{app_dir}/config.yaml'):
        raise Exception(f'{app_dir}/config.yaml not found')

    with open(f'{app_dir}/config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())

    return config


def save_config(config: dict) -> bool:
    app_dir = os.path.dirname(os.path.realpath(__file__))

    try:
        with open(f'{app_dir}/config.yaml', 'w') as f:
            yaml.safe_dump(config, f)
        return True
    except Exception as e:
        logging.error(e)
        return False


def check_ip_addresses(hosts: dict) -> list:
    ip_changes = False
    for host in hosts:
        ip = str(socket.gethostbyname(hosts[host]["fqdn"])) + "/32"
        if ip != hosts[host]["last_known_ip"]:
            hosts[host]["last_known_ip"] = ip
            logging.info(f"{host}: {hosts[host]["fqdn"]} changed to {ip}")
            ip_changes = True
        else:
            logging.info(f"{host}: {hosts[host]["fqdn"]} no changes")
            continue
    if ip_changes:
        return [hosts[host]["last_known_ip"] for host in hosts]

    return []


@retry()
def update_linode_firewall(config: dict, api_token: str):
    ip_addresses = check_ip_addresses(config["hosts"])

    if not ip_addresses:
        logging.info("IPs not changed")
        return

    headers = {"Authorization": f"Bearer {api_token}"}
    url = "https://api.linode.com/v4/networking/firewalls"
    response = requests.get(url, headers=headers)
    fw_rules = response.json()

    for firewall in fw_rules["data"]:
        for direction in firewall["rules"]:
            if direction not in config["firewall_rules"]:
                break
            for rule in firewall["rules"][direction]:
                if rule["label"] not in config["firewall_rules"][direction]:
                    break
                rule["addresses"]["ipv4"] = ip_addresses
                update_url = f"https://api.linode.com/v4/networking/firewalls/{firewall["id"]}/rules"
                response = requests.put(update_url, headers=headers, json=firewall["rules"])
                if response.ok:
                    logging.info(f"{firewall["label"]} {direction} {rule["label"]} updated")
                else:
                    raise Exception("Error whiling updating firewall rules")

    save_config(config)


def main():

    logging.info("Start")
    api_token = os.environ.get('api_token')
    if not api_token:
        logging.info("No Linode API Token found")
        exit()

    config = load_config()
    sleep_interval = int(config["interval"]) * 60

    while True:
        update_linode_firewall(config, api_token)
        logging.info(f"Sleeping for {sleep_interval/60} minutes")
        time.sleep(sleep_interval)


if __name__ == '__main__':
    main()
