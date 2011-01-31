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
        elif self.game == 'dropn':
            self.count = self.opts.dropn

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

        # We ALWAYS want to ignore this. Consider the game of drop the first
        # DNS request and let the rest through. We are trying to attack malware
        # that's first DNS request is a C&C lookup. It'll never be windows NTP.
        # Furthermore, if we disable the time lookup we could introduce addtnl
        # problems due to malware noticing a clock discrepancy. To be safe,
        # this should be a hardcoded case.
        if dnsqr.qname == 'time.windows.com.':
            return False

        # Increment for games that rely on a count of domains
        self.gamestate[dnsqr.qname] += 1

        if self.opts.whitelist and self.whitelisted(dnsqr.qname):
            print('%s is whitelisted' % dnsqr.qname)
            return False
        # Handle dropall game
        if self.game == 'dropall':
            print("Spoofing nxdomain for %s" % dnsqr.qname)
            nx = self.nxdomain(packet)
            send(nx)
            return True
        elif self.game == 'dropn':
            if self.gamestate['dropn'] == dnsqr.qname:
                print("%s was a --drop-n packet, dropping" % dnsqr.qname)
                nx = self.nxdomain(packet)
                send(nx)
                return True
            # Game over, accept all from now on
            elif self.count == 0:
                print('--dropn game over!')
                return False
            else:
                self.count -= 1
                print("Spoofing nxdomain for %s" % dnsqr.qname)
                self.gamestate['dropn'] = dnsqr.qname
                nx = self.nxdomain(packet)
                send(nx)
                return True

        print('Fell through game ifelif chain, accepting')
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
