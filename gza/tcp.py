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
        remove_computed_fields(p)

        return p

    # spoof function
    def spoof(self, packet):
        """If we have a DNS response, change it to NXDomain."""
        src_ip = packet[IP].src

        # whitelist
        print("ip address: %s" % src_ip)
        if src_ip in seen_ips:
            print("ip %s already seen, let it through" % src_ip)
            return False

        for ip in WHITELIST_IPS:
            if src_ip.startswith(ip):
                print("ip %s whitelisted" % ip)
                return False

        print("spoofing tcp rst, will accept next time")
        p = self.rst(packet)
        send(p)

        # we will no longer tcp rst this IP
        seen_ips.append(src_ip)

        return True

    def playgame(self, i, payload):
        """docstring for main"""
        data = payload.get_data()
        packet = IP(data)
        if self.spoof(packet):
            print("tcp reset sent")
            payload.set_verdict(nfqueue.NF_DROP)
            return
        else:
            print("no match")
            payload.set_verdict(nfqueue.NF_ACCEPT)
            return
