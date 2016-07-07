#!/usr/bin/python
#
# Ian Altgilbers
# ian@altgilbers.com
#
# XML-RPC script to synchronize group memberships between two servers
#  - written because we changed from Delegated directory to a "Connector" directory
#    group memerships had be be reestablished, so we made a copy on another server and
#    synced



import sys, string, xmlrpclib, urllib, os, datetime

def sendError(message):
    print message
    sys.exit(2)

source_wikiHost = 'source.example.net'
source_confluenceUser = "username"
source_confluencePasswd = "password"
source_url="https://" + source_wikiHost + "/confluence/rpc/xmlrpc"

dest_wikiHost = 'destination.example.net'
dest_confluenceUser = "username"
dest_confluencePasswd = "password"
dest_url="https://" + dest_wikiHost + "/confluence/rpc/xmlrpc"

### Flags
_DEBUG = 0


### Now, we try to contact the Confluence server
try:
    source_server = xmlrpclib.ServerProxy(source_url);
except:
    sendError("Could not connect to the URL" + source_url)
try:
    dest_server = xmlrpclib.ServerProxy(dest_url);
except:
    sendError("Could not connect to the URL" + dest_url)

try:
    source_token = source_server.confluence2.login(source_confluenceUser, source_confluencePasswd);
except xmlrpclib.Fault, fault:
    print fault.faultString
    sendError("Could not log into " + source_url)
if _DEBUG:
    print "Logged into Confluence server"

try:
    dest_token = dest_server.confluence2.login(dest_confluenceUser, dest_confluencePasswd);
except xmlrpclib.Fault, fault:
    print fault.faultString
    sendError("Could not log into " + dest_url)
if _DEBUG:
    print "Logged into Confluence server"

try:
    source_groups = source_server.confluence2.getGroups(source_token)
    dest_groups = dest_server.confluence2.getGroups(dest_token)
except xmlrpclib.Fault, fault:
    print fault.faultString
    sendError("Could not fetch list of groups" )


print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print str(len(source_groups)) + " groups on " + source_wikiHost
print str(len(dest_groups)) + " groups on " + dest_wikiHost


###  group names must be lower case... existing groups must be downcased before being recreated
for group in source_groups:
	dest_server.confluence2.addGroup(dest_token,group.lower())
	print "Adding group "+group.lower()+" to "+dest_wikiHost


### now that groups are synced, we can sync memberships.
# this has to be done user by user, because there is not function to get all users in a group, only get all 
try:
    source_users = source_server.confluence2.getActiveUsers(source_token, True)
    dest_users = dest_server.confluence2.getActiveUsers(dest_token, True)
except xmlrpclib.Fault, fault:
    print fault.faultString
    sendError("Could not fetch list of users" )


for user in dest_users:
	try:
		source_user_groups=source_server.confluence2.getUserGroups(source_token,user)
	except xmlrpclib.Fault, fault:
		print "user "+user+" not in source server"
	for group in source_user_groups:
        	dest_server.confluence2.addUserToGroup(dest_token,user,group.lower())
        	print "Adding user "+user+" to group "+group.lower()+" on "+dest_wikiHost

print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print "Finished processing group memberships"
