#!/usr/bin/env python
#
# DNS gameplay

from scapy.all import *
import sys,os,time
import nfqueue
import socket
from gzacommon import GZA

# time.windows, damballa, damballa, local
WHITELIST_IPS = ["207.46.232.", "172.22.0.", "172.22.10.", "192.168.", "0.0.0.0", "255.255.255.255"]
seen_ips = []

class TCPGZA(GZA):
    def __init__(self, vmnum, opts):
        super(TCPGZA, self).__init__(vmnum, opts)
        if self.game == 'dropn':
            sys.stderr.write('--drop-n not implemented in %s, terminating\n'
                    % self.__class__.__name__)
            sys.exit(2)
        elif self.game == 'taken':
            self.count = self.opts.taken

    def remove_computed_fields(self, pkt):
        del(pkt[IP].chksum)
        del(pkt[TCP].chksum)
        del(pkt[IP].len)
        #del(pkt[TCP].len)

    def rst(self, qpkt):
        """Returns TCP RST version of qpkt"""
        p = qpkt.copy()
        # ACK/RST
        p[TCP].flags = 0x16
        self.remove_computed_fields(p)

        return p

    def reset(self, signum, frame):
        if self.game == 'taken':
            sys.stderr.write('Reset self.count in %s\n' % self.__class__.__name__)
            self.count = self.opts.taken
        super(TCPGZA, self).reset(signum, frame)

    def forge(self, packet):
        print('TCP RST for %s' % packet[IP].src)
        p = self.rst(packet)
        send(p)
        return True

    # spoof function
    def spoof(self, packet):
        """Spoof TCP streams with TCP RST"""
        src_ip = packet[IP].src
        print("IP address: %s" % src_ip)

        # IP for time.windows.com. See gzadns.py to see why this requires its
        # own separate "whitelist".
        if src_ip == '202.89.231.60':
            return False

        if self.opts.whitelist and self.whitelistedip(src_ip):
            print('%s is whitelisted' % src_ip)
            return False

        if self.game == 'dropall':
            return self.forge(packet)
        elif self.game == 'taken':
            # Game over, reject all.
            if self.gamestate[src_ip] == 'whitelisted':
                print("%s was a --take-n packet, accepting" % src_ip)
                return False
            elif self.count == 0:
                return self.forge(packet)
            else:
                self.count -= 1
                self.gamestate[src_ip] = 'whitelisted'
                print('--take-n, let the packet through. %d more free packets left!'
                        % self.count)
                return False

        print('Fell through game ifelif chain, accepting')
        return True

    def playgame(self, i, payload):
        """docstring for main"""
        data = payload.get_data()
        packet = IP(data)
        if self.spoof(packet):
            payload.set_verdict(nfqueue.NF_DROP)
            return
        else:
            payload.set_verdict(nfqueue.NF_ACCEPT)
            return
