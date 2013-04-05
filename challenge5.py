#!/usr/bin/env python
# Challenge5 - Write a script that creates a Cloud Database instance. This
# instance should contain at least one database, and the database should have
# at least one user that can connect to it.
# Author: Scott Gilbert


# Requires the following three parameters:
#  DB Instance Name
#  DB Schema Name
#  DB User Name

import sys, os, time, argparse
import pyrax
import challenge1 as c1

def CreateADatabase(cdb, InstanceName, InstanceFlavor, VolumeSize, 
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
  if c1.isValidRegion(args.region):
    cdb = pyrax.connect_to_cloud_databases(region=args.region)
  else:
    print "The region you requested is not valid: %s" % args.region
    sys.exit(2)

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  CreateADatabase(cdb, args.Instance, args.flavor, args.volumesize, 
                  args.Schema, args.User)

# vim: ts=2 sw=2 tw=78 expandtab
