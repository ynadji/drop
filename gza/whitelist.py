#!/usr/bin/env python
#
# Checks against whitelists for matches.
#

import sys
from IPy import IP
from optparse import OptionParser

wl = set(['time.windows.com.',
          'ntp.org.',
          'alexa.com.',
          'googleapis.com.'])

ipwl = set([])

def makewhitelist(wlpath):
    with open(wlpath) as wlin:
        global wl
        for line in wlin:
            wl.add(line.split(',')[1].rstrip() + '.') # Alexa is missed '.'

def makeipwhitelist(wlpath):
    with open(wlpath) as wlin:
        global ipwl
        for line in wlin:
            if line.startswith('#') or line == '\n':
                continue
            for ip in IP(line.split(';')[0]):
                ipwl.add(long(ip.strDec()))

def whitelistedip(ip):
    if ip.startswith('192.168.'):
        return True
    addr = long(IP(ip).strDec())
    return addr in ipwl

def whitelisted(domain):
    pieces = domain.split('.')
    for i in range(len(pieces) - 2):
        if '.'.join(pieces[i:]) in wl:
            return True

    return False

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] input domain ... domain2"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        return 2

    # do stuff
    wl = makewhitelist(args[0])
    for domain in args[1:]:
        print('%s is %s' % (domain, 'whitelisted' if whitelisted(domain) else 'not whitelisted'))

if __name__ == '__main__':
    sys.exit(main())
