#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Challenge9 - Write an application that when passed the arguments FQDN,
# image, and flavor it creates a server of the specified image and flavor with
# the same name as the fqdn, and creates a DNS entry for the fqdn pointing to
# the server's public IP.

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
import argparse
import pyrax
import challenge1 as c1
import challenge4 as c4

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

  if not c4.is_valid_hostname(args.FQDN):
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
