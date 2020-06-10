#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from config import CrawlerConfig
import os
import subprocess
import time


class Fw():
    def __init__(self):
        self.bypass_rules = '/home/jnejati/bperf/config/fw/bypass.conf'
        self.redirect_rules = '/home/jnejati/bperf/config/fw/redirect.conf'
        self.iptables = '/sbin/iptables'
        self.restore = '/sbin/iptables-restore'

    def flush(self):
        subprocess.call(self.iptables + ' -F', shell=True)
        subprocess.call(self.iptables + ' -t nat -F', shell=True)

    def bypass(self):
        p = subprocess.call(self.restore +  ' < ' + self.bypass_rules, shell=True)

    def redirect(self):
        p = subprocess.call(self.restore +  ' < ' +  self.redirect_rules, shell=True)

if __name__=="__main__":
    print ("testing Fw class")
    fw = Fw()
    fw.flush()
    #fw.bypass()
    fw.redirect()
