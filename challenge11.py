#!/usr/bin/env python
# Challenge 11 - Write an application that will:
# - Create an SSL terminated load balancer (Create self-signed certificate.)
# - Create a DNS record that should be pointed to the load balancer.
# - Create Three servers as nodes behind the LB.
# - Each server should have a CBS volume attached to it. (Size and type are
#     irrelevant.)
# - All three servers should have a private Cloud Network shared between
#     them.
# - Login information to all three servers returned in a readable format as
#     the result of the script, including connection information.
# Author: Scott Gilbert

# Required Parameters:
#  FQDN                       FQDN for the DNS record
#  sslcertfile                file containing ssl certificate
#  sslkeyfile                 file containing ssl private key
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --basename BASENAME       Base name to assign to new servers
#   --image IMAGE             Image from which to create servers
#   --flavor FLAVOR           Flavor of servers to create
#   --numservers NUMSERVERS   Number of servers to create
#   --volumesize VOLUMESIZE   Size of CBS volume to attach to servers
#   --networkname NETWORKNAME Name to give to new Cloud Network
#   --networknet NETWORKNET   CIDR network address to use on new network
#   --lbname LBNAME           Name of Loadbalancer to create
#   --region REGION           Region in which to create devices (DFW or ORD)

import sys, os, time, argparse
import pyrax
import challenge1 as c1
import challenge4 as c4
import challenge7 as c7
import challenge9 as c9

if __name__ == "__main__": 
  print "\nChallenge 11 - Write an application that will:"
  print " - Create an SSL terminated load balancer (Create self-signed",
  print "certificate.)"
  print " - Create a DNS record that should be pointed to the load balancer."
  print " - Create Three servers as nodes behind the LB."
  print " - Each server should have a CBS volume attached to it. (Size and",
  print "type are irrelevant.)"
  print " - All three servers should have a private Cloud Network shared",
  print "between them."
  print " - Login information to all three servers returned in a readable",
  print "format as the result of the script, including connection",
  print "information.\n\n"

  parser = argparse.ArgumentParser()
  parser.add_argument("FQDN", help="FQDN for the DNS record")
  parser.add_argument("sslcertfile", help="File containing ssl certificate")
  parser.add_argument("sslkeyfile", help="file containing ssl private key")
  parser.add_argument("--basename", help="Base name to assign to new servers")
  parser.add_argument("--image", help="Image from which to create servers", 
                      default='c195ef3b-9195-4474-b6f7-16e5bd86acd0')
  parser.add_argument("--flavor", default=2, 
                      help="Flavor of servers to create")
  parser.add_argument("--numservers", default=3, type=int,
                      help="Number of servers to create")
  parser.add_argument("--volumesize", default=100, type=int,
                      help="Size of CBS volume to attach to servers")
  parser.add_argument("--networkname", default='Challenge11',
                      help="Name to give to new Cloud Network")
  parser.add_argument("--networknet", default='192.168.99.0/24',
                      help="CIDR network address to use on new network")
  parser.add_argument("--lbname", default=False,
                      help="Name of Loadbalancer to create")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create devices (DFW or ORD)")
  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if c1.isValidRegion(args.region):
    cs = pyrax.connect_to_cloudservers(region=args.region)
    dns = pyrax.connect_to_cloud_dns(region=args.region)
    clb = pyrax.connect_to_cloud_loadbalancers(region=args.region)
    cn = pyrax.connect_to_cloud_networks(region=args.region)
    cbs = pyrax.connect_to_cloud_blockstorage(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  sslCertFile = os.path.expanduser(args.sslcertfile)
  if not os.path.isfile(sslCertFile):
    print 'The specified SSL Cert file "%s" does not exist' % sslCertFile
    sys.exit(3)

  sslKeyFile = os.path.expanduser(args.sslkeyfile)
  if not os.path.isfile(sslKeyFile):
    print 'The specified SSL Private Key file "%s" does not exist' % sslKeyFile
    sys.exit(4)

  if args.volumesize < 100 or args.volumesize > 1024:
    print 'The specified volume size is not valid: %s' % args.volumesize
    sys.exit(5)

  if not c9.isValidHostname(args.FQDN):
    print "The specified FQDN is not valid: %s" % args.FQDN
    sys.exit(6)

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  #Create new Cloud Network
  print "Creating new CloudNetwork named %s using %s" % (args.networkname
                                                         args.networknet)
  network = cn.create(args.networkname, cidr=args.networknet)
  allnets = network.get_server_networks(public=True, private=True)

  #Create servers and attach to network
  servers = c1.BuildSomeServers(cs, args.flavor, args.image, args.FQDN,
                                args.numservers, {}, allnets)
  c1.waitForServerNetworks(servers)
  c1.printServersInfo(servers)
  #Create CBS volumes and attach to servers
  for srv in servers:
    volname = "vol_%s" % srv.name
    print "Creating Block Storage Volume %s of size %d" % (volname, 
                                                           args.volumesize)
    vol = cbs.create(name=volname, size=args.volumesize, volume_type="SATA")
    print "Attaching volume %s to server %s" % (volname, srv.name)
    vol.attach_to_instance(srv)
  #Create LB, with server nodes 
  if not args.lbname:
    LBName = 'LB' + args.FQDN
  else:
    LBName = args.lbname
  print "Creating Loadbalancer %s" % LBName
  lb = c7.CreateLBandAddServers(clb, LBName, servers)
  waitForLBBuild(lb)
  #install ssl cert/key on LB
  cert = open(sslCertFile, 'r').read()
  key = open(sslKeyFile, 'r').read()
  print "Applying SSL cert from file %s to Loadbalancer" % sslCertFile
  lb.add_ssl_termination(securePort=443, enabled=True, secureTrafficOnly=False,
                         certificate=cert, privatekey=key)
  # create DNS entries for the LB
  c4.createDNSRecord(dns, args.FQDN, lb.virtual_ips[0].address, 'A')

# vim: ts=2 sw=2 tw=78 expandtab
