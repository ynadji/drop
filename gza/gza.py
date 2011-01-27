#!/usr/bin/env python

from scapy.all import *
import dns
import tcp
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
    usage = "usage: %prog [options] dns|tcp vmnum"
    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--drop-n', dest='dropn', default=-1, action='store',
            type='int',
            help='"Block" first n packets and accept rest (0 for all, -1 for ignore this rule) based on game type [default: %default]')
    parser.add_option('-t', '--take-n', dest='taken', default=-1, action='store',
            type='int',
            help='"Accept" first n packets and drop rest (0 for all, -1 for ignore this rule) based on game type [default: %default]')
    parser.add_option('-w', '--whitelist', dest='whitelist', default=False,
            action='store_true', help='Use whitelist')
    parser.add_option('--whitelist-path', dest='whitelistpath',
            default='top1000.csv', help='Whitelist to use [default: %default]')

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        return 2
    if args[0] != 'dns' and args[1] != 'tcp':
        parser.print_help()
    if options.taken >= 0 and options.dropn >= 0:
        parser.error('--take-n and --drop-n are mutually exclusive. Only use one.')

    # do stuff
    startgame(args[0], int(args[1]))

if __name__ == '__main__':
    sys.exit(main())
