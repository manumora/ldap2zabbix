
# LDAP to Zabbix
Migration hosts from LDAP to Zabbix

## Installation
- python3 -m venv venv
- source venv/bin/activate
- pip install -r requirements

## Configuration
Fill the following parameters
> ZABBIX_SERVER
> ZABBIX_USER
> ZABBIX_PASSWORD
> ZABBIX_GROUP_PANEL
> ZABBIX_GROUP_AIO
> ZABBIX_GROUP_SIA
> LDAP_SERVER
> LDAP_BASE
> LDAP_USER
> LDAP_PASSWORD

## Execution
python3 ldap2zabbix.py