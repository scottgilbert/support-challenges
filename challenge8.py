#!/usr/bin/env python
# Challenge8 - Write a script that will create a static webpage served out of
# Cloud Files. The script must create a new container, cdn enable it, enable
# it to serve an index file, create an index file object, upload the object to
# the container, and create a CNAME record pointing to the CDN URL of the
# container. 
# Author: Scott Gilbert

# Requires the following parameter:
#  DNS name to create CNAME for (ie: 'www.example.com')
#
# Optional second parameter:
#  filename of "index" file to upload.  If not specified a default is created.

import sys, os, time
import pyrax
import challenge4 as c4

credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(credential_file)
cf = pyrax.cloudfiles
dns = pyrax.cloud_dns

defaultIndexFileContents='''<html>
<head><title>Sample Website Served by CloudFiles</title></head>
<body><b>Sample Website Served by CloudFiles</b><br>
<br>
Welcome to our sample website!
</body>
</html>'''
defaultIndexFileName='index.html'

def makeAWebsite(siteName, indexFileContents, indexFileName):
  """Create a simple website on CloudFiles using specified content

  Create a new, randomly named, public, CloudFiles container

  Upload the specified file (or a default, if not specified) to the new
  CloudFiles container.

  Set the "Index Page" on the Container to be the uploaded file.

  Create a DNS CNAME record for the specified name pointing to the CDN URL
  of the new CloudFiles container.
  """

  # Create a new, public, randomly named, container 
  contName = pyrax.utils.random_name(12, ascii_only=True)
  cont = cf.create_container(contName)
  print "New Container:", cont.name
  cf.make_container_public(cont)

  # Store index file contents in a new object 
  indexObj = cf.store_object(cont, indexFileName, indexFileContents)

  # Make this new image the "index page" for the container
  cf.set_container_web_index_page(cont, indexFileName)

  c4.createDNSRecord(siteName, cont.cdn_uri.lstrip('http://'), 'CNAME')
  print "Done!"

if __name__ == "__main__":

  if len(sys.argv) == 3:
    siteName = os.path.expanduser(sys.argv[1])
    indexFileName = os.path.expanduser(sys.argv[2])
    if os.path.isfile(indexFileName):
      indexFileContents = open(indexFileName, 'r').read()
      makeAWebsite(siteName, indexFileContents,
                  os.path.basename(indexFileName))
    else:
      print 'The specified file "%s" does not exist' % indexFile
  elif len(sys.argv) == 2:
    siteName = os.path.expanduser(sys.argv[1])
    makeAWebsite(siteName, defaultIndexFileContents, defaultIndexFileName)
  else:
    print "Wrong number of parameters specified!\n"
    print "Usage:  challenge8 <site name> <index file (optional)>\n"

# vim: ts=2 sw=2 tw=78 expandtab
