#!/usr/bin/env python
#
# DNS gameplay

from scapy.all import *
import sys,os,time
import nfqueue
import socket
from gzacommon import GZA

class DNSGZA(GZA):
    def __init__(self, vmnum, opts):
        super(DNSGZA, self).__init__(vmnum, opts)
        if self.game == 'taken':
            sys.stderr.write('--take-n not implemented in %s, terminating\n'
                    % self.__class__.__name__)
            sys.exit(2)

    def reset(self, signum, frame):
        if self.game == 'dropn':
            sys.stderr.write('Reset self.count in %s\n' % self.__class__.__name__)
            self.count = self.opts.dropn
        super(DNSGZA, self).reset(signum, frame)

    def remove_computed_fields(self, pkt):
        """Remove UDP computed fields"""
        del(pkt[IP].chksum)
        del(pkt[UDP].chksum)
        del(pkt[IP].len)
        del(pkt[UDP].len)

    def nxdomain(self, qpkt):
        """Returns NXDomain version of qpkt"""
        nx = qpkt.copy()
        nx[DNS].an = None
        nx[DNS].ns = None
        nx[DNS].ar = None
        nx[DNS].ancount = 0
        nx[DNS].nscount = 0
        nx[DNS].arcount = 0
        nx[DNS].rcode = "name-error"
        self.remove_computed_fields(nx)

        return nx

    # spoof function
    def spoof(self, packet):
        """If we have a DNS response, change it to NXDomain."""
        dns = packet[DNS]
        dnsqr = packet[DNSQR]
        print("Domain name: %s" % dnsqr.qname)

        # Increment for games that rely on a count of domains
        self.gamestate[dnsqr.qname] += 1

        # Handle dropall game
        if self.game == 'dropall':
            if self.opts.whitelist and self.whitelisted(dnsqr.qname):
                return False
            else:
                print("Spoofing nxdomain for %s" % dnsqr.qname)
                nx = self.nxdomain(packet)
                send(nx)
                return True
        elif self.game == 'dropn':
            # Game over, accept all from now on
            if self.opts.dropn == 0:
                self.spoof = lambda x, y: False
                return False
            else:
                if self.whitelist and self.whitelisted(dnsqr.qname):
                    print('%s is whitelisted' % dnsqr.qname)
                    return False
                self.opts.dropn -= 1
                print("Spoofing nxdomain for %s" % dnsqr.qname)
                nx = self.nxdomain(packet)
                send(nx)
                return True

    def playgame(self, i, payload):
        data = payload.get_data()
        packet = IP(data)
        if packet.haslayer(DNS) and self.spoof(packet):
            payload.set_verdict(nfqueue.NF_DROP)
            return
        else:
            payload.set_verdict(nfqueue.NF_ACCEPT)
            return
