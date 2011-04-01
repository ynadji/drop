#!/usr/bin/env python
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import sys
import re
from optparse import OptionParser

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] results.tab"
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--show', default=False, action='store_true',
            help='Show figure instead of save it to PNG [default: %default]')

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    # do stuff
    matchupregex = re.compile('"(\w+ < \w+)"')
    dnsgames = []
    tcpgames = []
    dnsnames = []
    tcpnames = []
    gains = []
    inlist = False

    with open(args[0]) as results:
        for line in results:
            line = line.strip()

            try:
                # Get competing games: [1] "nonedomaincount < dnswdomaincount"
                # and store "sensible" ones (domaincount for dns, etc.)
                controlgame, expgame = matchupregex.search(line).group(1).split(' < ')
            except AttributeError:
                pass

            # Determine if we're in vector output from R
            if line.startswith('c('):
                inlist = True
                line = line[2:]
            if inlist:
                # Looks like: 2L, 1L, 4L, 8L,
                try:
                    gains.extend(map(long, re.sub(r'\s+', '', line)[:-1].split(',')))
                except ValueError:
                    sys.stderr.write('map failed, if line isnt just ")", you have a problem\n')
                    sys.stderr.write('line: %s\n' % line)
                    inlist = False
            if line.endswith('L)'):
                inlist = False
                if 'dns' in expgame and 'domaincount' in controlgame:
                    dnsgames.append(gains)
                    dnsnames.append(expgame)
                elif 'tcp' in expgame and 'ipcount' in controlgame:
                    tcpgames.append(gains)
                    tcpnames.append(expgame)

                gains = []

    # Thank you color brewer (http://colorbrewer2.org/)
    dnscolors = ['#1B9E77', '#D95F02'][:len(dnsgames)]
    tcpcolors = ['#7570B3', '#E7298A', '#66A61E', '#E6AB02'][:len(tcpgames)]

    dnsnames = ['$G_{\mathrm{%s}}$' % x[:4] for x in dnsnames]
    tcpnames = ['$G_{\mathrm{%s}}$' % x[:4] for x in tcpnames]

    plt.subplot(211)
    for game, color, name in zip(tcpgames, tcpcolors, tcpnames):
        n, bins, patches = plt.hist(game, len(game), facecolor=color, alpha=0.75, range=(1, 60), label=name)
    #n, bins, patches = plt.hist(tcpgames, len(max(tcpgames, key=len)), color=tcpcolors, range=(1, 60), label=tcpnames)
    # Not sure why the commented-out line above doesn't work. It's treating the list of colors as a single
    # color value, rather than the color for each entry.

    plt.grid(True)
    plt.ylabel('Frequency of samples')
    plt.xlabel('(a) Raw increase in IP addresses')
    plt.legend()

    plt.subplot(212)
    for game, color, name in zip(dnsgames, dnscolors, dnsnames):
        n, bins, patches = plt.hist(game, len(game), facecolor=color, alpha=0.75, range=(1, 60), label=name)

    plt.grid(True)
    plt.ylabel('Frequency of samples')
    plt.xlabel('(b) Raw increase in domain names')
    plt.legend()

    if options.show:
        plt.show()
    else:
        plt.savefig(args[0] + '-hist.png')

if __name__ == '__main__':
    sys.exit(main())
