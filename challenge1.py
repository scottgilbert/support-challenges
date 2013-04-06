#!/usr/bin/env python
# Challenge1 - Write a script that builds three 512 MB Cloud Servers that
# following a similar naming convention. (ie., web1, web2, web3) and returns
# the IP and login credentials for each server. Use any image you want.
# Author: Scott Gilbert

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


import os, sys, time, argparse
import pyrax

def isValidRegion(region):
  """ Check validity of a region """
  if region in ['DFW','ORD']:
    return True
  else:
    return False

def BuildSomeServers(cs, flavor, image, serverBaseName, numServers,
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
                    files=insertFiles, networks=nets))
  else:
    for server_num in xrange(1, numServers + 1):
      print "Requesting build for server %s%d" % (serverBaseName, server_num)
      servers.append(cs.servers.create("%s%d" % (serverBaseName, server_num), 
                                      image, flavor, files=insertFiles,
                                      networks=nets))
  return servers

def waitForServerNetworks(servers):  
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
  
def printServersInfo(servers):
  """Given an array of pyrax server objects, print basic information about
  each one.
  """
  print "Done!\n"
  for srv in servers:
    print "\n\nServer Name: %s" % srv.name
    print "Status: %s" % srv.status
    #print "Region: %s" % srv.region
    print "Root Password: %s" % srv.adminPass
    for net in srv.networks:
      print "%s IPs:" % net,
      for ip in srv.networks[net]:
        print ip,
      print "\n"

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
  if isValidRegion(args.region):
    cs = pyrax.connect_to_cloudservers(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  servers = BuildSomeServers(cs, args.flavor, args.image, args.basename,
                            args.numservers)
  waitForServerNetworks(servers)
  printServersInfo(servers)

# vim: ts=2 sw=2 tw=78 expandtab
