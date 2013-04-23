#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Challenge10 - Write an application that will:
#  - Create 2 servers, supplying a ssh key to be installed at 
#    /root/.ssh/authorized_keys.
#  - Create a load balancer
#  - Add the 2 new servers to the LB
#  - Set up LB monitor and custom error page. 
#  - Create a DNS record based on a FQDN for the LB VIP. 
#  - Write the error page html to a file in cloud files for backup.

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
#  FQDN                       FQDN for the new website
#  sshkeyfile                 file containing public ssh-key
#  errorpage                  file containing error page content (html)
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --image IMAGE             Image from which to create servers
#   --flavor FLAVOR           Flavor of servers to create
#   --numservers NUMSERVERS   Number of servers to create
#   --lbname LBNAME           Name of Loadbalancer to create
#   --container CONTAINER     Cloudfiles container to copy error page file to
#   --region REGION           Region in which to create devices (DFW or ORD)


import sys
import os
import time
import argparse
import pyrax
import challenge1 as c1
import challenge4 as c4
import challenge7 as c7
import challenge9 as c9

def cloud_lb_public_ipv4(lb):
  """Given a pyrax CloudLoadbalancer object, return the IPv4 VIP address
  """
  for addr in  lb.virtual_ips:
    if c4.is_valid_ipv4_address(addr):
      return addr
  # if we don't find one, then return False
  return False

def cloud_lb_public_ipv6(lb):
  """Given a pyrax CloudLoadbalancer object, return the IPv6 VIP address
  """
  for addr in  lb.virtual_ips:
    if c4.is_valid_ipv6_address(addr):
      return addr
  # if we don't find one, then return False
  return False

def wait_for_lb_build(lb):  
  """Given a pyrax loadbalancer object, wait until the loadbalancer build
     is complete.  Print a little activity indicator to let the
      user know that we are not stuck.
  """
  print "\nWaiting for loadbalancer to become active..."
  lb.get()
  while lb.status != 'ACTIVE':
    time.sleep(2)
    print '.', 
    lb.get()
  print "Done!"


if __name__ == "__main__":
  print "\nChallenge10 - Write an application that will:"
  print " - Create 2 servers, supplying a ssh key to be installed at",
  print "/root/.ssh/authorized_keys."
  print " - Create a load balancer"
  print " - Add the 2 new servers to the LB"
  print " - Set up LB monitor and custom error page."
  print " - Create a DNS record based on a FQDN for the LB VIP." 
  print " - Write the error page html to a file in cloud files for backup.\n\n"

  parser = argparse.ArgumentParser()
  parser.add_argument("FQDN", help="FQDN for the new website")
  parser.add_argument("sshkeyfile", help="File containing public ssh-key")
  parser.add_argument("errorpage", help="File containing error page html")
  parser.add_argument("--image", help="Image from which to create servers", 
                      default='c195ef3b-9195-4474-b6f7-16e5bd86acd0')
  parser.add_argument("--flavor", default=2, 
                      help="Flavor of servers to create")
  parser.add_argument("--numservers", default=2, type=int,
                      help="Number of servers to create")
  parser.add_argument("--lbname", default=False,
                      help="Name of Loadbalancer to create")
  parser.add_argument("--container", default=False,
                      help="Cloudfiles container to copy error page file to")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create devices (DFW or ORD)")
  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if (c1.is_valid_region(args.region, 'compute') and
      c1.is_valid_region(args.region, 'object_store') and
      c1.is_valid_region(args.region, 'load_balancer')):
    cs = pyrax.connect_to_cloudservers(region=args.region)
    dns = pyrax.connect_to_cloud_dns(region=args.region)
    clb = pyrax.connect_to_cloud_loadbalancers(region=args.region)
    cf = pyrax.connect_to_cloudfiles(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  sshkeyFile = os.path.expanduser(args.sshkeyfile)
  errorPageFile = os.path.expanduser(args.errorpage)
  if not c4.is_valid_hostname(args.FQDN):
    print "The specified FQDN is not valid: %s" % args.FQDN
    sys.exit(7)
  if not os.path.isfile(sshkeyFile):
    print "The ssh key file does not exist: %s" % sshKeyFile
    sys.exit(3)
  if not os.path.isfile(errorPageFile):
    print "The Error Page file does not exist: %s" % errorPageFile
    sys.exit(4)
  if not c1.is_valid_image(cs, args.image):
    print "This does not appear to be a valid image-uuid: %s" % args.image
    sys.exit(5)
  if not c1.is_valid_flavor(cs, args.flavor):
    print "This does not appear to be a valid flavor-id: %s" % args.flavor
    sys.exit(6)

  # Create Servers
  sshkey = open(sshkeyFile, 'r').read()
  authkeyFile = '/root/.ssh/authorized_keys'
  serverFiles = {authkeyFile: sshkey}
  servers = c1.build_some_servers(cs, args.flavor, args.image, args.FQDN,
                                  args.numservers, serverFiles)
  c1.wait_for_server_networks(servers)
  c1.print_servers_info(servers)

  # Create Loadbalancer
  if not args.lbname:
    LBName = '%s-LB' % args.FQDN
  else:
    LBName = args.lbname
  print "Creating Loadbalancer %s" % LBName
  lb = c7.create_lb_and_add_servers(clb, LBName, servers)
  wait_for_lb_build(lb)

  # create DNS entries for the LB
  c4.create_dns_record(dns, args.FQDN, lb.virtual_ips[0].address, 'A')

  print "Adding Loadbalancer monitor"
  lb.add_health_monitor(type="CONNECT", delay=5, timeout=2,
          attemptsBeforeDeactivation=1)
  wait_for_lb_build(lb)

  # add LB error page
  errorPage = open(errorPageFile, 'r').read()
  lb.set_error_page(errorPage)

  # Upload error page to cloudfiles (container?)
  if not args.container:
    args.container = pyrax.utils.random_name(12, ascii_only=True)
  cont = cf.create_container(args.container)
  cf.store_object(cont, os.path.basename(errorPageFile), errorPage)
  print "Loadbalancer error page stored in CloudFiles container %s" % cont.name

# vim: ts=2 sw=2 tw=78 expandtab
