#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Challenge4 - Write a script that uses Cloud DNS to create a new A record
# when passed a FQDN and IP address as arguments.

# Copyright 2013 Scott Gilbert
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Adds an "A record" if an IPv4 address is supplied, or a "AAAA record" if 
# an IPv6 address is supplied.
#
# Required Parameters:
#  FQDN
#  IP (either IPv4 or IPv6)
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --region REGION           Region (DFW or ORD)


import sys
import os
import re
import socket
import argparse
import pyrax
import challenge1 as c1

def create_dns_record(dns, FQDN, IPAddr, RcdType):
  """ Create specified DNS record in CloudDNS
  
  First attempt to add record to zone matching specified name.

  If that fails, next try to add record to zone of specified name with
  first element removed (ie: if "www.example.com" is specified, try adding
  to "example.com" zone.

  If that also fails, next try creating a new zone for the specified name.

  If that also fails, then give up and report error.
  """

  # if FQDN exists as a domain, add record to that domain
  # elif stripping off the first part results in a domain that exists, add to
  #   that domain
  # else
  #     create new domain of FQDN
  #     add rcd to that domain
  dns_rec = {"type": RcdType,
            "name": FQDN,
            "data": IPAddr,
            "ttl": 300}
  try:
    domain = dns.find(name=FQDN)
  except pyrax.exceptions.NotFound:
    try:
      domain = dns.find(name=FQDN.split('.',1)[1])
    except pyrax.exceptions.NotFound:
      try:
        domain = dns.create(name=FQDN, ttl=300,
                            emailAddress='dnsmaster@%s' % FQDN)
      except pyrax.exceptions.DomainCreationFailed as err:
        print "Domain does not exist, and attempt to create it",
        print "failed with:" 
        print err
        sys.exit(5)

  rec = domain.add_record(dns_rec)
  print "DNS record %s %s %s added to zone %s" % (FQDN, RcdType, IPAddr, 
	domain.name)

def is_valid_ipv4_address(address):
  """Return True if parameter is a valid IPv4 address, otherwise return
  False
  """
  try:
    addr= socket.inet_pton(socket.AF_INET, address)
  except AttributeError: 
    try:
      addr= socket.inet_aton(address)
    except socket.error:
      return False
    return address.count('.') == 3
  except socket.error:
    return False
  return True

def is_valid_ipv6_address(address):
  """Return True if parameter is a valid IPv6 address, otherwise return
  False
  """
  try:
    addr=socket.inet_pton(socket.AF_INET6, address)
  except socket.error:
    return False
  return True

def is_valid_hostname(hostname):
  """Check for basic validity of a FQDN
  Return True if the FQDN is valid, False otherwise.
  """
  if len(hostname) > 255:
    return False
  if hostname[-1:] == ".":
    hostname = hostname[:-1] # strip exactly one dot from the right, if present
  allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
  return all(allowed.match(x) for x in hostname.split("."))

if __name__ == "__main__":
  print "\nChallenge4 - Write a script that uses Cloud DNS to create a new A"
  print "record when passed a FQDN and IP address as arguments.\n\n"

  parser = argparse.ArgumentParser()
  parser.add_argument("FQDN",  help="Fully Qualified Domain Name")
  parser.add_argument("IP", help="IP address (IPv4 or IPv6)")
  parser.add_argument("--region", default='DFW',
                      help="Region (DFW or ORD)")
  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if c1.is_valid_region(args.region):
    dns = pyrax.connect_to_cloud_dns(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  if not is_valid_hostname(args.FQDN):
    print "This does not appear to be a valid host name: %s" % args.FQDN
    sys.exit(3)

  if is_valid_ipv4_address(args.IP):
    create_dns_record(dns, args.FQDN, args.IP, 'A')
  elif is_valid_ipv6_address(args.IP):
    create_dns_record(dns, args.FQDN, args.IP, 'AAAA')
  else:
    print 'The specified IP address "%s" is not valid' % IPAddr
    sys.exit(4)

# vim: ts=2 sw=2 tw=78 expandtab
