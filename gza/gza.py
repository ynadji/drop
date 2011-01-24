#!/usr/bin/env python

from scapy.all import *
import dns
import tcp
import dnsnever
from optparse import OptionParser

def playgame(packet):
    """playgame!"""
    dns.playgame(packet)

def startgame(gamename, i):
    if gamename == 'dns':
        dns.startgame(i)
    elif gamename == 'tcp':
        tcp.startgame(i)
    elif gamename == 'dnsnever':
        dnsnever.startgame(i)

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] game vmnum"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        return 2

    # do stuff
    startgame(args[0], int(args[1]))

if __name__ == '__main__':
    sys.exit(main())
