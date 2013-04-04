#!/usr/bin/env python
# Challenge1 - Write a script that builds three 512 MB Cloud Servers that
# following a similar naming convention. (ie., web1, web2, web3) and returns
# the IP and login credentials for each server. Use any image you want.
# Author: Scott Gilbert

import os, sys, time
import pyrax

def BuildSomeServers(cs, flavor, image, serverBaseName, numServers, insertFiles={}):
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
                    files=insertFiles))
  else:
    for server_num in xrange(1, numServers + 1):
      print "Requesting build for server %s%d" % (serverBaseName, server_num)
      servers.append(cs.servers.create("%s%d" % (serverBaseName, server_num), 
                                      image, flavor, files=insertFiles))
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
    print "Root Password: %s" % srv.adminPass
    print "Public IPs:", 
    for ip in srv.networks['public']: print '%s  ' % ip,
    print "\nPrivate IP:", 
    for ip in srv.networks['private']: print '%s  ' % ip,
  
  print "\n"

if __name__ == "__main__":
  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  
  # flavor = 512MB
  flavor = 2 
  # image = CentOS 6.3
  image = 'c195ef3b-9195-4474-b6f7-16e5bd86acd0'
  # Base name to user for new servers
  serverBaseName = 'web'
  # Number of servers to build
  numServers = 3
  
  pyrax.set_credential_file(credential_file)
  cs = pyrax.cloudservers


  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  servers = BuildSomeServers(cs, flavor, image, serverBaseName, numServers)
  waitForServerNetworks(servers)
  printServersInfo(servers)

# vim: ts=2 sw=2 tw=78 expandtab
