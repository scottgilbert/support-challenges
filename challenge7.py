#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Challenge7 - Write a script that will create 2 Cloud Servers and add them as
# nodes to a new Cloud Load Balancer. 

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
#  none
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --flavor FLAVOR           Flavor of servers to create
#   --image IMAGE             Image from which to create servers
#   --basename BASENAME       Base name to assign to new servers
#   --numservers NUMSERVERS   Number of servers to create
#   --region REGION           Region in which to create servers (DFW or ORD)
#   --lbname                  Name for created Cloud Loadbalancer 

import os
import sys
import argparse
import pyrax
import challenge1 as c1

def create_lb_and_add_servers(clb, LBName, servers):
  """Create a new CloudLoadbalancer instance and add CloudServers to
  loadbalancing pool.
  """

  #create "nodes" for each cloudServer
  node = []
  for s in servers:
    node.append(clb.Node(address=s.networks['private'][0], port=80))

  # create the VIP
  vip = clb.VirtualIP(type="PUBLIC")

  # Create the LB itself
  lb = clb.create(LBName, port=80, protocol="HTTP",
          nodes=node, virtual_ips=[vip], algorithm='ROUND_ROBIN')
  print "\nNew Loadbalancer %s:" % lb.name 
  print " VIP: %s" % lb.virtual_ips[0].address
  print " protocol: %s" % lb.protocol
  print " port: %s" % lb.port
  print " Nodes:"
  for n in lb.nodes:
    print "   addr: %s  port: %s  status: %s" % (n.address, n.port, 
                                                 n.condition)
  print "\n"

  return lb

if __name__ == "__main__":
  print "\nChallenge7 - Write a script that will create 2 Cloud Servers and"
  print "add them as nodes to a new Cloud Load Balancer.\n\n"

  parser = argparse.ArgumentParser()
  parser.add_argument("--flavor", default=2, 
                      help="Flavor of servers to create")
  parser.add_argument("--image", help="Image from which to create servers", 
                      default='c195ef3b-9195-4474-b6f7-16e5bd86acd0')
  parser.add_argument("--basename", default='Challenge7Server', 
                      help="Base name to assign to new servers")
  parser.add_argument("--numservers", default=2, type=int,
                      help="Number of servers to create")
  parser.add_argument("--lbname", default='Challenge7LB',
                      help="Name for created Cloud Loadbalancer")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create devices (DFW or ORD)")

  args = parser.parse_args()
             
  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if c1.is_valid_region(args.region, 'compute') and
      c1.is_valid_region(args.region, 'load_balancer'):
    cs = pyrax.connect_to_cloudservers(region=args.region)
    clb = pyrax.connect_to_cloud_loadbalancers(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  if not c1.is_valid_image(cs, args.image):
    print "This does not appear to be a valid image-uuid: %s" % args.image
    sys.exit(3)

  if not c1.is_valid_flavor(cs, args.flavor):
    print "This does not appear to be a valid flavor-id: %s" % args.flavor
    sys.exit(4)

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  servers = c1.build_some_servers(cs, args.flavor, args.image, args.basename,
                                args.numservers)
  c1.wait_for_server_networks(servers)
  c1.print_servers_info(servers)

  lb = create_lb_and_add_servers(clb, args.lbname, servers)

# vim: ts=2 sw=2 tw=78 expandtab
