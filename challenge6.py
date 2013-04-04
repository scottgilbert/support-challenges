#!/usr/bin/env python
# Challenge6 - Write a script that creates a CDN-enabled container in Cloud
# Files.
# Author: Scott Gilbert

# Requires one parameter:
#  Cloudfiles container name to be created
#

import sys, os, time
import pyrax

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
  print "Challenge6 - Write a script that creates a CDN-enabled container in"
  print "Cloud Files.\n\n"

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  cf = pyrax.cloudfiles

  if len(sys.argv) == 2:
    newContainerName = sys.argv[1]
    createCDNContainer(cf, newContainerName)
  else:
    print "Wrong number of parameters specified!"
    print "Usage:  challenge6 <New Container Name> "

# vim: ts=2 sw=2 tw=78 expandtab
