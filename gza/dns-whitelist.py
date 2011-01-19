#!/usr/bin/env python
# 
# DNS gameplay
#
# whitelist including more than time.windows

from scapy.all import *
import sys,os,time
import nfqueue
import socket

# Set log level to benefit from Scapy warnings
import logging
logging.getLogger("scapy").setLevel(1)

# my logging
log = logging.getLogger("dnsw.py")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s - %(levelname)s: %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

WHITELIST_DOMAINS = ["time.windows.com.", 
"google.com.", "www.google.com.", "facebook.com.", "www.facebook.com.", "youtube.com.", "www.youtube.com.", "yahoo.com.", "www.yahoo.com.", "live.com.",
"www.live.com.", "baidu.com.", "www.baidu.com.", "wikipedia.org.", "www.wikipedia.org.", "blogger.com.", "www.blogger.com.", "msn.com.", "www.msn.com.",
"twitter.com.", "www.twitter.com.", "qq.com.", "www.qq.com.", "yahoo.co.jp.", "www.yahoo.co.jp.", "google.co.in.", "www.google.co.in.", "taobao.com.",
"www.taobao.com.", "amazon.com.", "www.amazon.com.", "sina.com.cn.", "www.sina.com.cn.", "google.de.", "www.google.de.", "google.com.hk.", "www.google.com.hk.",
"wordpress.com.", "www.wordpress.com.", "google.co.uk.", "www.google.co.uk.", "ebay.com.", "www.ebay.com.", "bing.com.", "www.bing.com.", "google.fr.",
"www.google.fr.", "microsoft.com.", "www.microsoft.com.", "yandex.ru.", "www.yandex.ru.", "linkedin.com.", "www.linkedin.com.", "163.com.", "www.163.com.",
"google.co.jp.", "www.google.co.jp.", "myspace.com.", "www.myspace.com.", "google.com.br.", "www.google.com.br.", "craigslist.org.", "www.craigslist.org.", "conduit.com.",
"www.conduit.com.", "fc2.com.", "www.fc2.com.", "flickr.com.", "www.flickr.com.", "mail.ru.", "www.mail.ru.", "google.it.", "www.google.it.",
"imdb.com.", "www.imdb.com.", "vkontakte.ru.", "www.vkontakte.ru.", "livejasmin.com.", "www.livejasmin.com.", "google.es.", "www.google.es.", "googleusercontent.com.",
"www.googleusercontent.com.", "mozilla.com.", "www.mozilla.com.", "soso.com.", "www.soso.com.", "sohu.com.", "www.sohu.com.", "rapidshare.com.", "www.rapidshare.com.",
"apple.com.", "www.apple.com.", "bbc.co.uk.", "www.bbc.co.uk.", "go.com.", "www.go.com.", "aol.com.", "www.aol.com.", "youku.com.",
"www.youku.com.", "ask.com.", "www.ask.com.", "doubleclick.com.", "www.doubleclick.com.", "google.com.mx.", "www.google.com.mx.", "xvideos.com.", "www.xvideos.com.",
"paypal.com.", "www.paypal.com.", "pornhub.com.", "www.pornhub.com.", "google.ru.", "www.google.ru.", "bp.blogspot.com.", "www.bp.blogspot.com.", "google.ca.",
"www.google.ca.", "adobe.com.", "www.adobe.com.", "cnn.com.", "www.cnn.com.", "orkut.com.br.", "www.orkut.com.br.", "mediafire.com.", "www.mediafire.com.",
"tudou.com.", "www.tudou.com.", "youporn.com.", "www.youporn.com.", "sogou.com.", "www.sogou.com.", "hotfile.com.", "www.hotfile.com.", "xhamster.com.",
"www.xhamster.com.", "4shared.com.", "www.4shared.com.", "about.com.", "www.about.com.", "photobucket.com.", "www.photobucket.com.", "orkut.com.", "www.orkut.com.",
"livejournal.com.", "www.livejournal.com.", "ameblo.jp.", "www.ameblo.jp.", "espn.go.com.", "www.espn.go.com.", "google.co.id.", "www.google.co.id.", "megaupload.com.",
"www.megaupload.com.", "cnet.com.", "www.cnet.com.", "ebay.de.", "www.ebay.de.", "hao123.com.", "www.hao123.com.", "imageshack.us.", "www.imageshack.us.",
"rakuten.co.jp.", "www.rakuten.co.jp.", "google.com.tr.", "www.google.com.tr.", "megavideo.com.", "www.megavideo.com.", "google.com.au.", "www.google.com.au.", "uol.com.br.",
"www.uol.com.br.", "google.cn.", "www.google.cn.", "livedoor.com.", "www.livedoor.com.", "orkut.co.in.", "www.orkut.co.in.", "thepiratebay.org.", "www.thepiratebay.org.",
"google.pl.", "www.google.pl.", "nytimes.com.", "www.nytimes.com.", "ifeng.com.", "www.ifeng.com.", "alibaba.com.", "www.alibaba.com.", "tube8.com.",
"www.tube8.com.", "ebay.co.uk.", "www.ebay.co.uk.", "tianya.cn.", "www.tianya.cn.", "godaddy.com.", "www.godaddy.com.", "google.com.sa.", "www.google.com.sa.",
"twitpic.com.", "www.twitpic.com."]

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
    log.debug("domain name: %s", dnsqr.qname)
    if dnsqr.qname in WHITELIST_DOMAINS:
        log.debug("domain %s whitelisted", dnsqr.qname)
        return False
    else:
        log.debug("spoofing nxdomain")
        nx = nxdomain(packet)
        send(nx)
        return True

def playgame(i, payload):
    """docstring for main"""
    data = payload.get_data()
    packet = IP(data)
    if packet.haslayer(DNS) and spoof(packet):
        log.debug("dns packet match found")
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
        print "usage: ./dns-whitelist.py QUEUENUM"
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
