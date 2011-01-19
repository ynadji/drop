#/usr/bin/python
import os,sys,time
import nfqueue
from scapy.all import *
import socket

data = None


class MyQueue:
	def __init__(self):
		self.q = nfqueue.queue()

	def remove_computed_fields(self, pkt):
            # del(pkt[DNS].ns)
            # del(pkt[DNS].nscount)
            # del(pkt[DNS].ar)
            # del(pkt[DNS].arcount)
            del(pkt[IP].chksum)
            del(pkt[UDP].chksum)
            del(pkt[IP].len)
            del(pkt[UDP].len)

	def one_rr(self, pkt):
            self.remove_non_answers(pkt)
            if pkt[DNS].ancount == 1:
                return
            else:
                one_rr = pkt[DNSRR].lastlayer().copy()
                del(pkt[DNS].an)
                pkt[DNS].an = one_rr
                pkt[DNS].ancount = 1

	def process(self, i, payload):
            print "other1.py, TCP shit, accept!"
            payload.set_verdict(nfqueue.NF_ACCEPT)
            return

        def main(self):
            self.q.open()
            self.q.set_callback(self.process)
            self.q.fast_open(1, socket.AF_INET)
            #self.q.create_queue(1)
            try:
                self.q.try_run()
            except KeyboardInterrupt:
                print "Exiting..."
                self.q.unbind(socket.AF_INET)
                self.q.close()
                sys.exit(1)

MyQueue().main()
