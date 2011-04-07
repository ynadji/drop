#!/usr/bin/env python
#
# Given a results output file, find identical malware samples by the gamed
# network results i.e.,:
#   given two distinct malware samples m and m'
#   if set(dnsw-domains(m)) == set(dnsw-domains(m')) and
#      set(null-domains(m)) != set(null-domains(m')):
#       m and m' are equal
#
# Do the same for IP addresses.
#

import sys
from optparse import OptionParser

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] the.results"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    sets = []
    # do stuff
    with open(args[0]) as results:
        # Ignore header
        _ = results.readline()
        for result in results:
            tmp = result.strip().split('\t')
            # md5 0, naiveips 2, naivedomains 4, dnswdomains 8, tcpwips 10
            sets.append((tmp[0][:-4],
                         set(tmp[2].split(',')), set(tmp[4].split(',')),
                         set(tmp[8].split(',')), set(tmp[10].split(','))))

    dnswout = open(args[0] + '-dnsw.dot', 'w')
    dnsnaiveout = open(args[0] + '-dnsnaive.dot', 'w')
    tcpwout = open(args[0] + '-tcpw.dot', 'w')
    tcpnaiveout = open(args[0] + '-tcpnaive.dot', 'w')

    dnswout.write('graph %s {\nnode [shape=point, label=""];\n' % 'asdf')
    dnsnaiveout.write('graph %s {\nnode [shape=point, label=""];\n' % 'asdf')
    tcpwout.write('graph %s {\nnode [shape=point, label=""];\n' % 'asdf')
    tcpnaiveout.write('graph %s {\nnode [shape=point, label=""];\n' % 'asdf')

    for i, (md5i, naiveipsi, naivedomainsi, dnswdomainsi, tcpwipsi) in enumerate(sets):

        dnswout.write('n%s;\n' % md5i)
        dnsnaiveout.write('n%s;\n' % md5i)
        tcpwout.write('n%s;\n' % md5i)
        tcpnaiveout.write('n%s;\n' % md5i)

        for md5j, naiveipsj, naivedomainsj, dnswdomainsj, tcpwipsj in sets[i + 1:]:
            if dnswdomainsi == dnswdomainsj and naivedomainsi != naivedomainsj:
                for domain in dnswdomainsi:
                    dnswout.write('n%s -- n%s;\n' % (md5i, md5j)) # Edge for each shared domain
                for domain in naivedomainsi:
                    if domain in naivedomainsj:
                        dnsnaiveout.write('n%s -- n%s;\n' % (md5i, md5j)) # Edge for each shared domain

            if tcpwipsi == tcpwipsj and naiveipsi != naiveipsj:
                for tcp in tcpwipsi:
                    tcpwout.write('n%s -- n%s;\n' % (md5i, md5j)) # Edge for each shared tcp
                for tcp in naiveipsi:
                    if tcp in naiveipsj:
                        tcpnaiveout.write('n%s -- n%s;\n' % (md5i, md5j)) # Edge for each shared tcp

    dnswout.write('}\n\n')
    dnsnaiveout.write('}\n\n')
    tcpwout.write('}\n\n')
    tcpnaiveout.write('}\n\n')

    dnswout.close()
    dnsnaiveout.close()
    tcpwout.close()
    tcpnaiveout.close()

if __name__ == '__main__':
    sys.exit(main())
