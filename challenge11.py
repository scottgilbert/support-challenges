#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
#  FQDN                       FQDN for the DNS record
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
#   --sslcertfile             file containing ssl certificate
#   --sslkeyfile              file containing ssl private key
#   --lbname LBNAME           Name of Loadbalancer to create
#   --region REGION           Region in which to create devices (DFW or ORD)


import sys
import os
import argparse
import pyrax
import challenge1 as c1
import challenge4 as c4
import challenge7 as c7
import challenge9 as c9
import challenge10 as c10

try:
  from OpenSSL import crypto, SSL
  from time import gmtime, mktime
  canGenerateSSL = True
except:
  canGenerateSSL = False

def create_self_signed_cert(cn):
  """ create a new self-signed cert and key.
  Returns tuple (cert, private_key)
  """
   
  # create a key pair
  pkey = crypto.PKey()
  pkey.generate_key(crypto.TYPE_RSA, 2048)
    
  # create a self-signed cert
  cert = crypto.X509()
  cert.set_pubkey(pkey)
  cert.get_subject().CN = cn
  cert.get_subject().C = "US"
  cert.get_subject().ST = "Texas"
  cert.get_subject().L = "San Antonio"
  cert.get_subject().O = "Awesome Unlimited!"
  cert.get_subject().OU = "Extra Awesome"
  cert.set_serial_number(1)
  cert.gmtime_adj_notBefore(0)
  cert.gmtime_adj_notAfter(10*365*24*60*60)
  cert.set_issuer(cert.get_subject())
  cert.sign(pkey, 'sha1')
     
  ssCert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
  ssKey = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey)
  return (ssCert, ssKey)

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
  parser.add_argument("--basename", help="Base name to assign to new servers")
  parser.add_argument("--image", help="Image from which to create servers", 
                      default='c195ef3b-9195-4474-b6f7-16e5bd86acd0')
  parser.add_argument("--flavor", default=2, 
                      help="Flavor of servers to create")
  parser.add_argument("--numservers", default=3, type=int,
                      help="Number of servers to create")
  parser.add_argument("--volumesize", default=100, type=int,
                      help="Size of CBS volume to attach to servers")
  parser.add_argument("--networkname", default=False,
                      help="Name to give to new Cloud Network")
  parser.add_argument("--networknet", default='192.168.99.0/24',
                      help="CIDR network address to use on new network")
  parser.add_argument("--sslcertfile", default=False,
                      help="File containing ssl certificate")
  parser.add_argument("--sslkeyfile", default=False,
                      help="file containing ssl private key")
  parser.add_argument("--lbname", default=False,
                      help="Name of Loadbalancer to create")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create devices (DFW or ORD)")
  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if c1.is_valid_region(args.region):
    cs = pyrax.connect_to_cloudservers(region=args.region)
    dns = pyrax.connect_to_cloud_dns(region=args.region)
    clb = pyrax.connect_to_cloud_loadbalancers(region=args.region)
    cn = pyrax.connect_to_cloud_networks(region=args.region)
    cbs = pyrax.connect_to_cloud_blockstorage(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  if not args.sslcertfile or not args.sslkeyfile:
    print "You didn't supply an SSL certificate and key.",
    print "No worries! We'll create one for you...\n"
    (cert, key) = create_self_signed_cert(args.FQDN) 
  else:
    sslCertFile = os.path.expanduser(args.sslcertfile)
    if not os.path.isfile(sslCertFile):
      print 'The specified SSL Cert file "%s" does not exist' % sslCertFile
      sys.exit(3)
  
    sslKeyFile = os.path.expanduser(args.sslkeyfile)
    if not os.path.isfile(sslKeyFile):
      print 'The specified SSL Private Key file "%s" does not exist' % sslKeyFile
      sys.exit(4)

    cert = open(sslCertFile, 'r').read()
    key = open(sslKeyFile, 'r').read()

  if args.volumesize < 100 or args.volumesize > 1024:
    print 'The specified volume size is not valid: %s' % args.volumesize
    sys.exit(5)

  if not c4.is_valid_hostname(args.FQDN):
    print "The specified FQDN is not valid: %s" % args.FQDN
    sys.exit(6)

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  #Create new Cloud Network
  if not args.networkname: 
    args.networkname = '%s-net' % args.FQDN
  print "Creating new CloudNetwork named %s using %s" % (args.networkname,
                                                         args.networknet)
  network = cn.create(args.networkname, cidr=args.networknet)
  allnets = network.get_server_networks(public=True, private=True)

  #Create servers and attach to network
  servers = c1.build_some_servers(cs, args.flavor, args.image, args.FQDN,
                                  args.numservers, {}, allnets)
  c1.wait_for_server_builds(servers)
  c1.print_servers_info(servers)

  #Create CBS volumes and attach to servers
  for srv in servers:
    volname = "%s_vol" % srv.name
    print "Creating Block Storage Volume %s of size %d" % (volname, 
                                                           args.volumesize)
    vol = cbs.create(name=volname, size=args.volumesize, volume_type="SATA")
    print "Attaching volume %s to server %s" % (volname, srv.name)
    vol.attach_to_instance(srv, mountpoint='/dev/xvdd')

  #Create LB, with server nodes 
  if not args.lbname:
    LBName = '%s-LB' % args.FQDN
  else:
    LBName = args.lbname
  print "Creating Loadbalancer %s" % LBName
  lb = c7.create_lb_and_add_servers(clb, LBName, servers)
  c10.wait_for_lb_build(lb)

  #install ssl cert/key on LB
  print "Applying SSL certificate to Loadbalancer\n" 
  lb.add_ssl_termination(securePort=443, enabled=True, secureTrafficOnly=False,
                         certificate=cert, privatekey=key)

  # create DNS entries for the LB
  c4.create_dns_record(dns, args.FQDN, lb.virtual_ips[0].address, 'A')
  print "\nDone!\n"

# vim: ts=2 sw=2 tw=78 expandtab
