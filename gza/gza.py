#!/usr/bin/env python

import sys
from scapy.all import *
from gzadns import DNSGZA
from gzatcp import TCPGZA
from optparse import OptionParser

gameargs = {'dns1': ['--drop-n', '1', 'dns'],
            'dnsw': ['--dropall', '--whitelist', 'dns'],
            'tcpw': ['--dropall', '--whitelist', 'tcp'],
            'tcp1': ['--take-n', '1', 'tcp'],
            'tcp2': ['--take-n', '2', 'tcp'],
            'tcp3': ['--take-n', '3', 'tcp']
            }

def startgame(game, vmnum):
    if game == 'none':
        return
    args = gameargs[game]
    args.append(str(vmnum))
    main(arglist=args)

def main(arglist=None):
    """main function for standalone usage"""
    usage = "usage: %prog [options] dns|tcp vmnum"
    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--drop-n', dest='dropn', default=-1, action='store',
            type='int',
            help='"Block" first n packets and accept rest (-1 for ignore this rule) based on game type [default: %default]')
    parser.add_option('-t', '--take-n', dest='taken', default=-1, action='store',
            type='int',
            help='"Accept" first n packets and drop rest (-1 for ignore this rule) based on game type [default: %default]')
    parser.add_option('-a', '--dropall', dest='dropall', default=False,
            action='store_true', help='Drop all packets')
    parser.add_option('-w', '--whitelist', dest='whitelist', default=False,
            action='store_true', help='Use whitelist')
    parser.add_option('--whitelist-path', dest='whitelistpath',
            default='gza/top1000.csv', help='Whitelist to use [default: %default]')
    parser.add_option('-i', '--iptables-rule', dest='iptables',
            action='store_true',
            default=False, help='Print out sample iptables rule')

    if arglist is None:
        (options, args) = parser.parse_args()
    else:
        (options, args) = parser.parse_args(arglist)

    if len(args) != 2:
        parser.print_help()
        return 2
    if args[0] != 'dns' and args[0] != 'tcp':
        parser.print_help()
        return 2
    if options.iptables:
        if args[0] == 'dns':
            args[0] = 'udp'
        for action in ['-A', '-D']:
            print('iptables %s FORWARD -d 192.168.%s.0/24 -m %s -p %s -j NFQUEUE --queue-num %s'
                    % (action, args[1], args[0], args[0], args[1]))
        sys.exit(0)
    if options.taken >= 0 and options.dropn >= 0:
        parser.error('--take-n and --drop-n are mutually exclusive. Only use one.')

    # do stuff
    print('Running %s on tap%s with options: %s' % (args[0], args[1], options))
    if args[0] == 'dns':
        g = DNSGZA(int(args[1]), options)
    elif args[0] == 'tcp':
        g = TCPGZA(int(args[1]), options)
    else:
        return 0
    g.startgame()

if __name__ == '__main__':
    sys.exit(main())
