#!/usr/bin/env python
# Challenge3 - Write a script that accepts a directory as an argument as well
# as a container name. The script should upload the contents of the specified
# directory to the container (or create it if it doesn't exist). The script
# should handle errors appropriately. (Check for invalid paths, etc.)  
# Author: Scott Gilbert

# Required Parameters:
#  SourceDir  source directory containing files to be uploaded
#  Container  destination cloudfiles container
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --region REGION           Region in which to create container (DFW or ORD)

# Requires the following two parameters:

import sys
import os
import time
import argparse
import pyrax
import challenge1 as c1


def upload_dir_to_container(cf, ULdirectory, ULContainer):
  """ Upload contents of a local directory to a CloudFiles Container

  If the specified CloudFiles container does not already exist, then it
  is created.

  A simple progress message is displayed every 2 seconds and function
  does not return until upload completes.
  """

  # if container does not already exist, then create it!
  try:
    cont = cf.get_container(ULContainer)
    print "The container %s already exists. We'll use it!" % ULContainer
  except:
    print "The container %s did not yet exit - creating it now!" % ULContainer
    cont = cf.create_container(ULContainer)

  print "\nUploading the contents of %s to CloudFiles container %s:" % \
    (ULdirectory, ULContainer)
  upload_key, total_bytes = cf.upload_folder(ULdirectory, cont)

  uploaded = 0
  while uploaded < total_bytes:
    time.sleep(2)
    uploaded = cf.get_uploaded(upload_key)
    print "Progress: %4.2f%%" % ((uploaded * 100.0) / total_bytes)

  print "Done!"

if __name__ == "__main__":
  print "\nChallenge3 - Write a script that accepts a directory as an argument"
  print "as well as a container name. The script should upload the contents"
  print "of the specified directory to the container (or create it if it"
  print "doesn't exist). The script should handle errors appropriately."
  print "(Check for invalid paths, etc.)\n\n" 

  parser = argparse.ArgumentParser()
  parser.add_argument("Directory", 
                      help="Directory containing files to upload to CONTAINER")
  parser.add_argument("Container", 
                      help="CloudFiles container")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create container (DFW or ORD)")

  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if c1.is_valid_region(args.region):
    cf = pyrax.connect_to_cloudfiles(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  ULDir = os.path.expanduser(args.Directory)
  ULContainer = args.Container

  # pyrax silently ignores 'no premissions to read dir' errors, so we check
  # for "read permissions" before calling pyrax
  if os.access(ULDir, os.R_OK):
    try:
      upload_dir_to_container(cf, ULDir, ULContainer)
    except pyrax.exceptions.FolderNotFound: 
      print 'The specified directory "%s" does not exist' % ULDir
  else:
    print 'ERROR!\nYou do not have read access to directory "%s"' % ULDir

# vim: ts=2 sw=2 tw=78 expandtab
