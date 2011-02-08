#!/usr/bin/env python

import sys
import socket
import dpkt
from dpkt.pcap import Reader
from dpkt.ethernet import Ethernet
from optparse import OptionParser

def domainsandips(pcappath):
    domains = set([])
    ips = set([])

    pcap = Reader(file(pcappath, 'rb'))
    for _, data in pcap:
        eth = Ethernet(data)
        ip = eth.data
        trans = ip.data

        try:
            ips.add(socket.inet_ntoa(ip.src))
            ips.add(socket.inet_ntoa(ip.dst))

            if type(trans) == dpkt.udp.UDP and \
                    (trans.sport == 53 or trans.dport == 53):
                dns = dpkt.dns.DNS(ip.data.data)
                for query in dns.qd:
                    domains.add(query.name)
        except Exception as e:
            pass

    return (domains, ips)

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] pcap"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    # do stuff
    (domains, ips) = domainsandips(args[0])
    for domain in domains:
        print(domain)
    for ip in ips:
        print(ip)

if __name__ == '__main__':
    sys.exit(main())
