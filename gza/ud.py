#!/usr/bin/env python
#
# Extract unique domains from a PCAP dump.

import sys
import logging
logging.disable(logging.WARNING)

from scapy.all import *

def unique_domains(pcap):
  """Extract and print unique domains queried in file 'pcap'."""
  pkts = rdpcap(pcap)
  dns = pkts.filter(lambda x: x.haslayer(DNSQR))
  ud = set([p[DNSQR].qname for p in dns])

  return ud

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: ./ud pcap-file"
        sys.exit(1)
    else:
        ud = unique_domains(sys.argv[1])
        for domain in sorted(ud):
            print domain
