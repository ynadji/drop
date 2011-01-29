#!/usr/bin/env python
#
# DNS gameplay

from scapy.all import *
import sys,os,time
import nfqueue
import socket
from gzacommon import GZA

WHITELIST_DOMAINS = ["time.windows.com."]
seen_domains = {}
TRIES = 1

ADD = '-A'
DEL = '-D'
IPTABLES_COMMAND = \
        'iptables %s FORWARD -d 192.168.%d.0/24 -m udp -p udp -j NFQUEUE --queue-num %d'

class DNSGZA(GZA):
    def __init__(self, vmnum, opts):
        super(DNSGZA, self).__init__(vmnum, opts)

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

        # whitelist
        print("Domain name: %s" % dnsqr.qname)
        # increment count if seen
        if dnsqr.qname in self.gamestate:
            if self.gamestate[dnsqr.qname] == TRIES:
                print("Seen %d times, accept" % TRIES)
                return False
            else:
                self.gamestate[dnsqr.qname] += 1

        if dnsqr.qname in WHITELIST_DOMAINS:
            print("Domain %s whitelisted" % dnsqr.qname)
            return False
        else:
            print("Spoofing nxdomain")
            nx = self.nxdomain(packet)
            send(nx)

            # add to self.gamestate
            self.gamestate[dnsqr.qname] = 1

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
