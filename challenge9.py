#!/usr/bin/env python
# Challenge9 - Write an application that when passed the arguments FQDN,
# image, and flavor it creates a server of the specified image and flavor with
# the same name as the fqdn, and creates a DNS entry for the fqdn pointing to
# the server's public IP.
# Author: Scott Gilbert

# Requires the following parameters:
#  FQDN
#  image uuid
#  flavor

import sys, os, re
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
  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  cs = pyrax.cloudservers
  dns = pyrax.cloud_dns

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  if len(sys.argv) == 4:
    fqdn = sys.argv[1]
    image = sys.argv[2]
    flavor = sys.argv[3]
    if not isValidHostname(fqdn):
      print "This does not appear to be a valid image-uuid: %s" % image
      sys.exit(2)
    if not isValidImage(image):
      print "This does not appear to be a valid image-uuid: %s" % image
      sys.exit(3)
    if not isValidFlavor(flavor):
      print "This does not appear to be a valid flavor-id: %s" % flavor
      sys.exit(4)

    
    servers = c1.BuildSomeServers(cs, flavor, image, fqdn, 1)
    c1.waitForServerNetworks(servers)
    c1.printServersInfo(servers)
    pubIPv4 = CloudServerPublicIPv4(servers[0])
    c4.createDNSRecord(dns, fqdn, pubIPv4, 'A')
    pubIPv6 = CloudServerPublicIPv6(servers[0])
    c4.createDNSRecord(dns, fqdn, pubIPv6, 'AAAA')

  else:
    print "Wrong number of parameters specified!\n"
    print "Usage:  challenge9 <FQDN> <image-uuid> <flavor-id>\n"
    sys.exit(1)

# vim: ts=2 sw=2 tw=78 expandtab
