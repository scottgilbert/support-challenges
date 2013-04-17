#!/usr/bin/env python
# Challenge9 - Write an application that when passed the arguments FQDN,
# image, and flavor it creates a server of the specified image and flavor with
# the same name as the fqdn, and creates a DNS entry for the fqdn pointing to
# the server's public IP.
# Author: Scott Gilbert

# Required Parameters:
#   FQDN                      FQDN for the new CloudServer
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --flavor FLAVOR           Flavor of server to create
#   --image IMAGE             Image from which to create server
#   --region REGION           Region in which to create servers (DFW or ORD)

import sys
import os
import re
import argparse
import pyrax
import challenge1 as c1
import challenge4 as c4

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

def cloud_server_public_ipv4(server):
  """Given a pyrax cloudserver object, extract and return the server's primary
  public IPv4 address.
  """
  for addr in  server.networks['public']:
    if c4.is_valid_ipv4_address(addr):
      return addr
  # if we don't find one, then return False
  return False

def cloud_server_public_ipv6(server):
  """Given a pyrax cloudserver object, extract and return the server's primary
  public IPv4 address.
  """
  for addr in  server.networks['public']:
    if c4.is_valid_ipv6_address(addr):
      return addr
  # if we don't find one, then return False
  return False


if __name__ == "__main__":
  print "\nChallenge9 - Write an application that when passed the arguments"
  print "FQDN, image, and flavor it creates a server of the specified image"
  print "and flavor with the same name as the fqdn, and creates a DNS entry"
  print "for the fqdn pointing to the server's public IP.\n\n"

  parser = argparse.ArgumentParser()
  parser.add_argument("FQDN", help="FQDN for the new CloudServer")
  parser.add_argument("--image", help="Image from which to create server", 
                      default='c195ef3b-9195-4474-b6f7-16e5bd86acd0')
  parser.add_argument("--flavor", default=2, 
                      help="Flavor of server to create")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create server (DFW or ORD)")
  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if c1.is_valid_region(args.region):
    cs = pyrax.connect_to_cloudservers(region=args.region)
    dns = pyrax.connect_to_cloud_dns(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  if not is_valid_hostname(args.FQDN):
    print "This does not appear to be a valid host name: %s" % args.FQDN
    sys.exit(2)
  if not c1.is_valid_image(cs, args.image):
    print "This does not appear to be a valid image-uuid: %s" % args.image
    sys.exit(3)
  if not c1.is_valid_flavor(cs, args.flavor):
    print "This does not appear to be a valid flavor-id: %s" % args.flavor
    sys.exit(4)
  
  servers = c1.build_some_servers(cs, args.flavor, args.image, args.FQDN, 1)
  c1.wait_for_server_networks(servers)
  c1.print_servers_info(servers)
  pubIPv4 = cloud_server_public_ipv4(servers[0])
  c4.create_dns_record(dns, args.FQDN, pubIPv4, 'A')
  pubIPv6 = cloud_server_public_ipv6(servers[0])
  c4.create_dns_record(dns, args.FQDN, pubIPv6, 'AAAA')

# vim: ts=2 sw=2 tw=78 expandtab
