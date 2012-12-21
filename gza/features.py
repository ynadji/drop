#!/usr/bin/env python
#
# Extract Jaccard features for MD5s.
#

import sys
import os
from optparse import OptionParser

from domainsandips import domainsandips

def pcappath(md5, md5dir, gametype, t):
    return os.path.join(md5dir, '%s-%d-%s.pcap' % (md5, t, gametype))

def J(s1, s2):
    return float(len(s1 & s2)) / len(s1 | s2)

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] md5dir < md5list"
    parser = OptionParser(usage=usage)
    parser.add_option('-t', '--time', default=1800, type='int',
            help='Value of t used in experiments')

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    # pcap naming format: md5-duration-game.pcap

    features = []

    for md5 in sys.stdin:
        md5 = md5.strip()
        noneD, noneI = domainsandips(pcappath(md5, args[0], 'none', options.time))
        dnswtD, dnswtI = domainsandips(pcappath(md5, args[0], 'dnsw', options.time))
        tcpwtD, tcpwtI = domainsandips(pcappath(md5, args[0], 'tcpw', options.time))
        dnswt2D, dnswt2I = domainsandips(pcappath(md5, args[0], 'dnsw', options.time * 2))
        tcpwt2D, tcpwt2I = domainsandips(pcappath(md5, args[0], 'tcpw', options.time * 2))

        # domain name features
        features.append(J(noneD, dnswtD))
        features.append(J(noneD, dnswt2D))
        features.append(J(dnswtD, dnswt2D))

        # IP features
        features.append(J(noneI, dnswtI))
        features.append(J(noneI, dnswt2I))
        features.append(J(dnswtI, dnswt2I))

        print('%s\t%s' % (md5, '\t'.join(map(str, features))))
        del features[:]

if __name__ == '__main__':
    sys.exit(main())
