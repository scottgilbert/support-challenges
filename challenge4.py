#!/usr/bin/env python
# Challenge4 - Write a script that uses Cloud DNS to create a new A record
# when passed a FQDN and IP address as arguments.
# Author: Scott Gilbert

# Requires the following two parameters:
#  FQDN
#  IP (either IPv4 or IPv6)
#
# Adds an "A record" if an IPv4 address is supplied, or a "AAAA record" if 
# an IPv6 address is supplied.

import sys, os, socket, argparse
import pyrax

def createDNSRecord(dns, FQDN, IPAddr, RcdType):
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

if __name__ == "__main__":
  print "\nChallenge4 - Write a script that uses Cloud DNS to create a new A"
  print "record when passed a FQDN and IP address as arguments.\n\n"

  parser = argparse.ArgumentParser()
  parser.add_argument("FQDN",  help="Fully Qualified Domain Name")
  parser.add_argument("IP", help="IP address (IPv4 or IPv6)")
  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  dns = pyrax.cloud_dns

  if is_valid_ipv4_address(args.IP):
    createDNSRecord(dns, args.FQDN, args.IP, 'A')
  elif is_valid_ipv6_address(args.IP):
    createDNSRecord(dns, args.FQDN, args.IP, 'AAAA')
  else:
    print 'The specified IP address "%s" is not valid' % IPAddr
    sys.exit(2)

# vim: ts=2 sw=2 tw=78 expandtab
