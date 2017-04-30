#!/usr/bin/python 
# encoding=utf8

import sys
from pythonzimbra.tools import auth
from pythonzimbra.communication import Communication
import argparse
from argparse import RawTextHelpFormatter

reload(sys)
sys.setdefaultencoding('utf8')

parser = argparse.ArgumentParser(
    description='Authenticates as zimbra administrator and get the number of\
    \nmessages in Inbox of accounts from user list.',
    formatter_class=RawTextHelpFormatter)
parser.add_argument('-a', '--admin', action='store', dest='admin',
                    help='Zimbra Admin Account to authenticate on server',
                    required=True)
parser.add_argument('-p', '--pass', action='store', dest='password',
                    help='Zimbra Admin Password String', required=True)
parser.add_argument('-d', '--domains', action='store', dest='domains',
                    help='List of domains to get accounts info\
                    \n\tExample:\n--domains example.com or\
                    \n--domains example.net,example.com,exam...,',
                    required=True)
parser.add_argument('-H', '--host', action='store', dest='hostname',
                    help='webmail URL', required=True)

argslist = parser.parse_args()

url = "https://" + argslist.hostname + ":7071/service/admin/soap"
admin = argslist.admin
password = argslist.password
domains = argslist.domains.split(',')
comm = Communication(url)


def zimbraAtributes():
    return ['cn',
            'displayName',
            'zimbraAccountStatus',
            'zimbraCOSId',
            'zimbraIsAdminAccount',
            'zimbraPrefMailForwardingAddress',
            'zimbraLastLogonTimestamp']


def getAllInfo(url, adm, pword, domain):
    token = auth.authenticate(url, adm, pword, admin_auth=True)
    request = comm.gen_request(token=token, set_batch=True)
    request.add_request(
        "GetAllCosRequest",
        {
        },
        "urn:zimbraAdmin"
    )
    request.add_request(
        "GetAllAccountsRequest",
        {
            "domain": {
                "_content": domain,
                "by": "name"
            }
        },
        "urn:zimbraAdmin"
    )

    response = comm.send_request(request)
    if not response.is_fault():
        return response.get_response(2)
    else:
        return "Error on zimbraAdmin: " + response.get_fault_message()


accountlist = []
allInfo = getAllInfo(url, admin, password, domains[0])
accresp = allInfo['GetAllAccountsResponse']['account']
line = "account"
for i in zimbraAtributes():
    line += ", %s" % (i)
print (line)
for account in accresp:
    line = account['name']
    attrs = account['a']
    for i in zimbraAtributes():
        line += ","
        for x in attrs:
            if i.encode('utf-8') == x.values()[1].encode('utf-8'):
                line += x.values()[0]
    print (line)

# print allInfo
print (accresp[1].keys())
# print accresp[1]['a']['displayName']
