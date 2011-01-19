#!/usr/bin/env python
# 
# DNS gameplay

from scapy.all import *
import sys,os,time
import nfqueue
import socket

# Set log level to benefit from Scapy warnings
import logging
logging.getLogger("scapy").setLevel(1)

# my logging
log = logging.getLogger("tcp.py")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s - %(levelname)s: %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

# time.windows, damballa, damballa, local
WHITELIST_IPS = ["207.46.232.", "172.22.0.", "172.22.10.", "192.168.", "0.0.0.0", "255.255.255.255"]
seen_ips = []

def remove_computed_fields(pkt):
    del(pkt[IP].chksum)
    del(pkt[TCP].chksum)
    del(pkt[IP].len)
    #del(pkt[TCP].len)

def rst(qpkt):
    """Returns TCP RST version of qpkt"""
    p = qpkt.copy()
    # ACK/RST
    p[TCP].flags = 0x16
    remove_computed_fields(p)

    return p

# spoof function
def spoof(packet):
    """If we have a DNS response, change it to NXDomain."""
    src_ip = packet[IP].src

    # whitelist
    log.debug("ip address: %s", src_ip)
    if src_ip in seen_ips:
        log.debug("ip %s already seen, let it through", src_ip)
        return False

    for ip in WHITELIST_IPS:
        if src_ip.startswith(ip):
            log.debug("ip %s whitelisted", ip)
            return False

    log.debug("spoofing tcp rst, will accept next time")
    p = rst(packet)
    send(p)

    # we will no longer tcp rst this IP
    seen_ips.append(src_ip)

    return True

def playgame(i, payload):
    """docstring for main"""
    data = payload.get_data()
    packet = IP(data)
    if spoof(packet):
        log.debug("tcp reset sent")
        payload.set_verdict(nfqueue.NF_DROP)
        return
    else:
        log.debug("no match")
        payload.set_verdict(nfqueue.NF_ACCEPT)
        return

def cleanup(q):
    q.unbind(socket.AF_INET)
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: ./tcp.py QUEUENUM"
        sys.exit(1)

    qnum = int(sys.argv[1])

    q = nfqueue.queue()
    q.open()
    q.set_callback(playgame)
    q.fast_open(qnum, socket.AF_INET)
    try:
        q.try_run()
    except KeyboardInterrupt:
        print "Exiting..."
        q.unbind(socket.AF_INET)
        sys.exit(1)
