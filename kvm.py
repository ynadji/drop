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
from signal import SIGINT, SIGUSR1
from subprocess import Popen
from optparse import OptionParser

sys.path.append('wulib')
from wulib import chunks

DHCPD_CONF_PATH = 'dhcpd.conf'

def dhcpd_start(opts):
    conf = ['ddns-update-style none;', 'default-lease-time 600;', 'max-lease-time 7200;',
            'log-facility local7;']
    entry = """subnet 192.168.%d.0 netmask 255.255.255.0 {
    range 192.168.%d.41 192.168.%d.254;
    option domain-name-servers %s;
    option routers 192.168.%d.1;
}
"""
    for i in range(1, opts.numvms + 1):
        conf.append(entry % (i, i, i, opts.dns, i))

    with open(DHCPD_CONF_PATH, 'w') as conffile:
        conffile.write('\n'.join(conf))

    os.system('dhcpd -cf %s' % DHCPD_CONF_PATH)

def dhcpd_stop():
    try:
        os.unlink(DHCPD_CONF_PATH)
    except:
        pass
    os.system('pkill dhcpd')

def kvmmakeargs(opts, num, name):
    return ['kvm', '-usbdevice', 'tablet', '-snapshot',
            '-hda', '%s' % opts.vmimage,'-vnc', ':%d' % num,
            '-net', 'nic,vlan=%d,macaddr=ca:fe:de:ad:be:ef' % num, '-net',
            'dump,vlan=%d,file=%s/%s.pcap' % (num, opts.tcpdump, name),
            '-net', 'tap,vlan=%d,ifname=tap%d,script=no,downscript=no' %
            (num, num)]

def kvm(opts, num, name):
    args = kvmmakeargs(opts, num, name)
    return Popen(args)

def kvmcall(opts, num, name):
    args = kvmmakeargs(opts, num, name)
    args.insert(0, 'sudo')
    return ' '.join(args)

def nfqueue_rule(i, games):
    game = games[(i - 1) % len(games)]
    if game == 'none':
        return
    elif game.startswith('dns'):
        transporttype = 'udp'
    elif game.startswith('tcp'):
        transporttype = 'tcp'
    else:
        sys.stderr.write('Unknown nfqueue rule for game %s\n' % game)
        return

    os.system('iptables -A FORWARD -d 192.168.%d.0/24 -m %s -p %s -j LOG'
                    % (i, transporttype, transporttype))
    os.system('iptables -A FORWARD -d 192.168.%d.0/24 -m %s -p %s -j NFQUEUE --queue-num %d'
                    % (i, transporttype, transporttype, i))

def setup(opts):
    installstage2(opts)
    games = opts.games.split(',')
    # loop
    for i in range(1, opts.numvms + 1):
        os.system('tunctl -u root -t tap%d' % i)
        os.system('ifconfig tap%d 192.168.%d.1 netmask 255.255.255.0 up' % (i, i))
        try:
            sampledir = os.path.join(opts.webroot, str(i))
            os.mkdir(sampledir)
        except OSError:
            shutil.rmtree(sampledir)
            os.mkdir(sampledir)

    time.sleep(10)
    os.system('sysctl -w net.ipv4.ip_forward=1')
    os.system('iptables-restore < %s' % opts.iptables)
    for i in range(1, opts.numvms + 1):
        nfqueue_rule(i, games)
    dhcpd_start(opts)

def teardown(opts):
    dhcpd_stop()
    # loop
    for i in range(1, opts.numvms + 1):
        os.system('ifconfig tap%d down' % i)
        os.system('tunctl -d tap%d' % i)
        try:
            shutil.rmtree(os.path.join(opts.webroot, str(i)))
        except:
            pass

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

def pcaporganize(opts):
    rundir = os.path.join(opts.tcpdump, time.strftime('%Y%m%d-%H:%M:%S'))
    os.mkdir(rundir)
    pcaps = glob.glob(os.path.join(opts.tcpdump, '*.pcap'))
    for pcap in pcaps:
        shutil.move(pcap, rundir)

