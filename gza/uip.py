#!/usr/bin/env python
# 
# Extract unique domains from a PCAP dump.

import re
import sys
import logging
from optparse import OptionParser
logging.disable(logging.WARNING)

from scapy.all import *

def layer_to_list(pkt):
  """Get list of layers below a layer."""
  i = 0
  layers = []
  l = pkt.getlayer(i)
  while l:
      layers.append(l)
      i += 1
      l = pkt.getlayer(i)

  return layers

def private_ip(ip):
  """Returns true if IP is private as specified by RFC 1918/4193"""
  return ip.startswith("192.168.") or ip.startswith("10.") or re.match("172\.([1-2][0-9]|3[01])", ip) \
          or ip == "0.0.0.0" or ip == "255.255.255.255"

def unique_ips(pcap, parse_all):
  """Extract and print unique IPs queried in file 'pcap'."""
  pkts = rdpcap(pcap)

  ip_pkts = pkts.filter(lambda x: x.haslayer(IP))
  unique_ips = set()

  for pkt in ip_pkts:
      if not private_ip(pkt[IP].src):
          unique_ips.add(pkt[IP].src)
      if not private_ip(pkt[IP].dst):
          unique_ips.add(pkt[IP].dst)

  # get extra, unused IPs from DNS
  if parse_all:
      dnsrr = pkts.filter(lambda x: x.haslayer(DNSRR))

      for pkt in dnsrr:
          records = layer_to_list(pkt[DNSRR])
          for rr in records:
              if re.match("[\d\.]+", rr.rdata):
                  unique_ips.add(rr.rdata)

  for ip in sorted(unique_ips):
      print ip

if __name__ == '__main__':
    usage = "usage: %prog [options] pcap-file"
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--all", action="store_true", dest="all", default=False, 
            help="Display ALL IPs (i.e., IPs retrieved but never used, like IPs returned by a DNS query)")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)
    else:
        unique_ips(args[0], options.all)
