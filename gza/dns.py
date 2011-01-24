#!/usr/bin/env python
#
# DNS gameplay

from scapy.all import *
import sys,os,time
import nfqueue
import socket

WHITELIST_DOMAINS = ["time.windows.com."]
seen_domains = {}
TRIES = 1

ADD = '-A'
DEL = '-D'
IPTABLES_COMMAND = \
        'iptables %s FORWARD -d 192.168.%d.0/24 -m udp -p udp -j NFQUEUE --queue-num %d'

def remove_computed_fields(pkt):
    del(pkt[IP].chksum)
    del(pkt[UDP].chksum)
    del(pkt[IP].len)
    del(pkt[UDP].len)

def nxdomain(qpkt):
    """Returns NXDomain version of qpkt"""
    nx = qpkt.copy()
    nx[DNS].an = None
    nx[DNS].ns = None
    nx[DNS].ar = None
    nx[DNS].ancount = 0
    nx[DNS].nscount = 0
    nx[DNS].arcount = 0
    nx[DNS].rcode = "name-error"
    remove_computed_fields(nx)

    return nx

# spoof function
def spoof(packet):
    """If we have a DNS response, change it to NXDomain."""
    dns = packet[DNS]
    dnsqr = packet[DNSQR]

    # whitelist
    print("Domain name: %s" % dnsqr.qname)
    # increment count if seen
    if dnsqr.qname in seen_domains:
        if seen_domains[dnsqr.qname] == TRIES:
            print("Seen %d times, accept" % TRIES)
            return False
        else:
            seen_domains[dnsqr.qname] += 1

    if dnsqr.qname in WHITELIST_DOMAINS:
        print("Domain %s whitelisted" % dnsqr.qname)
        return False
    else:
        print("Spoofing nxdomain")
        nx = nxdomain(packet)
        send(nx)

        # add to seen_domains
        seen_domains[dnsqr.qname] = 1

        return True

def playgame(i, payload):
    """docstring for main"""
    data = payload.get_data()
    packet = IP(data)
    if packet.haslayer(DNS) and spoof(packet):
        payload.set_verdict(nfqueue.NF_DROP)
        return
    else:
        payload.set_verdict(nfqueue.NF_ACCEPT)
        return

def startgame(vmnum):
    os.system(IPTABLES_COMMAND % (ADD, vmnum, vmnum))
    goodtogo = False
    while not goodtogo:
        try:
            q = nfqueue.queue()
            q.open()
            q.set_callback(playgame)
            q.fast_open(vmnum, socket.AF_INET)
            goodtogo = True
        except RuntimeError:
            sys.stderr.write('fast_open on %d for game %s failed, trying again\n' % (vmnum, 'dns'))
            q.unbind(socket.AF_INET)
            os.system(IPTABLES_COMMAND % (DEL, vmnum, vmnum))
            time.sleep(7)
    try:
        q.try_run()
    except KeyboardInterrupt:
        stopgame(vmnum, q)

def stopgame(vmnum, q):
    os.system(IPTABLES_COMMAND % (DEL, vmnum, vmnum))
    print("Exiting...")
    q.unbind(socket.AF_INET)
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: ./dns.py QUEUENUM"
        sys.exit(1)

    startgame(int(sys.argv[1]))
