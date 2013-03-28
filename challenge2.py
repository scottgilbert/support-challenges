#!/usr/bin/env python
# Challenge2 - Write a script that clones a server (takes an image and deploys
# the image as a new server). 
# Author: Scott Gilbert

# Requires a single parameter of the uuid of the server to be cloned.

import sys, os, time, datetime
import pyrax
import challenge1 as c1


credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(credential_file)
cs = pyrax.cloudservers

def cloneIt(serverUUID):
  """Create a clone of an existing CloudServer.

  An image of the "source" CloudServer is created and then a new
  CloudServer is created from that image.
  The new CloudServer is give a hostname of the source CloudServer
  with "-clone" appended.

  Function returns as soon as network IPs are available for the new
  CloudServer. The build of the CloudServer will not yet be complete.
  """
  # get info about source server
  source_server = cs.servers.get(serverUUID)

  # Request image of source server
  imageName='%s-%s' % (source_server.name,
            datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
  image_id = cs.servers.create_image(serverUUID, imageName)

  # Wait for image to complete
  print "Waiting for image build to complete (usually takes 30-90 minutes)..."
  newImage = cs.images.get(image_id)
  while newImage.status <> 'ACTIVE':
    time.sleep(60)
    newImage.get()
    print "%s %d%%" % (newImage.status, newImage.progress)

  # Create new server using image 
  print "Image complete!\nBuilding new server"
  newserver = cs.servers.create(source_server.name + '-clone', image_id,
                                source_server.flavor['id'])
  return newserver

if __name__ == "__main__":

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  if len(sys.argv) == 2:
    newserver = cloneIt(sys.argv[1]);
    # Wait for network info to become available
    c1.waitForServerNetworks([newserver])
    # Print info for new server
    c1.printServersInfo([newserver])

  else:
    print "Wrong number of parameters specified!"
    print "Usage:  challenge2 <server uuid>"

# vim: ts=2 sw=2 tw=78 expandtab
