#!/usr/bin/env python
# Challenge3 - Write a script that accepts a directory as an argument as well
# as a container name. The script should upload the contents of the specified
# directory to the container (or create it if it doesn't exist). The script
# should handle errors appropriately. (Check for invalid paths, etc.)  
# Author: Scott Gilbert

# Requires the following two parameters:
#  source directory containing files to be uploaded
#  destination cloudfiles container

import sys, os, time
import pyrax

credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(credential_file)
cf = pyrax.cloudfiles

def UploadDirToContainer(ULdirectory, ULContainer):
  """ Upload contents of a local directory to a CloudFiles Container

  If the specified CloudFiles container does not already exist, then it
  is created.

  A simple progress message is displayed every 2 seconds and function
  does not return until upload completes.
  """

  # if container does not already exist, then create it!
  try:
    cont = cf.get_container(ULContainer)
  except:
    cont = cf.create_container(ULContainer)

  print 'Uploading the contents of %s to CloudFiles container %s:' % \
    (ULdirectory, ULContainer)
  upload_key, total_bytes = cf.upload_folder(ULdirectory, cont)

  uploaded = 0
  while uploaded < total_bytes:
    time.sleep(2)
    uploaded = cf.get_uploaded(upload_key)
    print "Progress: %4.2f%%" % ((uploaded * 100.0) / total_bytes)

  print "Done!"

if __name__ == "__main__":

  if len(sys.argv) == 3:
    ULDir = os.path.expanduser(sys.argv[1])
    ULContainer = sys.argv[2]
    # pyrax silently ignores 'no premissions to read dir' errors, so we check
    # for "read permissions" before calling pyrax
    if os.access(ULDir, os.R_OK):
      try:
        UploadDirToContainer(ULDir, ULContainer)
      except pyrax.exceptions.FolderNotFound: 
        print 'The specified directory "%s" does not exist' % ULDir
    else:
      print 'ERROR!\nYou do not have read access to directory "%s"' % ULDir
  else:
    print "Wrong number of parameters specified!"
    print "Usage:  challenge3 <directory> <CloudFiles Container>"

# vim: ts=2 sw=2 tw=78 expandtab