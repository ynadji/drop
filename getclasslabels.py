#!/usr/bin/env python

import sys
from optparse import OptionParser
sys.path.append('wulib')
from wulib import chunks

def iscount(var):
    try:
        int(var)
        return True
    except ValueError:
        return False

def gameworked(fields):
    # Fields will be an array of the counts. So for my current set of
    # experiments, it'll be
    # noneipcount,nonedomaincount,g1ipcount,g1domaincount...
    #
    # So, pop the first two off the list and compare them against the even and
    # odd values.
# noneipcount	nonedomaincount	dns1ipcount	dns1domaincount	dnswipcount	dnswdomaincount	tcpwipcount	tcpwdomaincount	tcp1ipcount	tcp1domaincount	tcp2ipcount	tcp2domaincount	tcp3ipcount	tcp3domaincount
    fields = [int(x) for x in fields]
    noneip = fields[0]
    nonedns = fields[1]
    dns1domaincount = fields[3]
    dnswdomaincount = fields[5]
    tcpwipcount = fields[6]
    tcp1ipcount = fields[8]
    tcp2ipcount = fields[10]
    tcp3ipcount = fields[12]

    if dns1domaincount > nonedns or dnswdomaincount > nonedns:
        return True
    if tcpwipcount > noneip or tcp1ipcount > noneip or tcp2ipcount > noneip \
            or tcp3ipcount > noneip:
                return True

    return False

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] results"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    # do stuff
    print('md5\tgameworked')
    with open(args[0]) as results:
        results.readline() # Ignore header
        for line in results:
            fields = line.split('\t')
            fields[0] = fields[0].replace('.exe', '')
            countfields = filter(iscount, fields)
            if gameworked(countfields):
                print('%s\tYES' % fields[0])
            else:
                print('%s\tNO' % fields[0])

if __name__ == '__main__':
    sys.exit(main())
