#!/usr/bin/python
#
# Ian Altgilbers
# ian@altgilbers.com
#
# quick XML-RPC script to add users to confluence-users if they are not already
# - When using a "Connector" type directory in Confluence, user accounts are automatically
#   created, but they are not "full-fledged" accounts until they first log in and 
#   are added to confluence-users group.
#
#   This was written to let us retire a tool that allowed an admin to bulk-add user accounts
#


import sys, string, xmlrpclib, urllib, os, datetime

def sendError(message):
    print message
    sys.exit(2)

### Defaults
wikiHost = 'wiki.example.net'
confluenceUser = "username"
confluencePasswd = "password"
url="https://" + wikiHost + "/confluence/rpc/xmlrpc"

### Flags
_DEBUG = 0


### Now, we try to contact the Confluence server
try:
    server = xmlrpclib.ServerProxy(url);
except:
    sendError("Could not connect to the URL" + url)

try:
    token = server.confluence2.login(confluenceUser, confluencePasswd);
except xmlrpclib.Fault, fault:
    print fault.faultString
    sendError("Could not log into " + url)
if _DEBUG:
    print "Logged into Confluence server"

try:
    ### users that can use Confluence 
    activeUserList = server.confluence2.getActiveUsers(token, False)
    ### all users
    completeUserList = server.confluence2.getActiveUsers(token, True)
except xmlrpclib.Fault, fault:
    print fault.faultString
    sendError("Could not fetch list of users" )

#create a list of users who are not in 
newUsersList=list(set(completeUserList)-set(activeUserList))
#sort just to make monitoring progress easy
newUsersList.sort()

print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print str(len(activeUserList)) + " users in confluence-users"
print str(len(completeUserList)) + " users in system as a whole"
print "Adding "+ str(len(newUsersList)) + " new users to confluence-users"

for user in newUsersList:
    try:
        server.confluence2.addUserToGroup(token,user,"confluence-users")
    except xmlrpclib.Fault, fault:
	print fault.faultString
	sendError("Could not add user to group")
    print user+" - added to confluence-users"


