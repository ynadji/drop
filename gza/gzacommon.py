import sys
import nfqueue
import socket
import signal
import whitelist
from collections import defaultdict

class GZA(object):
    def __init__(self, vmnum, opts):
        self.gamestate = defaultdict(int)
        self.vmnum = vmnum
        self.opts = opts
        signal.signal(signal.SIGUSR1, self.reset) # So we can reset gamestate
        if self.opts.whitelist:
            whitelist.makewhitelist(opts.whitelistpath)
            self.whitelisted = whitelist.whitelisted

    def reset(self, signum, frame):
        print('Cleared game state!')
        self.gamestate.clear()
        try:
            self.q.try_run()
        except KeyboardInterrupt:
            print('Clean shutdown')
            self.q.unbind(socket.AF_INET)
            sys.exit(0)

    def playgame(self, i, payload):
        payload.set_verdict(nfqueue.NF_ACCEPT)

    def startgame(self):
        self.q = nfqueue.queue()
        self.q.open()
        self.q.set_callback(self.playgame)
        self.q.fast_open(self.vmnum, socket.AF_INET)
        try:
            self.q.try_run()
        except KeyboardInterrupt:
            print('Clean shutdown')
            self.q.unbind(socket.AF_INET)
            sys.exit(0)

