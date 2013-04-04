#!/usr/bin/env python
# Challenge7 - Write a script that will create 2 Cloud Servers and add them as
# nodes to a new Cloud Load Balancer. 
# Author: Scott Gilbert

import os, sys, time
import pyrax
import challenge1 as c1

def CreateLBandAddServers(clb, LBName, servers):
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
  print "\nNew Loadbalancer %s:\n" % lb.name 
  print " VIP: %s" % lb.virtual_ips[0].address
  print " protocol: %s" % lb.protocol
  print " port: %s" % lb.port
  print " Nodes:"
  for n in lb.nodes:
    print "   addr: %s  port: %s  status: %s" % (n.address, n.port, n.condition)
  print "\n"

  return lb

if __name__ == "__main__":
  print "Challenge7 - Write a script that will create 2 Cloud Servers and"
  print "add them as nodes to a new Cloud Load Balancer.\n\n"
 
  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  
  # flavor = 512MB
  flavor = 2 
  # image = CentOS 6.3 
  image = 'c195ef3b-9195-4474-b6f7-16e5bd86acd0'
  # Base name to user for new servers
  serverBaseName = 'web'
  # Number of servers to build
  numServers = 2
  # Name of the new LB instance
  LBName = 'LB-Challenge7'
  
  pyrax.set_credential_file(credential_file)
  cs = pyrax.cloudservers
  clb = pyrax.cloud_loadbalancers

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  servers = c1.BuildSomeServers(cs, flavor, image, serverBaseName, numServers)
  c1.waitForServerNetworks(servers)
  c1.printServersInfo(servers)

  lb = CreateLBandAddServers(clb, LBName, servers)

# vim: ts=2 sw=2 tw=78 expandtab
