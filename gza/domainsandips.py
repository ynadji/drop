#!/usr/bin/env python

import sys
import socket
import dpkt
from dpkt.pcap import Reader
from dpkt.ethernet import Ethernet
from optparse import OptionParser
from encodings.idna import ToASCII as asciify

def domainsandips(pcappath, allips=False):
    domains = set([])
    ips = set([])

    pcap = Reader(file(pcappath, 'rb'))
    for _, data in pcap:
        eth = Ethernet(data)
        ip = eth.data
        trans = ip.data

        try:
            if type(trans) == dpkt.tcp.TCP:
                ips.add(socket.inet_ntoa(ip.src))
                ips.add(socket.inet_ntoa(ip.dst))

            if type(trans) == dpkt.udp.UDP and \
                    (trans.sport == 53 or trans.dport == 53):
                dns = dpkt.dns.DNS(ip.data.data)
                for query in dns.qd:
                    # asciify is the standard for normalizing domains
                    # to ascii. Also we don't want any tab characters to
                    # fuck up our R script.
                    domains.add(asciify(query.name).replace('\t', ''))
                if allips:
                    for answer in dns.an:
                        try:
                            ips.add(socket.inet_ntoa(answer.rdata))
                        except socket.error as e:
                            pass
        except Exception as e:
            pass

    return (domains, ips)

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] pcap"
    parser = OptionParser(usage=usage)
    parser.add_option('-a', '--all-ips', default=False, action='store_true',
                      dest='allips')

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    # do stuff
    (domains, ips) = domainsandips(args[0], allips=options.allips)
    for domain in domains:
        print(domain)
    for ip in ips:
        print(ip)

if __name__ == '__main__':
    sys.exit(main())
