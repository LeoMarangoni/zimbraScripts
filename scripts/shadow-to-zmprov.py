#!/usr/bin/python

"""
    Usage:
        Shadow: Set Linux Shadow file path used by postfix
        Domain: Change to your default domain
        ignored: Put here accounts to be ignored. 
                 Example: ignored = ["john, "dennys"]
        prov_account = Set False if you wanna just set password,
                       instead of create accounts.

    In postfix server run:
        sudo chmod +x shadow-to-zmprov.py
        sudo ./shadow-to-zmprov.py > accounts.prov
    
    Copy accounts.prov to zimbra server and run:
        su - zimbra or sudo su - zimbra
        zmprov -f accounts.prov
"""

shadow = "/etc/shadow" # default: "/etc/shadow"
domain = "example.com"
ignored = []
prov_account = True # If True, create account before set pass hash
try:
    shadow = open(shadow, "r")
    shadow = shadow.read()
    shadow = shadow.split("\n")
except (IOError):
    print "File %s doesn't exist" % (shadow)
    raise SystemExit(400)    

for line in shadow:
    line = line.split(":")
    user = line[0]
    passwd = line[1]
    if passwd != "*" and user not in ignored:
        if prov_account:
            print "zmprov ca %s@%s CreateAccount@Pass12345" % (user, domain)
        print "zmprov ma %s@%s userPassword '{crypt}%s'" % (user, domain, passwd)
