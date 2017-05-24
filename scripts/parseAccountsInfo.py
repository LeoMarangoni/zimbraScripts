#!/usr/bin/python
# encoding=utf8

import sys
from datetime import datetime
from pythonzimbra.tools import auth
from pythonzimbra.communication import Communication
import argparse
from argparse import RawTextHelpFormatter
from modules import sendmail


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
parser.add_argument('-S', '--send-mail', dest='send_mail', nargs='+',
                    metavar=('email', 'smtp-server'),
                    help='Add this if you want to send output by email')


argslist = parser.parse_args()

url = "https://" + argslist.hostname + ":7071/service/admin/soap"
admin = argslist.admin
password = argslist.password
domain = argslist.domain
comm = Communication(url)
sendm = argslist.send_mail


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


def parseInfo():
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
    return("\n".join(archive))


if sendm is not None:
    try:
        smtpserver = sendm[1]
    except IndexError:
        smtpserver = argslist.hostname
    finally:
        today = datetime.now().date()
        subject = "Accounts List %s - %s" % (domain, today)
        message = "Hello,\nSAttached is the list of accounts\
                   of the domain %s" % (domain)
        path = "/tmp/%s.csv" % (domain)
        csv = open(path, "w")
        csv.write(str(parseInfo()))
        csv.close()
        try:
            sendmail.send_mail(admin,
                               [sendm[0]],
                               subject,
                               message,
                               server=smtpserver,
                               user=admin,
                               passw=password,
                               files=[path])
            print "List sent to %s, please check your mailbox" % (sendm[0])
        except Exception as e:
            print "%s, try to change smtp server" % e
else:
    print str(parseInfo())
