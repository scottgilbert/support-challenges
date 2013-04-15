#!/usr/bin/env python
# Challenge 12: Write an application that will create a route in mailgun so
# that when an email is sent to <YourSSO>@apichallenges.mailgun.org it calls
# your Challenge 1 script that builds 3 servers.
# Author: Scott Gilbert

# Required Parameters:
#   none
#
# Optional Parameters:
#   -h, --help                show help message and exit
#   --email EMAILADDR         email address for which to create route
#                             (default is
#                             scott.gilbert@apichallenges.mailgun.org)
#   --dest STRING             Either a email address or URL to which to route
#                             the email. (default is
#                             http://cldsrvr.com/challenge1) 
#   --list                    List routes. No new routes are created.
#   --delete ID               Delete route identified by ID.
#   --priority PRIORITY       Priority of new route.
#   --description DESCRIPTION Description of new route.


import sys, os, argparse
import requests
import json

def mg_list_routes(apiKey):
  routes = requests.get("https://api.mailgun.net/v2/routes", 
                        auth=("api", apiKey))
  #print routes.text
  routedict =  json.loads(routes.text)
  print "Priority            ID                  Description       ",
  print "Expression/Action"
  print "-------- -------------------------  ------------------- ",
  print "------------------------------"
  for r in routedict['items']:
    print "%7s  %-25s  %-20s %s" % (r['priority'], r['id'], r['description'], 
                           r['expression'])
    for a in r['actions']:
      print "%7s  %-25s  %-20s %s" % ('', '', '', a)
  return routes

def mg_delete_route(apiKey, routeID):
  print "Deleting route %s" % routeID
  return requests.delete("https://api.mailgun.net/v2/routes/%s" % routeID,
                         auth=("api", apiKey))

def mg_create_route(apiKey, email, dest, priority, desc):
  print "Creating route for %s, with priority %s," % (email, priority),
  print "to %s with description '%s'" % (dest, desc)
  return requests.post("https://api.mailgun.net/v2/routes", 
                       auth=("api", apiKey),
                       data={"priority": priority,
                             "description": desc,
                             "expression": "match_recipient('%s')" % email,
                             "action": "forward('%s')" % dest}) 

if __name__ == "__main__":
  print "\nChallenge 12: Write an application that will create a route in"
  print "mailgun so that when an email is sent to",
  print "<YourSSO>@apichallenges.mailgun.org\nit calls your Challenge 1",
  print "script that builds 3 servers\n\n"

  parser = argparse.ArgumentParser()
  parser.add_argument("--email",
                      default="scott.gilbert@apichallenges.mailgun.org",
                      help="Email address for which to create route")
  parser.add_argument("--dest", default="http://cldsrvr.com/challenge1",
                      help="Either a email address or URL to which to route")
  parser.add_argument("--priority", default=50, type=int,
                      help="Priority of new route")
  parser.add_argument("--description", default="Challenge12 route",
                      help="Description of new route")
  group = parser.add_mutually_exclusive_group()
  group.add_argument("--list", action="store_true",
                      help="List routes. No routes are created.")
  group.add_argument("--delete", 
                      help="Delete route identified by ID.")
  args = parser.parse_args()

  credential_file = os.path.expanduser("~/.mailgunapi")
  apiKey = open(credential_file, 'r').read().strip()

  if args.list:
    mg_list_routes(apiKey)
  elif args.delete:
    mg_delete_route(apiKey, args.delete)
  else:
    mg_create_route(apiKey, args.email, args.dest, args.priority,
                    args.description)

# vim: ts=2 sw=2 tw=78 expandtab
