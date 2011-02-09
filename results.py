#!/usr/bin/env python

import sys
import glob
import os
import re
from optparse import OptionParser
from itertools import chain, izip, repeat

sys.path.append('gza')
from domainsandips import domainsandips
import whitelist
from multiprocessing import Pool, cpu_count

sys.path.append('wulib')
import wulib as wu

def intersperse(lst1, lst2):
    return chain.from_iterable(izip(lst1, lst2))

def notwhitelisted(domain):
    return not whitelist.whitelisted(domain)

def notwhitelistedip(ip):
    return not whitelist.whitelistedip(ip)

def run((md5, options)):
    try:
        # do stuff
        games = options.games.split(',')
        md5 = md5 + '.exe'
        md5res = []
        ipres = []
        for game in games:
            pcapfile = os.path.realpath(os.path.join(options.dir, md5) + '-' + game + '.pcap')
            uniqdomains, uniqips = domainsandips(pcapfile)
            if options.whitelist:
                uniqdomains = filter(notwhitelisted, uniqdomains)
                uniqips = filter(notwhitelistedip, uniqips)
            md5res.append(uniqdomains)
            ipres.append(uniqips)

        res = []
        domaincounts = [str(len(x)) for x in md5res]
        domainstrs = [','.join(domains) for domains in md5res]
        ipcounts = [str(len(x)) for x in ipres]
        ipstrs = [','.join(ips) for ips in ipres]

        for i in range(len(ipstrs)):
            res.append(ipcounts[i])
            res.append(ipstrs[i])
            res.append(domaincounts[i])
            res.append(domainstrs[i])
        res.insert(0, md5)
        return '\t'.join(res)
    except KeyboardInterrupt as e:
        return 'User interrupt!'

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] dir"
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--games", dest="games", default="none",
            help="Games to analyze (comma separated list of: none,dns,dns5)")
    parser.add_option("-w", "--whitelist", dest="whitelist", default=False,
            action='store_true', help="Use whitelist")
    parser.add_option("-p", "--whitelistpath", default="gza/top1000.csv",
            help="Whitelist Alexa CSV to use [default: %default]")
    parser.add_option("-i", "--ipwhitelistpath", default="gza/generic-dnswl",
            help="IP whitelist to use [default: %default]")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    options.dir = args[0]
    if options.whitelist:
        whitelist.makewhitelist(options.whitelistpath)
        whitelist.makeipwhitelist(options.ipwhitelistpath)

    # Print header
    games = options.games.split(',')
    headers = []
    for g in games:
        headers.append(g + 'ipcount')
        headers.append(g + 'ips')
        headers.append(g + 'domaincount')
        headers.append(g + 'domains')

    print('md5\t' + '\t'.join(headers))

    try:
        p = Pool(cpu_count())
        pcaps = glob.glob(os.path.join(args[0], '*.pcap'))
        # Only send the MD5s
        r = re.compile('([0-9a-fA-F]{32})\.exe')
        md5s = wu.unique([re.search(r, x).group(1) for x in pcaps])
        res_it = p.imap_unordered(run, izip(md5s, repeat(options)), 100)
        for res in res_it:
            print(res)
    except KeyboardInterrupt as e:
        sys.stderr.write('User termination!\n')
        p.terminate()

if __name__ == '__main__':
    sys.exit(main())
