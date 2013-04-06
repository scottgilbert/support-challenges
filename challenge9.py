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

import sys, os, re, argparse
import pyrax
import challenge1 as c1
import challenge4 as c4


def isValidImage(cs, image):
  """Check the validity of a CloudServer image uuid.
  Return True if image is valid, False otherwise.
  """
  try:
    cs.images.get(image)
    return True
  except:
    return False

def isValidFlavor(cs, flavor):
  """Check the validity of a CloudServer flavor-id.
  Return True if flavor-id is valid, False otherwise.
  """
  try:
    cs.flavors.get(flavor)
    return True
  except:
    return False

def isValidHostname(hostname):
  """Check for basic validity of a FQDN
  Return True if the FQDN is valid, False otherwise.
  """
  if len(hostname) > 255:
    return False
  if hostname[-1:] == ".":
    hostname = hostname[:-1] # strip exactly one dot from the right, if present
  allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
  return all(allowed.match(x) for x in hostname.split("."))

def CloudServerPublicIPv4(server):
  """Given a pyrax cloudserver object, extract and return the server's primary
  public IPv4 address.
  """
  for addr in  server.networks['public']:
    if c4.is_valid_ipv4_address(addr):
      return addr
  # if we don't find one, then return False
  return False

def CloudServerPublicIPv6(server):
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
  if c1.isValidRegion(args.region):
    cs = pyrax.connect_to_cloudservers(region=args.region)
    dns = pyrax.connect_to_cloud_dns(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  if not isValidHostname(args.FQDN):
    print "This does not appear to be a valid host name: %s" % args.FQDN
    sys.exit(2)
  if not isValidImage(cs, args.image):
    print "This does not appear to be a valid image-uuid: %s" % args.image
    sys.exit(3)
  if not isValidFlavor(cs, args.flavor):
    print "This does not appear to be a valid flavor-id: %s" % args.flavor
    sys.exit(4)
  
  servers = c1.BuildSomeServers(cs, args.flavor, args.image, args.FQDN, 1)
  c1.waitForServerNetworks(servers)
  c1.printServersInfo(servers)
  pubIPv4 = CloudServerPublicIPv4(servers[0])
  c4.createDNSRecord(dns, args.FQDN, pubIPv4, 'A')
  pubIPv6 = CloudServerPublicIPv6(servers[0])
  c4.createDNSRecord(dns, args.FQDN, pubIPv6, 'AAAA')

# vim: ts=2 sw=2 tw=78 expandtab
