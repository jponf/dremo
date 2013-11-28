#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
# -------

import sys
import gdata
import common
import select
import socket
import logging
import srvhandlers

# Program Data
# ------------
__program__ = "DREMO Server"
__version__ = '0.5a'
__author__ = "Josep Pon Farreny, Marc Piñol Pueyo"
__license__ = "MIT"
__status__ = "Development"

# Functions
# ---------

def main():

	# Set logging and print command line options
	setUpLogging()
	printCommandLineOptions()

	# Set up sockets
	mon_sock, cli_sock, m_sock = setUpSockets()

	try:
		# Starts runs the main loop, close all the sockets at exit
		mainLoop(mon_sock, cli_sock, m_sock)
	finally:
		mon_sock.close()
		logging.info("Monitors socket closed")
		cli_sock.close()
		logging.info("Commands socket closed")
		m_sock.close()

def mainLoop(mon_sock, cli_sock, m_sock):
	"""mainLoop(mon_sock: socket, cli_sock: socket, m_sock: socket) -> void

	Main logic of the applications, listens to mon_sock and cli_sock and 
	starts threads to handle the petitions.

	"""
	opt = gdata.getCommandLineOptions()
	timeout = opt.connection_timeout
	mg_ip = opt.multicast_group
	mg_port = opt.multicast_group_port

	insocks = set([mon_sock, cli_sock])
	logging.info("Server running press Ctrl+C to Quit!")

	try:
		while True:
			i, o , e = select.select(insocks, [], [])

			for s in i:
				t = None
				if s is mon_sock:
					ns, addr = s.accept()
					logging.debug("New monitor connexion from %s:%d" % addr)

					t = srvhandlers.MonitorHandler(ns, timeout)
					t.start()

				else:
					# If is not mon_sock then it is conn_sock
					ns, addr = s.accept()
					logging.debug("New command connexion from %s:%d" % addr)

					t = srvhandlers.CommandHandler(ns, m_sock, mg_ip, mg_port,
													timeout)
					t.start()

	except KeyboardInterrupt:
		logging.info("Finishing due to KeyboardInterrupt")
	finally:
		logging.info("Waiting threads termination")
		waitThreads()
		logging.info("All threads terminated")

def waitThreads():
	srvhandlers.MonitorHandler.waitAll()
	srvhandlers.CommandHandler.waitAll()
	

def setUpSockets():
	"""setUpSockets() -> tcp_socket, multicast_socket

	Sets up the clients connection socket and the multicast socket.

	"""
	opt = gdata.getCommandLineOptions()

	mon_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind conn_sock
	try:
		mon_sock.bind((opt.ip, opt.mon_port))
		mon_sock.listen(opt.connection_queue_size)
		logging.info('Monitor socket bound to %s:%d' % (opt.ip, opt.mon_port))

		cli_sock.bind((opt.ip, opt.cli_port))
		cli_sock.listen(opt.connection_queue_size)
		logging.info('Client socket bound to %s:%d' % (opt.ip, opt.cli_port))

	except socket.error, e:
		logging.critical("%s [%s]" % (str(e), opt.ip))
		sys.exit(-1)

	# Set multicast socket options (only send)
	mgroup_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	mgroup_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 
		opt.multicast_group_ttl)
	# Avoid receiving own messages
	# mgroup_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

	return mon_sock, cli_sock, mgroup_sock

def setUpLogging():
	"""setUpLogging() -> void

	Sets up the logging module.

	"""
	options = gdata.getCommandLineOptions()

	lvl = logging.DEBUG if options.debug else logging.INFO
	#format = '[%(levelname)s] (%(asctime)s): %(message)s'
	format = '[%(levelname)s]: %(message)s'
	datefmt='%d/%m/%Y %H:%M:%S'

	logging.basicConfig(stream = options.logfile, level=lvl, format=format,
						datefmt=datefmt)

def printCommandLineOptions():
	"""printOptions() -> void 

	Prints options to the logging file.

	"""
	o = gdata.getCommandLineOptions()

	logging.debug("IP: " + o.ip)
	logging.debug("Monitors Port: " + str(o.mon_port) )
	logging.debug("Clients Port: " + str(o.cli_port))
	logging.debug("Connection timeout: " + str(o.connection_timeout) )
	logging.debug("Connection queue size: " + str(o.connection_queue_size))
	logging.debug("Multicast Group: " + o.multicast_group)
	logging.debug("Multicast Port: " + str(o.multicast_group_port))
	logging.debug("Multicast TTL: " + str(o.multicast_group_ttl))
	logging.debug("Data life time: " + str(o.data_life_time))
	logging.debug("Logfile: " + o.logfile.name)

#
#
if __name__ == '__main__':
	# Initialize command line options
	gdata.initSrvCommandLineOptions(sys.argv[1:], __version__)

	main()