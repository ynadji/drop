#!/usr/bin/env python
#
# GHOSTFACE, CATCH THE BLAST OF A HYPE VERSE,
# MY GLOCK BURST LEAVE IN A HEARSE I DID WORSE
#
# Proposed label for RR: gray  prediction confidence: 0.870883065746
#

import sys
from optparse import OptionParser
import re
import fileinput
from collections import defaultdict
from itertools import product

sys.path.append('wulib')
from wulib import meanwithconfidence

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

    classes['both'] = classes['black'] + classes['gray']

    for klass, conf in product(['both', 'white'], [0.95, 0.99]):
        mean, interval = meanwithconfidence(classes[klass])
        print('%s mean: %f (%f%% confidence interval of +/- %f)' %
                (klass, mean, conf, interval))

if __name__ == '__main__':
    sys.exit(main())
