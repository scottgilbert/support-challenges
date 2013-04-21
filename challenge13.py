#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Challenge 13: Write an application that nukes everything in your Cloud
# Account. It should:
#   Delete all Cloud Servers
#   Delete all Custom Images
#   Delete all Cloud Files Containers and Objects
#   Delete all Databases
#   Delete all Networks
#   Delete all CBS Volumes

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

# Optional Parameters:
#   -h, --help                Show help message and exit
#   prefix                    Delete cloud resources with names starting
#                             with this prefix
#   --region REGION           Region in which to delete resources (DFW or ORD)
#   --all                     Delete ALL cloud resources in account (within a 
#                             single region)
#   --dryrun                  Do not actually delete anything, just print what
#                             would be deleted.


import sys
import os
import argparse
import pyrax
import challenge1 as c1

def  clean_up_generic(cloud, prefix, type):
  """Generic Cloud Delete.  It will attempt to delete whatever cloud device
  type it is given, if the name of the device matches the specified prefix.
  """
  for obj in cloud.list():
    if obj.name.startswith(prefix):
      print "%s: Deleting %s" % (type, obj.name)
      #if not dryrun: cloud.delete(obj)
      if not dryrun: obj.delete()

def  clean_up_files(cf, prefix):
  """Delete all Cloudfiles containers (and contents) where the container
  name starts with specified prefix
  """
  for contName in cf.list_containers():
    if contName.startswith(prefix):
      cont = cf.get_container(contName)
      for obj in cont.get_objects():
        print "CloudFiles: deleting object %s/%s" % (contName, obj.name)
        if not dryrun: cont.delete_object(obj)
      if cont.object_count == 0:
        print "CloudFiles: deleting container %s" % contName
        if not dryrun: cf.delete_container(contName)
      else:
        print "CloudFiles: Container %s matches prefix," % contName,
        print "but is not empty, so cannot be deleted" 

def  clean_up_dns(dns, prefix):
  """Delete all DNS records and zones that start with specified prefix"""
  for zone in dns.list():
    if zone.name.startswith(prefix):
      print "DNS: Deleting entire zone %s" % zone.name
      if not dryrun: dns.delete(zone.id)
    else:
      for rcd in dns.list_records(zone.id):
        if rcd.name.startswith(prefix):
          print "DNS: Deleting %s %s %s" % (rcd.name, rcd.type, rcd.data)
          if not dryrun: dns.delete_record(zone.id, rcd.id)

def  clean_up_images(cs, prefix):
  """Delete all cloudserver images whose names start with specified prefix"""
  for img in cs.images.list():
    if img.name.startswith(prefix):
      try:
        if not dryrun: img.delete()
        print "Images: Deleting %s" % img.name
      except:
        print "Images: Attempt to delete %s failed"  % img.name

if __name__ == "__main__": 
  print "Challenge 13: Write an application that nukes everything in your",
  print "Cloud Account. It should:"
  print "  -Delete all Cloud Servers"
  print "  -Delete all Custom Images"
  print "  -Delete all Cloud Files Containers and Objects"
  print "  -Delete all Databases"
  print "  -Delete all Networks"
  print "  -Delete all CBS Volumes"

  parser = argparse.ArgumentParser()
  parser.add_argument("prefix", default=False
                      help="name prefix of resources to be deleted")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create devices (DFW or ORD)")
  parser.add_argument("--dryrun", action="store_true",
                      help="Do not actually perform deletes")
  parser.add_argument("--all", action="store_true",
                      help="Delete ALL cloud resources in account")

  args = parser.parse_args()
  if not c1.is_valid_region(args.region):
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)
  if not args.prefix and not args.all:
    print "You must either specify a prefix OR",
    print "to delete everything specify --all"
    sys.exit(3)
  if args.prefix and args.all:
    print "You cannot specify both a prefix and --all",
    print "If you want to delete everything, do not provide a prefix."
    sys.exit(4)

  dryrun = args.dryrun
  if args.all: args.prefix = ''

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)

  cs = pyrax.connect_to_cloudservers(region=args.region)
  dns = pyrax.connect_to_cloud_dns(region=args.region)
  clb = pyrax.connect_to_cloud_loadbalancers(region=args.region)
  cn = pyrax.connect_to_cloud_networks(region=args.region)
  cbs = pyrax.connect_to_cloud_blockstorage(region=args.region)
  cf = pyrax.connect_to_cloudfiles(region=args.region)
  cdb = pyrax.connect_to_cloud_databases(region=args.region)

  # Servers
  clean_up_generic(cs, args.prefix, 'CloudServer')
  # Files
  clean_up_files(cf, args.prefix)
  # DNS
  clean_up_dns(dns, args.prefix)
  # Loadbalancers
  clean_up_generic(clb, args.prefix, 'CloudLoadbalancer')
  # Images
  clean_up_images(cs, args.prefix)
  # Databases
  clean_up_generic(cdb, args.prefix, 'CloudDatabase')
  # Block Storage
  clean_up_generic(cbs, args.prefix, 'CloudBlockStorage')
  # Networks
  clean_up_generic(cn, args.prefix, 'CloudNetworks')

# vim: ts=2 sw=2 tw=78 expandtab