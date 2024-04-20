Since Linode Firewall Rules only allow IP addresses, and my ISP keep renewing IP address perdically, therefore I create this script to monitor IP changes based on DDNS and update corresponding rules based on Rule Label.


### Build:

git clone https://github.com/mr-0v0/linode_fw_rules_ddns

cd linode_fw_rules_ddns

docker build -t linode_fw_rules_ddns:latest .

### Setup:

Customize config_sample.yaml and save it as config.yaml.

Information needed for update:
- Rule Label
- FQDN of DDNS


### Run:

docker run -it -v {PWD}/config.yaml:/app/config.yaml linode_fw_rules_ddns:latest

