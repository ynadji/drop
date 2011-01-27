#!/usr/bin/env python

import sys
import glob
import os
from optparse import OptionParser
from itertools import chain, izip, repeat

sys.path.append('gza')
import ud
import whitelist

def intersperse(lst1, lst2):
    return chain.from_iterable(izip(lst1, lst2))

def notwhitelisted(domain):
    return not whitelist.whitelisted(domain)

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] dir"
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--games", dest="games", default="none",
            help="Games to analyze (comma separated list of: none,dns,dns5)")
    parser.add_option("-w", "--whitelist", dest="whitelist", default="gza/top1000.csv",
            help="Whitelist Alexa CSV to use [default: %default]")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    whitelist.makewhitelist(options.whitelist)

    # do stuff
    pcaps = glob.glob(os.path.join(args[0], '*.pcap'))
    games = options.games.split(',')
    print('md5\t' + '\t'.join(intersperse(games, repeat('domains'))))
    # Get just md5.exe
    md5s = set([os.path.basename(x)[:36] for x in pcaps])
    for md5 in md5s:
        md5res = []
        for game in games:
            pcapfile = os.path.realpath(os.path.join(args[0], md5) + '-' + game + '.pcap')
            md5res.append(filter(notwhitelisted, ud.unique_domains(pcapfile)))

        domaincounts = [str(len(x)) for x in md5res]
        domainstrs = [','.join(domains) for domains in md5res]
        sys.stdout.write(md5 + '\t')
        print('\t'.join(intersperse(domaincounts, domainstrs)))

if __name__ == '__main__':
    sys.exit(main())
