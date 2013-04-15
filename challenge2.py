#!/usr/bin/env python
# Challenge2 - Write a script that clones a server (takes an image and deploys
# the image as a new server). 
# Author: Scott Gilbert

# Required Parameters:
#  UUID of server to be cloned
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --region REGION           Region in which to create server (DFW or ORD)


import sys
import os
import time
import datetime
import argparse
import pyrax
import challenge1 as c1


def clone_server(cs, serverUUID):
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
  print "Requesting image of source server. Image will be named %s" % imageName
  image_id = cs.servers.create_image(serverUUID, imageName)

  # Wait for image to complete
  print "Waiting for image build to complete (usually takes 30-90 minutes)..."
  newImage = cs.images.get(image_id)
  while newImage.status <> 'ACTIVE':
    time.sleep(60)
    newImage.get()
    print "%s %d%%" % (newImage.status, newImage.progress)

  # Create new server using image 
  newServerName = source_server.name + '-clone'
  print "Image complete!\nBuilding new server named %s" % newServerName
  newserver = cs.servers.create(newServerName, image_id,
                                source_server.flavor['id'])
  return newserver

if __name__ == "__main__":
  print "Challenge2 - Write a script that clones a server (takes an image and"
  print "deploys the image as a new server).\n\n" 

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  parser = argparse.ArgumentParser()
  parser.add_argument("SourceServer", help="UUID of the server to clone")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create servers (DFW or ORD)")
  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if c1.is_valid_region(args.region):
    cs = pyrax.connect_to_cloudservers(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  try:
    cs.servers.find(id=args.SourceServer)
  except:
    print "The source server UUID you specified was not found"
    print "in region %s : %s" % (args.region, args.SourceServer)
    print "Perhaps it is in a different region?"
    print "Aborting...."
    sys.exit(2)

  newserver = clone_server(cs, args.SourceServer);
  # Wait for network info to become available
  c1.wait_for_server_networks([newserver])
  # Print info for new server
  c1.print_servers_info([newserver])

# vim: ts=2 sw=2 tw=78 expandtab
