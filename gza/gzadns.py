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
        if self.game == 'dropn':
            sys.stderr.write('--drop-n not implemented in %s, terminating\n'
                    % self.__class__.__name__)
            sys.exit(2)
        elif self.game == 'taken':
            self.count = self.opts.taken

    def reset(self, signum, frame):
        if self.game == 'taken':
            sys.stderr.write('Reset self.count in %s\n' % self.__class__.__name__)
            self.count = self.opts.taken
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

        return Ether(dst=self.mac)/nx

    def forge(self, packet):
        print('NXDomain for %s on %s' % (packet[DNSQR].qname, self.iface))
        p = self.nxdomain(packet)
        sendp(p, iface=self.iface)
        return True

    # spoof function
    def spoof(self, packet):
        """If we have a DNS response, change it to NXDomain."""
        dns = packet[DNS]
        dnsqr = packet[DNSQR]
        print("Domain name: %s" % dnsqr.qname)

        # We ALWAYS want to ignore this. Consider the game of accept the first
        # DNS request and spoof the rest. We are trying to attack malware
        # that's first DNS request is a rest of network connectivity.
        # It's unlikely to be the Windows NTP server.
        # Furthermore, if we disable the time lookup we could introduce addtnl
        # problems due to malware noticing a clock discrepancy. To be safe,
        # this should be a hardcoded case.
        if dnsqr.qname == 'time.windows.com.':
            return False

        if self.opts.whitelist and self.whitelisted(dnsqr.qname):
            print('%s is whitelisted' % dnsqr.qname)
            return False
        # Handle dropall game
        if self.game == 'dropall':
            return self.forge(packet)
        elif self.game == 'taken':
            if self.gamestate[dnsqr.qname] == 'whitelisted':
                print("%s was a --take-n packet, accepting" % dnsqr.qname)
                return False
            # Game over, reject all from now on
            elif self.count == 0:
                return self.forge(packet)
            else:
                self.count -= 1
                self.gamestate[dnsqr.qname] = 'whitelisted'
                print('--take-n, let the packet through. %d more free packets left!'
                        % self.count)
                return False

        print('Fell through game ifelif chain, do not spoof')
        return False

    def playgame(self, i, payload):
        data = payload.get_data()
        packet = IP(data)
        if packet.haslayer(DNS) and self.spoof(packet):
            payload.set_verdict(nfqueue.NF_DROP)
            return
        else:
            payload.set_verdict(nfqueue.NF_ACCEPT)
            return
