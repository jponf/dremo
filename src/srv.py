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
__version__ = '0.7a'
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
	except Exception, e:
		logging.critical("Finishing due to unknown exception:\n%s" % str(e))
		if opt.debug:
<<<<<<< HEAD
			import traceback; traceback.print_exc(sys.stderr)
=======
			import traceback; traceback.print_exc()
>>>>>>> afc0e9f6ba8a5bf4b04242ea8f7be43e1b8f5333
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
	queue_size = opt.connection_queue_size
	iface = opt.ip

	mon_sock = None; cmd_sock = None; mgroup_sock = None

	# Bind conn_sock
	try:
		mon_sock = common.createServerTCPSocket(iface, opt.mon_port, queue_size)
		logging.info('Monitor socket bound to %s:%d' % (iface, opt.mon_port))

		cmd_sock = common.createServerTCPSocket(iface, opt.cmd_port, queue_size)
		logging.info('Client socket bound to %s:%d' % (iface, opt.cmd_port))

		# Set multicast socket options (only send)
		mgroup_sock = common.createMulticastSocket(None, opt.multicast_group_ttl)
		logging.info('Multicas socket created (Not joined)')
		
	except socket.error, e:
		logging.critical("%s [%s]. Closing sockets" % (str(e), opt.ip))
		if mon_sock: mon_sock.close()
		if cmd_sock: cmd_sock.close()
		sys.exit(-1)	

	return mon_sock, cmd_sock, mgroup_sock

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
	logging.debug("Clients Port: " + str(o.cmd_port))
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