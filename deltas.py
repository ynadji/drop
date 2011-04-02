#!/usr/bin/env python
#
# Given results output from results.py, determine from the additional network
# features coerced by your games:
# * The delta (num days) domains/ips take to appear on blacklists,
# * The status of the 2LD on blacklists.
#
# Do this for each sample (row in results file) as well as an aggregate of all
# games in the results file. You can then do the same thing for the aggregate
# results to get an idea of the overall behavior.
#
# NOTE: Doing so is contigent on the DATE the samples WERE RUN. Take the date
# from the results filename. For the aggregate, report simply the percentage of
# domains/ips that never appeared on the blacklists.
#
# 2224 drop:master!? % time ./deltas.py tcpdump/raid11/results.aggregate
# Never blacklisted: 89273
# Blacklisted eventually: 1563
# real 2583.07
# user 12.67
# sys 3.03
#
#

import sys
import os
import psycopg2
from optparse import OptionParser
from dateutil.parser import parse
from itertools import chain
import numpy as np

sys.path.append('wulib')
from wulib import flatten, unique

def deserialize(md5, noneipcount, noneips, nonedomaincount, nonedomains, dnswipcount, dnswips, dnswdomaincount, dnswdomains, tcpwipcount, tcpwips, tcpwdomaincount, tcpwdomains):
    # Make ints
    noneipcount = int(noneipcount)
    nonedomaincount = int(nonedomaincount)
    dnswipcount = int(dnswipcount)
    dnswdomaincount = int(dnswdomaincount)
    tcpwipcount = int(tcpwipcount)
    tcpwdomaincount = int(tcpwdomaincount)

    # Make lists
    noneips = noneips.split(',')
    nonedomains = nonedomains.split(',')
    dnswips = dnswips.split(',')
    dnswdomains = dnswdomains.split(',')
    tcpwips = tcpwips.split(',')
    # We couldn't remove the newline earlier because it breaks cases where tcpdomains has
    # no domains listed (strips entire thing)
    tcpwdomains = tcpwdomains.rstrip().split(',')

    return (md5, noneipcount, noneips, nonedomaincount, nonedomains, dnswipcount, dnswips, dnswdomaincount, dnswdomains, tcpwipcount, tcpwips, tcpwdomaincount, tcpwdomains)

def deltas(conn, gameinfo, vanillainfo, date, ip=False):
    gameinfo = set(gameinfo)
    vanillainfo = set(vanillainfo)
    c = conn.cursor()
    daygains = []
    decoms = []
    incampaign = []
    nevers = []

    ipordomains = gameinfo - vanillainfo

    for ipordomain in ipordomains:
        if ip:
            q = "SELECT fdate, ldate FROM label_ip WHERE ip = '%s'" % ipordomain
        else:
            q = "SELECT fdate, ldate FROM label_zones WHERE dn = '%s'" % ipordomain
        c.execute(q)
        try:
            fdate, ldate = c.fetchone()

            delta = fdate - date
            if delta.days > 0:  # daygain case
                daygains.append((ipordomain, delta.days))
            else:
                delta = ldate - date
                if delta.days > 0:  # incampaign case
                    incampaign.append((ipordomain, date))
                else: # decoms case
                    decoms.append((ipordomain, delta.days))
        except TypeError: # nevers case
            nevers.append((ipordomain, date))

    c.close()
    return (daygains, decoms, incampaign, nevers)

def parsedelta(ipordns_gametype):
    try:
        x, y = zip(*[(x[0], x[1]) for x in unique(flatten(filter(None, ipordns_gametype)))])
        return (x, y)
    except ValueError: # Empty list
        return ([], [])


def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] exp.results"
    parser = OptionParser(usage=usage)
    parser.add_option('-g', '--games', default='none,dnsw,tcpw',
            help='Games played in the results file [default: %default]')

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    try:
        date = parse(os.path.basename(args[0])[:8])
    except ValueError:
        date = None # Change this to put today's date

    # Open DB connection
    conn = psycopg2.connect(host='tyr.gtisc.gatech.edu', database='pdmb', user='yacin')
    alldnsresults = []
    alltcpresults = []

    # do stuff
    with open(args[0]) as results:
        header = results.readline().strip()
        for exp in results:
            desargs = exp.split('\t')
            md5, noneipcount, noneips, nonedomaincount, nonedomains, dnswipcount, dnswips, dnswdomaincount, dnswdomains, tcpwipcount, tcpwips, tcpwdomaincount, tcpwdomains = deserialize(*desargs)

            # tcpw won
            if tcpwipcount > noneipcount:
                alltcpresults.append(deltas(conn, tcpwips, noneips, date, ip=True))

            # dnsw won
            if dnswdomaincount > nonedomaincount:
                alldnsresults.append(deltas(conn, dnswdomains, nonedomains, date))

    dnsdaygains, dnsdecoms, dnsincampaign, dnsnevers = zip(*alldnsresults)
    tcpdaygains, tcpdecoms, tcpincampaign, tcpnevers = zip(*alltcpresults)

    # Deltas
    domains1, dnsdaygains =   parsedelta(dnsdaygains)
    domains2, dnsdecoms =     parsedelta(dnsdecoms)
    domains3, dnsincampaign = parsedelta(dnsincampaign)
    domains4, dnsnevers =     parsedelta(dnsnevers)
    ips1, tcpdaygains =   parsedelta(tcpdaygains)
    ips2, tcpdecoms =     parsedelta(tcpdecoms)
    ips3, tcpincampaign = parsedelta(tcpincampaign)
    ips4, tcpnevers =     parsedelta(tcpnevers)

    # Unique domains
    uniquedomains = list(unique(chain(domains1, domains2, domains3, domains4)))
    uniqueips = list(unique(chain(ips1, ips2, ips3, ips4)))

    conn.close()
    print('DNS Blacklisted eventually: %d / %d, (Mean, Var): (%f, %f)' %
            (len(dnsdaygains), len(uniquedomains), np.mean(dnsdaygains), np.var(dnsdaygains)))
    print('DNS Decommissioned: %d / %d, (Mean, Var): (%f, %f)' %
            (len(dnsdecoms), len(uniquedomains), np.mean(dnsdecoms), np.var(dnsdecoms)))
    print('DNS In Campaign: %d / %d' %
            (len(dnsincampaign), len(uniquedomains)))
    print('DNS Never blacklisted: %d / %d' %
            (len(dnsnevers), len(uniquedomains)))
    print('IP Blacklisted eventually: %d / %d, (Mean, Var): (%f, %f)' %
            (len(tcpdaygains), len(uniqueips), np.mean(tcpdaygains), np.var(tcpdaygains)))
    print('IP Decommissioned: %d / %d, (Mean, Var): (%f, %f)' %
            (len(tcpdecoms), len(uniqueips), np.mean(tcpdecoms), np.var(tcpdecoms)))
    print('IP In Campaign: %d / %d' %
            (len(tcpincampaign), len(uniqueips)))
    print('IP Never blacklisted: %d / %d' %
            (len(tcpnevers), len(uniqueips)))

if __name__ == '__main__':
    sys.exit(main())
