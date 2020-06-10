#!/usr/bin/env python
# -*- coding: utf-8 -*-
# figure a way out to read filename from config parser

import random

from configparser import SafeConfigParser
import os
import csv
import socket

MYDIR = os.path.dirname(__file__)

class CrawlerConfig():

	def __init__(self, cfg_file = '../config/crawler.config'):
		self.config = SafeConfigParser()
		self.config.read(cfg_file)
		self.app_log = self.config.get('default','app_log').strip()
		self.adb_log = self.config.get('default','adb_log').strip()
		self.net_ip = self.get_ip_address()
		self.proxy = self.config.get('default','proxy').strip()
		self.retries = self.config.get('default', 'retries').strip()
		self.redirection_timeout = int(self.config.get('default','redirection_timeout'))
		self.test = True if ((self.config.get('test', 'test_run').strip())=="True") else False
		self.shuffle = True if ((self.config.get('test', 'shuffle').strip())=="True") else False
		self.mal_sites = self.getMalwareSites()
		self.emulated = True if ((self.config.get('emulator', 'emulated').strip())=="True") else False
		self.num_sites = int(self.config.get('test', 'sample_size').strip())
		self.start_from = int(self.config.get('test', 'start_from').strip())
		self.redirection_timeout = int(self.config.get('default','redirection_timeout').strip())

		self.studio_path = self.config.get('emulator','studio_path').strip()
		self.emulator = self.config.get('emulator','emulator').strip()
		self.pin = self.config.get('emulator','pin').strip()
		self.avds = [(x.strip()).encode('ascii', 'ignore') for x in\
			     (self.config.get('emulator','avds').split(','))]
		self.emu_start_delay = int(self.config.get('emulator','start_delay').strip())

	def getMalwareSites(self):
		sites = []
		malware_sites = self.config.get('default', 'mal_sites_file')
		with open(malware_sites) as sfp:
			creader = csv.reader(sfp)
			for row in creader:
				sites.append(row[0])
		# shuffle the list
		if self.shuffle:
			random.shuffle(sites)
		return sites

	'''get the ip of iface connected to net'''
	@staticmethod
	def get_ip_address():
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.connect(("8.8.8.8", 80))
			return s.getsockname()[0]
		except Exception as e:
			print ("No internet connection!")
			return None

if __name__=="__main__":

	cfg = CrawlerConfig()
	#print cfg.mal_sites
	print cfg.config.get('test', 'test_run')
	print cfg.config.get('test', 'sample_size')
	l = cfg.config.get('default','browsers')
	print l
	print type(cfg.get_ip_address()), cfg.get_ip_address()
	print cfg.proxy
	print cfg.net_ip
	print "start_from: {0}".format(cfg.start_from)
	print cfg.emulator
	print cfg.avds
	print cfg.emu_start_delay
	print cfg.studio_path
