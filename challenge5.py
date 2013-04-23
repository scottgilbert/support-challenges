#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Challenge5 - Write a script that creates a Cloud Database instance. This
# instance should contain at least one database, and the database should have
# at least one user that can connect to it.

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
#   Instance                  Name of CloudDatabase Instance to create
#   Schema                    Name of database schema to create
#   User                      Username for database access
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --flavor FLAVOR           Flavor of database instance to create
#   --volumesize VOLUMESIZE   Size of database volume (GB)
#   --region REGION           Region in which to create database (DFW or ORD)


import sys
import os
import time
import argparse
import pyrax
import challenge1 as c1

def create_a_database(cdb, InstanceName, InstanceFlavor, VolumeSize, 
	                  DBName, DBUserName):
  """Create a new CloudDatabase instance, Schema and User
  (with randomly generated password)

  Print vital information about the newly created database.
  """
  # Create database instance
  print "Creating database instance %s" % InstanceName
  dbi = cdb.create(InstanceName, flavor=cdb.get_flavor(InstanceFlavor), 
                    volume=VolumeSize)

  # Wait for new database instance to become active
  print "Waiting for database instance build to complete..."
  while dbi.status <> 'ACTIVE':
    time.sleep(5)
    dbi.get()
    print '.',

  # Create database schema
  dbs = dbi.create_database(DBName)
  
  # Create database user
  userPassword = pyrax.utils.random_name(10, ascii_only=True)
  dbu = dbi.create_user(DBUserName, userPassword, database_names=DBName)

  print "\n\nNew Database Created!\n"
  print "Instance Name: %s" % dbi.name
  print "Instance Hostname: %s" % dbi.hostname
  print "Schema (database) Name: %s" % dbs.name
  print "User: %s" % dbu.name
  print "Password: %s" % userPassword

def is_valid_db_flavor(cdb, id):
  """Check the validity of a CloudDatabase flavor-id"""
  try:
    cdb.get_flavor(id)
    return True
  except:
    return False

if __name__ == "__main__":
  print "\nChallenge5 - Write a script that creates a Cloud Database instance."
  print "This instance should contain at least one database, and the database"
  print "should have at least one user that can connect to it.\n\n"

  parser = argparse.ArgumentParser()
  parser.add_argument("Instance", 
                      help="Name of CloudDatabase Instance to create")
  parser.add_argument("Schema", help="Name of database schema to create") 
  parser.add_argument("User", help="Username for database access")
  parser.add_argument("--flavor", default=1, 
                      help="Flavor of CloudDatabase to create")
  parser.add_argument("--volumesize", default=1, type=int,
                      help="Size of database volume (GB)")
  parser.add_argument("--region", default='DFW',
                      help="Region in which to create database (DFW or ORD)")
  args = parser.parse_args()

  credential_file = os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  if c1.is_valid_region(args.region, 'database'):
    cdb = pyrax.connect_to_cloud_databases(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  if not is_valid_db_flavor(cdb, args.flavor):
    print "This is not a valid CloudDatabase flavor-id: %s" % args.flavor
    sys.exit(3)

  if args.volumesize < 1 or args.volumesize > 150:
    print "The requested volume size is not valid: %d" % args.volumesize
    sys.exit(4)

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  create_a_database(cdb, args.Instance, args.flavor, args.volumesize, 
                  args.Schema, args.User)

# vim: ts=2 sw=2 tw=78 expandtab
