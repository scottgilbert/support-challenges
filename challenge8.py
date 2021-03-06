#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Challenge8 - Write a script that will create a static webpage served out of
# Cloud Files. The script must create a new container, cdn enable it, enable
# it to serve an index file, create an index file object, upload the object to
# the container, and create a CNAME record pointing to the CDN URL of the
# container. 

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

# Required Parameters:
#   FQDN                      FQDN for the new website
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --htmlfile                Local file containing new site's content
#   --container               CloudFiles container name to create
#   --region                  Region in which to create site (DFW or ORD)


import sys
import os
import argparse
import pyrax
import challenge4 as c4
import challenge1 as c1

def make_a_website(cf, dns, siteName, contName, indexFileContents, 
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

  c4.create_dns_record(dns, siteName, cont.cdn_uri.lstrip('http://'), 'CNAME')
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
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create site (DFW or ORD)")
  args = parser.parse_args()

  credential_file=os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if c1.is_valid_region(args.region, 'object_store'):
    cf = pyrax.connect_to_cloudfiles(region=args.region)
    dns = pyrax.connect_to_cloud_dns(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  if not c4.is_valid_hostname(args.FQDN):
    print "This does not appear to be a valid host name: %s" % args.FQDN
    sys.exit(3)

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

  make_a_website(cf, dns, args.FQDN, args.container, indexFileContents, 
                 os.path.basename(indexFileName))

# vim: ts=2 sw=2 tw=78 expandtab
