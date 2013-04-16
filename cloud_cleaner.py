#!/usr/bin/env python
# cloud_cleaner 
#  "Clean up" (delete) all cloud resources matching a prefix

# Author: Scott Gilbert
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --prefix PREFIX           name prefix of resources to be deleted
#                              (default='test') 
#   --region REGION           Region in which to delete (DFW or ORD)

import sys
import os
import argparse
import pyrax

def  clean_up_files(cf, prefix):
  """Delete all Cloudfiles containers (and contents) where the container
  name starts with specified prefix
  """
  for contName in cf.list_containers():
    if contName.startswith(prefix):
      cont = cf.get_container(contName)
      for obj in cont.get_objects():
        print "CloudFiles: deleting object %s/%s" % (contName, obj)
        cont.delete_object(obj)
      if cont.object_count == 0:
        print "CloudFiles: deleting container %s" % contName
        cf.delete_container(contName)
      else:
        print "CloudFiles: Container %s matches prefix," % contName,
        print "but is not empty, so cannot be deleted" 

def  clean_up_generic(cloud, prefix, type):
  """Generic Cloud Delete.  It will attempt to delete whatever cloud device
  type it is given, if the name of the device matches the specified prefix.
  """
  for obj in cloud.list():
    if obj.name.startswith(prefix):
      print "%s: Deleting %s" % (type, obj.name)
      cloud.delete(obj)

def  clean_up_dns(dns, prefix):
  """Delete all DNS records and zones that start with specified prefix"""
  for zone in dns.list():
    if zone.name.startswith(prefix):
      print "DNS: Deleting entire zone %s" % zone.name
      dns.delete(zone.id)
    else:
      for rcd in dns.list_records(zone.id):
        if rcd.name.startswith(prefix):
          print "DNS: Deleting %s %s %s" % (rcd.name, rcd.type, rcd.data)
          dns.delete_record(zone.id, rcd.id)

def  clean_up_networks(cn, prefix):
  pass

def  clean_up_loadbalancers(clb, prefix):
  pass

def  clean_up_blockstorage(cbs, prefix):
  pass

def  clean_up_servers(dns, prefix):
  pass

def  clean_up_images(cs, prefix):
  for img in cs.images.list():
    if img.name.startswith(prefix):
      try:
        img.delete()
        print "Images: Deleting %s" % img.name
      except:
        print "Images: Attempt to delete %s failed"  % img.name

def  clean_up_databases(cdb, prefix):
  pass


if __name__ == "__main__": 
  parser = argparse.ArgumentParser()
  parser.add_argument("--prefix", default='test',
                      help="name prefix of resources to be deleted")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create devices (DFW or ORD)")

  args = parser.parse_args()

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
