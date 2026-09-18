# LDAP to Zabbix

Migration of hosts from LDAP to Zabbix.

This script reads the DNS records stored in an LDAP directory and registers the
matching machines in Zabbix as monitored hosts, so that the inventory kept in
LDAP stays the single source of truth and there is no need to add hosts to
Zabbix by hand.

## How it works

1. It binds anonymously to the LDAP server and reads the DHCP configuration
   entry (`cn=DHCP Config`, `cn=INTERNAL`) to work out the internal domain name.
2. It searches the `dc=<domain>,ou=hosts` subtree for the host entries whose
   name matches any of the configured suffixes, and collects their `dc`
   (hostname) and `aRecord` (IP address) attributes.
3. It logs in to the Zabbix API and, for every hostname found, checks whether
   the host already exists. Existing hosts are reported and left untouched;
   missing hosts are created with an agent interface (DNS based, port 10050,
   using `<hostname>.<domain>`) and added to the configured host group.

The run is idempotent: executing the script repeatedly only creates the hosts
that are not yet in Zabbix and never modifies or deletes existing ones.

## Requirements

- Python 3
- Network access to the LDAP server and to the Zabbix frontend API
- A Zabbix user with permission to create hosts

## Installation

- python3 -m venv venv
- source venv/bin/activate
- pip install -r requirements

## Configuration

Edit the constants at the top of `ldap2zabbix.py`:

| Parameter | Description |
| --- | --- |
| `ZABBIX_SERVER` | URL of the Zabbix frontend, for example `http://192.168.1.10` |
| `ZABBIX_USER` | Zabbix user with rights to create hosts |
| `ZABBIX_PASSWORD` | Password for that user |
| `ZABBIX_GROUP` | ID of the Zabbix host group the new hosts are added to |
| `LDAP_SERVER` | Address of the LDAP server |
| `LDAP_BASE` | Base DN of the directory, for example `dc=instituto,dc=extremadura,dc=es` |
| `LDAP_USER` | Administrator DN (kept for reference, the search binds anonymously) |
| `LDAP_PASSWORD` | Password for that DN |
| `HOST_SUFFIXES` | List of hostname suffixes to import |

### Choosing which hosts are imported

`HOST_SUFFIXES` holds the hostname endings that should be monitored. The LDAP
search filter is built from that list, so there is no need to write the filter
by hand:

```python
HOST_SUFFIXES = ["panel", "aio", "sia"]
# produces (|(dc=*-panel)(dc=*-aio)(dc=*-sia))
```

Add or remove entries from the list to widen or narrow the selection.

## Execution

```
python3 ldap2zabbix.py
```

Each host produces one line of output saying whether it already existed, was
created successfully, or failed to be created.

## Author

Manuel Mora Gordillo, <manuel.mora.gordillo @no-spam@ gmail.com>

## Licence

GNU General Public License v3 or later. See the header of `ldap2zabbix.py`.
