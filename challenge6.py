#!/usr/bin/env python
# Challenge6 - Write a script that creates a CDN-enabled container in Cloud
# Files.
# Author: Scott Gilbert

# Required Parameters:
#   container                 Name of CloudFiles container to create
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --region REGION           Region in which to create container (DFW or ORD)


import sys
import os
import argparse
import pyrax
import challenge1 as c1

def createCDNContainer(cf, newContainerName):
  """Create a new CloudFiles Container and enable public CDN access
  If the specified container already exists, abort with error message.
  """

  try:
    existingContainer = cf.get_container(newContainerName)
    # if we were able to get container info, then it already exists
    print 'The container %s already exists! ' % newContainerName
    if existingContainer.cdn_enabled:
      print 'The container is already CDN enabled,',
      print 'so no further action has been taken'
    else:
      print 'The container is not currently CDN enabled.'
      print 'We do not want to accidentally publish a private container,',
      print 'so no action has been taken.'
    return

  except :
    # proceed with creating container
    print 'Creating container %s...' % newContainerName
    newContainer = cf.create_container(newContainerName)
    newContainer.make_public()
    print "Done!"

if __name__ == "__main__":
  print "\nChallenge6 - Write a script that creates a CDN-enabled container in"
  print "Cloud Files.\n\n"

  parser = argparse.ArgumentParser()
  parser.add_argument("container", 
                      help="Name of CloudFiles container to create")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create container (DFW or ORD)")

  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if c1.isValidRegion(args.region):
    cf = pyrax.connect_to_cloudfiles(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  createCDNContainer(cf, args.container)

# vim: ts=2 sw=2 tw=78 expandtab
