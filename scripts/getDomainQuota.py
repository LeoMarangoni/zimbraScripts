#!/usr/bin/python

"""
In future will be implement a parameter to return in bytes, Kbytes,
Mbytes and Gbytes view, but now I am feeling lazy.
"""


import sys
from pythonzimbra.tools import auth
from pythonzimbra.communication import Communication
import argparse
from argparse import RawTextHelpFormatter
from modules import sendmail
from datetime import datetime


reload(sys)
sys.setdefaultencoding('utf8')

parser = argparse.ArgumentParser(
    description='Authenticates as zimbra administrator and returns a list\
    \nof accounts and their quota usage.',
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
sendm = argslist.send_mail
comm = Communication(url)


def getAllInfo(url, adm, pword, domain):
    token = auth.authenticate(url, adm, pword, admin_auth=True)
    request = comm.gen_request(token=token)
    request.add_request(
        "GetQuotaUsageRequest",
        {
            "domain": domain,
            "allServers": "1"
        },
        "urn:zimbraAdmin"
    )

    response = comm.send_request(request)
    if not response.is_fault():
        return response.get_response()['GetQuotaUsageResponse']['account']
    else:
        return "Error on zimbraAdmin: " + response.get_fault_message()


def getDomainQuota():
    archive = []
    for account in getAllInfo(url, admin, password, domain):
        archive.append("%s,%i,%i" % (account['name'],
                                     int(account['used'] / 1024 / 1024),
                                     int(account['limit'] / 1024 / 1024))
                       )

    archive = sorted(archive)
    return("\n".join(archive))


if sendm is not None:
    try:
        smtpserver = sendm[1]
    except IndexError:
        smtpserver = argslist.hostname
    finally:
        today = datetime.now().date()
        subject = "Quotas - Accounts List %s - %s" % (domain, today)
        message = "Hello,\nSAttached is the list of accounts\
                   of the domain %s" % (domain)
        path = "/tmp/%s.csv" % (domain)
        csv = open(path, "w")
        csv.write(str(getDomainQuota()))
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
    print str(getDomainQuota())
