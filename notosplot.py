#!/usr/bin/env python
#
# GHOSTFACE, CATCH THE BLAST OF A HYPE VERSE,
# MY GLOCK BURST LEAVE IN A HEARSE I DID WORSE
#
# Proposed label for RR: gray  prediction confidence: 0.870883065746
#

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import sys
from optparse import OptionParser
import re
import fileinput
from collections import defaultdict

r = re.compile('.*?Proposed label for RR: (\w+)  prediction confidence: ([\d.]+) ')

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] notos.output"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    classes = defaultdict(list)

    # do stuff
    for line in fileinput.input():
        match = r.search(line)
        if match:
            classes[match.group(1)].append(float(match.group(2)))

    n, bins, patches = plt.hist(classes['white'], bins=1000, normed=True, histtype='stepfilled')
    plt.show()

if __name__ == '__main__':
    sys.exit(main())
