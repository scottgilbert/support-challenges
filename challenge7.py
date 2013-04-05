#!/usr/bin/env python
# Challenge7 - Write a script that will create 2 Cloud Servers and add them as
# nodes to a new Cloud Load Balancer. 
# Author: Scott Gilbert

import os, sys, time, argparse
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
  parser.add_argument("--image", help="Image from which to creat servers", 
                            default='c195ef3b-9195-4474-b6f7-16e5bd86acd0')
  parser.add_argument("--basename", default='web', 
                              help="Base name to assign to new servers")
  parser.add_argument("--numservers", default=2, type=int,
                               help="Number of servers to create")
  parser.add_argument("--lbname", default='LB-Challenge7',
                               help="Name for created Cloud Loadbalancer")
  args = parser.parse_args()
             
  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  cs = pyrax.cloudservers
  clb = pyrax.cloud_loadbalancers

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  servers = c1.BuildSomeServers(cs, args.flavor, args.image, args.basename,
                                args.numservers)
  c1.waitForServerNetworks(servers)
  c1.printServersInfo(servers)

  lb = CreateLBandAddServers(clb, args.lbname, servers)

# vim: ts=2 sw=2 tw=78 expandtab