def rungames(vmlabels, games, gamelog, startgame):
    gamepids = []
    for vmgroup in chunks(vmlabels, len(games)):
        for game in games:
            # Can't terminate threads in python, so we'll fork the
            # infinite loop in startgame and send/handle SIGINT.
            vm = vmgroup.pop(0)
            if game == 'none':
                continue
            pid = os.fork()
            if pid == 0:
                #sys.stdout = gamelog
                startgame(game, vm)
                sys.exit(0)

            gamepids.append(pid)

    return gamepids

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] maldir"
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--games", dest="games", default="none",
            help="Games to play (comma separated list of: none,dns,dns5)")
    parser.add_option("-c", "--cleanup", dest="cleanup", default=False,
            action="store_true", help="Perform teardown operation")
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
    parser.add_option("-d", "--tcpdump-dir", dest="tcpdump", default="tcpdump",
            help="Directory for tcpdump pcaps [default: %default]")
    parser.add_option("--dns", dest="dns", default="8.8.8.8",
            help="DNS resolver to use [default: %default]")
    parser.add_option("-v", "--vm-image", dest="vmimage",
            default="/home/yacin/images/fresh_installs/winxp.qcow2",
            help="VM image path [default: %default]")
    parser.add_option("-l", "--game-log", dest="gamelog", default="game.log",
            help="Logfile for gameplay debug output [default: %default]")
    parser.add_option("--whitelistpath", dest="whitelistpath",
            default="/home/yacin/drop/gza/top1000.csv",
            help="Whitelist file to use [default: %default]")
    parser.add_option("-k", "--sample-kvm-cmd", dest="kvmcmd", default=False,
            action="store_true",
            help="Output a KVM call based on the other options (to debug)")

    (options, args) = parser.parse_args()

    if not os.geteuid() == 0:
        sys.stderr.write('Only root can run this script\n')
        sys.exit(1)

    if options.cleanup:
        print('Tearing down previous set up...')
        teardown(options)
        return 0

    if options.kvmcmd:
        print(kvmcall(options, 1, 'gamename'))
        return 0

    if len(args) != 1:
        parser.print_help()
        return 2

    # Pcap dir
    try:
        os.mkdir(options.tcpdump)
    except OSError: # Use an existing directory
        pass

    games = options.games.split(',')
    sys.path.append('gza')
    from gza import startgame

    mod = options.numvms % len(games)
    if mod != 0:
        options.numvms -= mod
        sys.stderr.write('Cannot evenly distribute concurrent VMs, only using %d VMs.\n'
                % options.numvms)

    try:
        # Run them VMs!
        setup(options)
        time.sleep(5)

        kvms = []
        vmlabels = range(1, options.numvms + 1)
        malware = glob.glob(os.path.join(args[0], "*"))
        gamelog = open(options.gamelog, 'w')
        gamepids = rungames(vmlabels, games, gamelog, startgame)
        time.sleep(10)
        # Runnin em
        while malware:
            while vmlabels:
                try:
                    sample = malware.pop(0)
                except IndexError:
                    print('Malware exhausted, waiting for running KVMs to terminate')
                    break
                for game in games:
                    # RUN DAT SHIT
                    i = vmlabels.pop(0)
                    installsample(options, sample, i)
                    print('Running: %s in VM #%d with game "%s"' % (sample, i, game))
                    kvms.append(kvm(options, i,
                        os.path.basename(sample) + '-' + game))
                    time.sleep(0.5)

            print('Sleeping for %d seconds...' % options.runtime)
            time.sleep(options.runtime)
            print('Terminating KVMs...')
            for proc in kvms:
                proc.terminate()
            for pid in gamepids:
                os.kill(pid, SIGUSR1) # Sends gamestate reset command
            del kvms[:]
            vmlabels = range(1, options.numvms + 1)
            print('KVMs terminated')
            time.sleep(5)

        for pid in gamepids:
            os.kill(pid, SIGINT) # CH-CH BLAOW
        pcaporganize(options)
    except KeyboardInterrupt:
        for proc in kvms:
            proc.terminate()
        for pid in gamepids:
            os.kill(pid, SIGINT)
        sys.stderr.write('User termination...\n')

    gamelog.close()
    teardown(options)
if __name__ == '__main__':
    sys.exit(main())
