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
    description='Authenticates as zimbra administrator and returns a list\
    \nof accounts and their attrs(previously defined on zimbraAtributes.',
    formatter_class=RawTextHelpFormatter)
parser.add_argument('-a', '--admin', action='store', dest='admin',
                    help='Zimbra Admin Account to authenticate on server',
                    required=True)
parser.add_argument('-p', '--pass', action='store', dest='password',
                    help='Zimbra Admin Password String', required=True)
parser.add_argument('-d', '--domain', action='store', dest='domain',
                    help='Domain to get accounts info\
                    \n\tExample: \n--domain example.com', required=True)
parser.add_argument('-H', '--host', action='store', dest='hostname',
                    help='webmail URL', required=True)

argslist = parser.parse_args()

url = "https://" + argslist.hostname + ":7071/service/admin/soap"
admin = argslist.admin
password = argslist.password
domain = argslist.domain
comm = Communication(url)


def multipleReplace(text, wordDict):
    for key in wordDict:
        text = text.replace(key, wordDict[key])
    return text


def zimbraAttributes():
    return ['displayName',
            'description',
            'zimbraAccountStatus',
            'zimbraCOSId',
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
        resp = [response.get_response(1), response.get_response(2)]
        return resp
    else:
        print "Error on zimbraAdmin: " + str(response.get_fault_message())
        sys.exit(3)


accountlist = []
allInfo = getAllInfo(url, admin, password, domain)
accresp = allInfo[1]['GetAllAccountsResponse']['account']
cosresp = allInfo[0]['GetAllCosResponse']['cos']
cosdict = {}
archive = []
for cos in cosresp:
    cosdict[cos['id']] = cos['name']

line = "account"
for i in zimbraAttributes():
    line += ", %s" % (i)
archive.append(line)
for account in accresp:
    line = account['name']
    attrs = account['a']
    for i in zimbraAttributes():
        line += ","
        for x in attrs:
            if i.encode('utf-8') == x.values()[1].encode('utf-8'):
                line += multipleReplace(x.values()[0], cosdict)
    archive.append(line)

archive = sorted(archive)
print("\n".join(archive))
