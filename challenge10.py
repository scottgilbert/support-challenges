#!/usr/bin/env python
# Challenge10 - Write an application that will:
#  - Create 2 servers, supplying a ssh key to be installed at 
#    /root/.ssh/authorized_keys.
#  - Create a load balancer
#  - Add the 2 new servers to the LB
#  - Set up LB monitor and custom error page. 
#  - Create a DNS record based on a FQDN for the LB VIP. 
#  - Write the error page html to a file in cloud files for backup.
# Author: Scott Gilbert

# Requires the following parameters:
#  FQDN
#  file containing public ssh key
#  file containing error page content (html)

import sys, os, time
import pyrax
import challenge1 as c1
import challenge4 as c4
import challenge7 as c7
import challenge9 as c9

credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(credential_file)
cs = pyrax.cloudservers
dns = pyrax.cloud_dns
clb = pyrax.cloud_loadbalancers
cf = pyrax.cloudfiles

def CloudLBPublicIPv4(lb):
  for addr in  lb.virtual_ips:
    if c4.is_valid_ipv4_address(addr):
      return addr
  # if we don't find one, then return False
  return False

def CloudLBPublicIPv6(lb):
  for addr in  lb.virtual_ips:
    if c4.is_valid_ipv6_address(addr):
      return addr
  # if we don't find one, then return False
  return False

def waitForLBBuild(lb):  
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


if __name__ == "__main__":

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  # flavor = 512MB
  flavor = 2 
  # image = CentOS 6.3
  image = 'c195ef3b-9195-4474-b6f7-16e5bd86acd0'
  # Number of servers to build
  numServers = 2


  if len(sys.argv) == 4:
    fqdn = sys.argv[1]
    sshkeyFile = os.path.expanduser(sys.argv[2])
    errorPageFile = os.path.expanduser(sys.argv[3])
    if not c9.isValidHostname(fqdn):
      print "The specified FQDN is not valid: %s" % fqdn
      sys.exit(2)
    if not os.path.isfile(sshkeyFile):
      print "The ssh key file does not exist: %s" % sshKeyFile
      sys.exit(3)
    if not os.path.isfile(errorPageFile):
      print "The Error Page file does not exist: %s" % errorPageFile
      sys.exit(4)

    # Create Servers
    sshkey = open(sshkeyFile, 'r').read()
    authkeyFile = '/root/.ssh/authorized_keys'
    serverFiles = {authkeyFile: sshkey}
    servers = c1.BuildSomeServers(flavor, image, fqdn, numServers, serverFiles)
    c1.waitForServerNetworks(servers)
    c1.printServersInfo(servers)
    # Create Loadbalancer
    LBName = 'LB' + fqdn
    print "Creating Loadbalancer %s" % LBName
    lb = c7.CreateLBandAddServers(LBName, servers)
    waitForLBBuild(lb)
    # create DNS entries for the LB
    c4.createDNSRecord(fqdn, lb.virtual_ips[0].address, 'A')
    # add LB monitor
    lb.add_health_monitor(type="CONNECT", delay=5, timeout=2,
            attemptsBeforeDeactivation=1)
    waitForLBBuild(lb)
    # add LB error page
    errorPage = open(errorPageFile, 'r').read()
    lb.set_error_page(errorPage)
    # Upload error page to cloudfiles (container?)
    contName = pyrax.utils.random_name(12, ascii_only=True)
    cont = cf.create_container(contName)
    print "New Container:", cont.name
    cf.store_object(cont, os.path.basename(errorPageFile), errorPage)
    print "Error page stored in CloudFiles container %s" % contName

  else:
    print "Wrong number of parameters specified!\n"
    print "Usage:  challenge10 <FQDN> <file containing public ssh key>",
    print "<file containing error page content>\n"
    sys.exit(1)

# vim: ts=2 sw=2 tw=78 expandtab
