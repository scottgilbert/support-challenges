#!/usr/bin/env python
# Challenge1 - Write a script that builds three 512 MB Cloud Servers that
# following a similar naming convention. (ie., web1, web2, web3) and returns
# the IP and login credentials for each server. Use any image you want.
# Author: Scott Gilbert

import os, sys, time
import pyrax

# unbuffer stdout for pretty output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

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

def BuildSomeServers(flavor, image, serverBaseName, numServers):
  """ Request build of CloudServers of specified flavor and image.
  Server hostnames are the combination of serverBaseName and a sequential
  counter, starting with 1 and ending with numServers

  Wait until at least network IPs are assigned before returning.  While 
  waiting for network assignment, a simple "progress" output is 
  generated, just to let the user know that *something* is happening.

  Finally, print basic information (IPs, passwords, etc) for each new 
  server is displayed.

  Note: Function returns when network info is available, but server build
  is probably not finished!
  """
    
  # Request build of new servers
  server=[]
  for server_num in xrange(1, numServers + 1):
    print "Requesting build for server %s%d" % (serverBaseName, server_num)
    server.append(cs.servers.create("%s%d" % (serverBaseName, server_num), 
                                    image, flavor))
  
  # Wait for all servers to get IP addrs assigned
  print "\nWaiting for IP addresses to be assigned..."
  networks_assigned = False
  while not networks_assigned:
    time.sleep(2)
    print '.', 
    networks_assigned = True
    for srv in server:
      srv.get()
      if srv.networks == {} and srv.status <> 'ERROR':  
        networks_assigned = False
        break
  
  # Print all the happy goodness!
  print "Done!\n"
  for srv in server:
    print "\n\nServer Name: %s" % srv.name
    print "Status: %s" % srv.status
    print "Root Password: %s" % srv.adminPass
    print "Public IPs:", 
    for ip in srv.networks['public']: print '%s  ' % ip,
    print "\nPrivate IP:", 
    for ip in srv.networks['private']: print '%s  ' % ip,
  
  print "\n"
  return server

if __name__ == "__main__":

  BuildSomeServers(flavor, image, serverBaseName, numServers)

# vim: ts=2 sw=2 tw=78 expandtab
