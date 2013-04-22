#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Challenge1 - Write a script that builds three 512 MB Cloud Servers that
# following a similar naming convention. (ie., web1, web2, web3) and returns
# the IP and login credentials for each server. Use any image you want.

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


import os
import sys
import time
import argparse
import pyrax

def valid_regions():
  """Return list of valid regions"""
  # I have not yet been able to find a good way to get this list via the API
  # so it is hardcoded for now.
  return ['DFW','ORD']

def is_valid_region(region):
  """ Check validity of a region """
  if region in valid_regions():
    return True
  else:
    return False

def is_valid_image(cs, image):
  """Check the validity of a CloudServer image uuid.
  Return True if image is valid, False otherwise.
  """
  try:
    cs.images.get(image)
    return True
  except:
    return False

def is_valid_flavor(cs, flavor):
  """Check the validity of a CloudServer flavor-id.
  Return True if flavor-id is valid, False otherwise.
  """
  try:
    cs.flavors.get(flavor)
    return True
  except:
    return False

def build_some_servers(cs, flavor, image, serverBaseName, numServers,
                     insertFiles={}, nets={}):
  """ Request build of CloudServers of specified flavor and image.
  Server hostnames are the combination of serverBaseName and a sequential
  counter, starting with 1 and ending with numServers - unless number of 
  servers is 1, then just the serverBaseName is used.

  Returns array of server objects.

  Note: Function returns immediately, network info and server build are almost
  certainly not complete yet.
  """
    
  # Request build of new servers
  servers=[]
  if numServers == 1:
    print "Requesting build for server %s" % serverBaseName
    servers.append(cs.servers.create(serverBaseName, image, flavor,
                    files=insertFiles, nics=nets))
  else:
    for server_num in xrange(1, numServers + 1):
      print "Requesting build for server %s%d" % (serverBaseName, server_num)
      servers.append(cs.servers.create("%s%d" % (serverBaseName, server_num), 
                                      image, flavor, files=insertFiles,
                                      nics=nets))
  return servers

def wait_for_server_networks(servers):  
  """Given an array of pyrax server objects, wait until all of the servers
  have network IPs assigned.  Print a little activity indicator to let the
  user know that we are not stuck.
  """
  print "\nWaiting for IP addresses to be assigned..."
  networks_assigned = False
  while not networks_assigned:
    time.sleep(2)
    print '.', 
    networks_assigned = True
    for srv in servers:
      srv.get()
      if srv.networks == {} and srv.status <> 'ERROR':  
        networks_assigned = False
        break

def wait_for_server_builds(servers):
  """Given an array of pyrax server objects, wait until all of the servers
  builds have completed.  Print a little activity indicator to let the user
  know that we are not stuck.
  """
  print "\nWaiting for all server builds to complete..."
  allBuildsComplete = False
  while not allBuildsComplete:
    time.sleep(2)
    print '.',
    allBuildsComplete = True
    for srv in servers:
      srv.get()
      if srv.status not in ['ACTIVE','ERROR']:
        allBuildsComplete = False
        break
  
def print_servers_info(servers):
  """Given an array of pyrax server objects, print basic information about
  each one.
  """
  print "Done!\n"
  for srv in servers:
    print "\n\nServer Name: %s" % srv.name
    print "Status: %s" % srv.status
    #print "Region: %s" % srv.region
    print "Root Password: %s" % srv.adminPass
    print "Networks:"
    for net in srv.networks:
      print "   %s IPs:" % net,
      for ip in srv.networks[net]:
        print ip,
      print 
    print 

if __name__ == "__main__":
  print "\nChallenge1 - Write a script that builds three 512 MB Cloud Servers"
  print "that following a similar naming convention. (ie., web1, web2, web3)"
  print "and returns the IP and login credentials for each server. Use any"
  print "image you want.\n\n"
  
  parser = argparse.ArgumentParser()
  parser.add_argument("--flavor", default=2, 
                      help="Flavor of servers to create")
  parser.add_argument("--image", help="Image from which to create servers", 
                      default='c195ef3b-9195-4474-b6f7-16e5bd86acd0')
  parser.add_argument("--basename", default='web', 
                      help="Base name to assign to new servers")
  parser.add_argument("--numservers", default=3, type=int,
                      help="Number of servers to create")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create servers (DFW or ORD)")
  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)

  if is_valid_region(args.region):
    cs = pyrax.connect_to_cloudservers(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)
 
  if not is_valid_image(cs, args.image):
    print "This does not appear to be a valid image-uuid: %s" % args.image
    sys.exit(3)

  if not is_valid_flavor(cs, args.flavor):
    print "This does not appear to be a valid flavor-id: %s" % args.flavor
    sys.exit(4)

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  servers = build_some_servers(cs, args.flavor, args.image, args.basename,
                            args.numservers)
  wait_for_server_networks(servers)
  print_servers_info(servers)

# vim: ts=2 sw=2 tw=78 expandtab
