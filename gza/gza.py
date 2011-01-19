#!/usr/bin/env python

from scapy.all import *
import dns
import tcp

def playgame(packet):
    """playgame!"""
    dns.playgame(packet)

if __name__ == '__main__':
    # first 10 dns packets, both queries/responses
    sniff(prn=playgame, filter="udp and port 53", count=20)
