#!/usr/bin/env python

# kvm.py -- Launches a batch of KVM virtual machines to
# analyze the binaries in maldir/. Networking and even
# distribution of malware binaries is handled automatically.
#
# This script MUST be run as root.
#
# Author: Yacin Nadji <yacin@gatech.edu>
#

import sys
import os
import shutil
import glob
import time
from subprocess import Popen
from optparse import OptionParser

DHCPD_CONF_PATH = 'dhcpd.conf'

def dhcpd_start(opts):
    conf = ['ddns-update-style none;', 'default-lease-time 600;', 'max-lease-time 7200;',
            'log-facility local7;']
    entry = """subnet 192.168.%d.0 netmask 255.255.255.0 {
    range 192.168.%d.41 192.168.%d.254;
    option domain-name-servers 192.168.%d.1;
    option routers 192.168.%d.1;
}
"""
    for i in range(1, opts.numvms + 1):
        conf.append(entry % (i, i, i, i, i))

    with open(DHCPD_CONF_PATH, 'w') as conffile:
        conffile.write('\n'.join(conf))

    os.system('dhcpd -cf %s' % DHCPD_CONF_PATH)

def dhcpd_stop():
    os.unlink(DHCPD_CONF_PATH)
    os.system('pkill dhcpd')

def kvm(opts, num):
    args = ['kvm', '-usbdevice', 'tablet', '-snapshot',
            '-hda', '%s' % opts.vmimage,'-vnc', ':%d' % num,
            '-net', 'nic,vlan=%d' % num, '-net',
            'tap,vlan=%d,ifname=tap%d,script=no,downscript=no' % (num, num)]
    return Popen(args)

def setup(opts):
    installstage2(opts)
    # loop
    for i in range(1, opts.numvms + 1):
        os.system('tunctl -u root -t tap%d' % i)
        os.system('ifconfig tap%d 192.168.%d.1 netmask 255.255.255.0 up' % (i, i))
        os.mkdir(os.path.join(opts.webroot, str(i)))

    time.sleep(10)
    os.system('sysctl -w net.ipv4.ip_forward=1')
    os.system('iptables-restore < %s' % opts.iptables)
    dhcpd_start(opts)

def teardown(opts):
    dhcpd_stop()
    # loop
    for i in range(1, opts.numvms + 1):
        os.system('ifconfig tap%d down' % i)
        os.system('tunctl -d tap%d' % i)
        shutil.rmtree(os.path.join(opts.webroot, str(i)))

    os.system('sysctl -w net.ipv4.ip_forward=0')
    os.system('iptables --flush')
    os.system('iptables -t nat --flush')

def installsample(opts, malpath, i):
    shutil.copy(malpath, os.path.join(opts.webroot, str(i), 'sample.exe'))

def installstage2(opts):
    try:
        shutil.copy(opts.stage2, os.path.join(opts.webroot, 'stage2.py'))
    except shutil.Error: # This occurs if the files are the same
        pass

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] maldir"
    parser = OptionParser(usage=usage)
    parser.add_option("-n", "--num-vms", dest="numvms", default=4,
            type="int", help="Number of VMs to use [default: %default]")
    parser.add_option("-t", "--runtime", dest="runtime", default=300,
            type="int", help="Running time per VM (seconds) [default: %default]")
    parser.add_option("-w", "--webroot", dest="webroot", default="/var/www",
            help="Webroot on host/gateway [default: %default]")
    parser.add_option("-2", "--stage2", dest="stage2", default="win/stage2-dropper.py",
            help="Stage 2 script [default: %default]")
    parser.add_option("-i", "--iptables", dest="iptables", default="iptables",
            help="IPtables script to perform NAT/abuse prevention [default: %default]")
    parser.add_option("-v", "--vm-image", dest="vmimage",
            default="/home/yacin/images/fresh_installs/winxp.qcow2",
            help="VM image path [default: %default]")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    if not os.geteuid() == 0:
        sys.stderr.write('Only root can run this script\n')
        sys.exit(1)

    try:
        # Run them VMs!
        setup(options)
        time.sleep(5)

        kvms = []
        malware = glob.glob(os.path.join(args[0], "*"))
        # Runnin em
        while malware:
            for i in range(1, options.numvms + 1):
                # RUN DAT SHIT
                try:
                    sample = malware.pop(0)
                    installsample(options, sample, i)
                    print('Running: %s in VM #%d...' % (sample, i))
                    kvms.append(kvm(options, i))
                except:
                    print('Malware exhausted, waiting for running KVMs to terminate')
                    pass

            print('Sleeping for %d seconds...' % options.runtime)
            time.sleep(options.runtime)
            print('Terminating KVMs...')
            for proc in kvms:
                proc.terminate()
            del kvms[:]
            print('KVMs terminated')
            time.sleep(5)
    except KeyboardInterrupt:
        sys.stderr.write('User termination...')
        for proc in kvms:
            proc.terminate()
    except Exception as e:
        sys.stderr.write(str(e))
    finally:
        teardown(options)

if __name__ == '__main__':
    sys.exit(main())
