#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
# -------

import sys
import gdata
import common
import socket
import logging
import srvhandlers
import srvmainloop

# Program Data
# ------------
__program__ = "DREMO Server"
__version__ = '0.1a'
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
	listen_sock, mgroup_socket = setUpSockets()

	# Starts runs the main loop, close all the sockets at exit
	srvmainloop.mainLoop(listen_sock, mgroup_socket)
	

def setUpSockets():
	"""setUpSockets() -> tcp_socket, multicast_socket

	Sets up the clients connection socket and the multicast socket.

	"""
	options = gdata.getCommandLineOptions()

	conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind conn_sock
	try:
		conn_sock.bind((options.ip, options.port))
		conn_sock.listen(options.connection_queue_size)
		logging.debug('Socket bound to %s:%d' % (options.ip, options.port))
	except socket.error, e:
		logging.critical("%s [%s]" % (str(e), options.ip))
		sys.exit(-1)

	# Set multicast socket options (only send)
	mgroup_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	mgroup_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 
		options.multicast_group_ttl)
	# Avoid receiving own messages
	# mgroup_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

	return conn_sock, mgroup_sock

def setUpLogging():
	"""setUpLogging() -> void

	Sets up the loggin module.

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
	logging.debug("Port: " + str(o.port) )
	logging.debug("Connection timeout: " + str(o.connection_timeout) )
	logging.debug("Connection queue size: " + str(o.connection_queue_size))
	logging.debug("Multicast Group: " + o.multicast_group)
	logging.debug("Multicast Port: " + str(o.multicast_group_port))
	logging.debug("Multicast TTL: " + str(o.multicast_group_ttl))
	logging.debug("Logfile: " + o.logfile.name)

#
#
if __name__ == '__main__':

	gdata.initSrvCommandLineOptions(sys.argv[1:], __version__)

	main()