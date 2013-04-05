#!/usr/bin/env python
# Challenge5 - Write a script that creates a Cloud Database instance. This
# instance should contain at least one database, and the database should have
# at least one user that can connect to it.
# Author: Scott Gilbert


# Requires the following two parameters:
#  DB Instance Name
#  DB Schema Name
#  DB User Name

import sys, os, time
import pyrax

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
  print "Challenge5 - Write a script that creates a Cloud Database instance."
  print "This instance should contain at least one database, and the database"
  print "should have at least one user that can connect to it.\n\n"

  credential_file = os.path.expanduser("~/.rackspace_cloud_credentials")
  pyrax.set_credential_file(credential_file)
  cdb = pyrax.cloud_databases
  
  # Instance Flavor (512MB RAM)
  InstanceFlavor = 1
  
  # Volume Size (1 GB)
  VolumeSize = 1

  # unbuffer stdout for pretty output
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  if len(sys.argv) == 4:
    InstanceName = sys.argv[1]
    DBName = sys.argv[2]
    DBUserName = sys.argv[3]
    CreateADatabase(cdb, InstanceName, InstanceFlavor, VolumeSize, DBName, 
                    DBUserName)
  else:
    print "Wrong number of parameters specified!"
    print "Usage:  challenge5 <DBInstanceName> <SchemaName> <UserName>"

# vim: ts=2 sw=2 tw=78 expandtab
