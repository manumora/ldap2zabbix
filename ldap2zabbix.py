##############################################################################
# -*- coding: utf-8 -*-
# Project:      LDAP to Zabbix
# Module:       ldap2zabbix.py
# Purpose:      Create zabbix hosts from ldap entries
# Language:     Python 3
# Date:         18-Dec-2023
# Ver:          18-Dec-2023
# Author:       Manuel Mora Gordillo
# Copyright:    2023 - Manuel Mora Gordillo <manuel.mora.gordillo @no-spam@ gmail.com>
#
# LDAP to Zabbix is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# LDAP to Zabbix is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
##############################################################################

from ldap3 import Server, Connection, ALL, SUBTREE
from pyzabbix import ZabbixAPI

ZABBIX_SERVER = "http://IP_SERVIDOR_ZABBIX"
ZABBIX_USER = "Admin"
ZABBIX_PASSWORD = "zabbix"
ZABBIX_GROUP = "2"

LDAP_SERVER = "IP_SERVIDOR_LDAP"
LDAP_BASE = "dc=instituto,dc=extremadura,dc=es"
LDAP_USER = "cn=admin,ou=people,%s" % LDAP_BASE
LDAP_PASSWORD = "PASSWORD_LDAP"


class LdapConnection(object):
  def __init__(self, host, user="", password=""):
    self.host = host
    self.user = user
    self.password = password

  def connectauth(self):
    server = Server(self.host, get_info=ALL)
    self.connectauth = Connection(server, "", "")
    self.connectauth.bind()
    return True

  def domain(self):
    config = self.search("cn=DHCP Config", "(cn=INTERNAL)", ["dhcpOption"])
    return config[0]["dhcpOption"][4].replace('"','').replace('domain-name ','')

  def search(self, baseDN, filter, retrieveAttributes):
    self.connectauth.search("%s,%s" % (baseDN, LDAP_BASE), filter, SUBTREE, attributes=retrieveAttributes)
    entries = list()
    for entry in self.connectauth.entries:
      entries.append(entry)
    return entries

  def getHostnames(self):
    hostnames_data = dict()
    search = self.search("dc=" + self.domain() + ",ou=hosts","(|(dc=*-panel)(dc=*-aio)(dc=*-sia))", ["dc", "aRecord"])
    for s in search:
      hostnames_data[s['dc'][0]] = s['aRecord'][0]
    return hostnames_data

def main():
  l = LdapConnection(LDAP_SERVER)
  l.connectauth()
  domain = l.domain()
  hostnames = l.getHostnames()

  zapi = ZabbixAPI(ZABBIX_SERVER)
  zapi.login(ZABBIX_USER, ZABBIX_PASSWORD)

  for hostname, ip in hostnames.items():
    host_info = zapi.host.get(filter={"host": hostname}, selectInterfaces="extend")
    if host_info:
      print(hostname + " already exists.")
    else:
      new_host = dict(
        host=hostname,
        interfaces=[
          dict(
            type=1,
            main=1,
            useip=0,
            ip=ip,
            dns="%s.%s" % (hostname, domain),
            port="10050"
          )
        ],
        groups=[
          dict(
            groupid=ZABBIX_GROUP
          )
        ]
      )
      result = zapi.host.create(**new_host)

      if result.get("hostids") and len(result.get("hostids")) > 0:
        print("---> %s created succesfully" % hostname)
      else:
        print("Error creating host %s" % hostname)

  zapi.user.logout()

if __name__ == '__main__':
  main()
