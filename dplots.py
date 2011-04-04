#!/usr/bin/env python
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import sys
import re
from optparse import OptionParser
from dateutil.parser import parse
import datetime

sys.path.append('wulib')
from wulib import chunks

countregex = re.compile('(\d+) / \d+')

def extract(line):
    return int(countregex.search(line).group(1))

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] deltas firstday"
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--show', default=False, action='store_true',
            help='Show figure instead of save it to PNG [default: %default]')

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        return 2

    # do stuff
    day = parse(args[1])
    days = []
    tomorrow = datetime.timedelta(1)
    resperday = list(chunks(file(args[0]).read().strip().split('\n'), 8))
    #for dnsblack, dnsdecom, dnsincamp, dnsnever, ipblack, ipdecom, ipincamp, ipnever in resperday:
    for _ in resperday:
        days.append(day)
        day += tomorrow

    firstday = days[0]
    lastday = days[-1]
    dnsblack, dnsdecom, dnsincamp, dnsnever, ipblack, ipdecom, ipincamp, ipnever = zip(*resperday)

    fig = plt.figure()
    ax = fig.add_subplot(223)
    plt.ylabel('Frequency')
    ax.plot(days, map(extract, dnsblack), '-r+', label='Blacklisted')
    ax.plot(days, map(extract, dnsdecom), '-bx', label='Decommissioned')
    ax.plot(days, map(extract, dnsincamp), '-g*', label='In Campaign')
    ax = fig.add_subplot(221)
    plt.title('DNS Games')
    plt.ylabel('Frequency')
    ax.plot(days, map(extract, dnsblack), '-r+', label='Blacklisted')
    ax.plot(days, map(extract, dnsdecom), '-bx', label='Decommissioned')
    ax.plot(days, map(extract, dnsincamp), '-g*', label='In Campaign')
    ax.plot(days, map(extract, dnsnever), '-s', label='Never Blacklisted')
    plt.legend(loc=2)

    ax = fig.add_subplot(224)
    ax.plot(days, map(extract, ipblack), '-r+')
    ax.plot(days, map(extract, ipdecom), '-bx')
    ax.plot(days, map(extract, ipincamp), '-g*')
    ax = fig.add_subplot(222)
    plt.title('TCP Games')
    ax.plot(days, map(extract, ipblack), '-r+')
    ax.plot(days, map(extract, ipdecom), '-bx')
    ax.plot(days, map(extract, ipincamp), '-g*')
    ax.plot(days, map(extract, ipnever), '-s')

    fig.autofmt_xdate()

    plt.show()

if __name__ == '__main__':
    sys.exit(main())
