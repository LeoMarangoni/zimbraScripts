#!/usr/bin/python

import sys
from pythonzimbra.tools import auth
from pythonzimbra.communication import Communication
import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(
    description='Authenticates as zimbra administrator and get the number of\
    \nmessages in Inbox of accounts from user list.',
    formatter_class=RawTextHelpFormatter)
parser.add_argument('-a', '--admin', action='store', dest='admin',
                    help='Zimbra Admin Account to authenticate on server',
                    required=True)
parser.add_argument('-p', '--pass', action='store', dest='password',
                    help='Zimbra Admin Password String', required=True)
parser.add_argument('-u', '--users', action='store', dest='users',
                    help='List of accounts to be monitored\
                    \n\tExample:\n--users spam@example.com or\
                    \n--users spam@example.com,ham@example.com,act...,',
                    required=True)
parser.add_argument('-H', '--host', action='store', dest='hostname',
                    help='webmail URL', required=True)
parser.add_argument('-w', '--warning', action='store', dest='warn',
                    help='Warning threshold, type=int, default == 40',
                    default=40)
parser.add_argument('-c', '--critical', action='store', dest='crit',
                    help='Critical threshold, type=int, default == 50',
                    default=50)

argslist = parser.parse_args()


url = "https://" + argslist.hostname + ":7071/service/admin/soap"
admin = argslist.admin
password = argslist.password
account = argslist.users.split(',')
comm = Communication(url)
warning = argslist.warn
critical = argslist.crit
outmessage = []
outresp = {}


def getUserToken(url, adm, acc, pword):
    token = auth.authenticate(url, adm, pword, admin_auth=True)
    request = comm.gen_request(token=token)
    request.add_request(
        "DelegateAuthRequest",
        {
            "account": {
                "_content": acc,
                "by": "name"
            }
        },
        "urn:zimbraAdmin"
    )

    response = comm.send_request(request)
    if not response.is_fault():
        return response.get_response()['DelegateAuthResponse'][
            'authToken']['_content']
    else:
        print "Error on zimbraAdmin: " + response.get_fault_message()
        sys.exit(3)


def getAccountInbox(url, adm, acc, pword):
    usertoken = getUserToken(url, adm, acc, pword)
    request = comm.gen_request(token=usertoken)
    request.add_request(
        "GetFolderRequest",
        {
            "folder": {
                "path": "/inbox"
            }
        },
        "urn:zimbraMail"
    )
    response = comm.send_request(request)
    if not response.is_fault():
        return response.get_response()['GetFolderResponse']['folder']['n']
    else:
        print "Error on get Accounts: " + response.get_fault_message()
        sys.exit(3)


for i in range(0, len(account)):
    outresp[account[i]] = getAccountInbox(url, admin, account[i], password)

for i in outresp.values():
    if i >= int(critical):
        print "CRIT - messages on inbox: %s" % (outresp)
        sys.exit(2)

for i in outresp.values():
    if i >= int(warning):
        print "WARN - messages on inbox: %s" % (outresp)
        sys.exit(1)


print "OK - Messages on inbox OK!"
sys.exit(0)
