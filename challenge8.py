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

import sys, os, time, argparse
import pyrax
import challenge4 as c4


def makeAWebsite(cf, dns, siteName, contName, indexFileContents, 
                 indexFileName):
  """Create a simple website on CloudFiles using specified content

  Create a new, randomly named, public, CloudFiles container

  Upload the specified file (or a default, if not specified) to the new
  CloudFiles container.

  Set the "Index Page" on the Container to be the uploaded file.

  Create a DNS CNAME record for the specified name pointing to the CDN URL
  of the new CloudFiles container.
  """

  # Create a new, public container 
  cont = cf.create_container(contName)
  print "New Container:", cont.name
  cf.make_container_public(cont)

  # Store index file contents in a new object 
  indexObj = cf.store_object(cont, indexFileName, indexFileContents)

  # Make this new image the "index page" for the container
  cf.set_container_web_index_page(cont, indexFileName)

  c4.createDNSRecord(dns, siteName, cont.cdn_uri.lstrip('http://'), 'CNAME')
  print "Done!"

if __name__ == "__main__":
  print "\nChallenge8 - Write a script that will create a static webpage"
  print "served out of Cloud Files. The script must create a new container,"
  print "CDN enable it, enable it to serve an index file, create an index"
  print "file object, upload the object to the container, and create a CNAME"
  print "record pointing to the CDN URL of the container.\n\n"

  parser = argparse.ArgumentParser()
  parser.add_argument("FQDN", help="FQDN for the new website")
  parser.add_argument("--htmlfile", 
                      help="Local file containing new site's content", 
                      default=False)
  parser.add_argument("--container", 
                      help="CloudFiles container name to create",
                      default=False)
  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  cf = pyrax.cloudfiles
  dns = pyrax.cloud_dns
  
  if args.htmlfile:
    indexFileName = os.path.expanduser(args.htmlfile)
    if os.path.isfile(indexFileName):
      indexFileContents = open(indexFileName, 'r').read()
    else:
      print 'The specified file "%s" does not exist' % indexFile
  else:
    indexFileName = 'index.html'
    indexFileContents = '''<html>
      <head><title>Sample Website Served by CloudFiles</title></head>
      <body><b>Sample Website Served by CloudFiles</b><br>
        <br>
        Welcome to our sample challenge8 website!
        <br>
      </body>
     </html>'''

  if not args.container:
    args.container = pyrax.utils.random_name(12, ascii_only=True)

  makeAWebsite(cf, dns, args.FQDN, args.container, indexFileContents, 
               os.path.basename(indexFileName))

# vim: ts=2 sw=2 tw=78 expandtab
