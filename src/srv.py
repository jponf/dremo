#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import common
import socket
import logging
import argparse
import srvhandler

__program__ = "DREMO Server"
__version__ = '0.1a'
__author__ = "Josep Pon Farreny, Marc Piñol Pueyo"
__license__ = "MIT"
__status__ = "Development"


def main():

	# Set logging and print command line options
	setUpLogging()
	printCommandLineOptions()
	
	# Set up sockets
	listen_sock, mgroup_socket = setUpSockets()

	# Starts runs the main loop, close all the sockets at exit
	srvhandler.mainLoop(listen_sock, mgroup_socket, options)
	

def setUpSockets():
	"""setUpSockets() -> tcp_socket, multicast_socket

	Sets up the clients connection socket and the multicast socket.

	"""
	conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind conn_sock
	conn_sock.bind((options.ip, options.port))
	conn_sock.listen(options.connection_queue_size)
	logging.debug('Socket bound to %s:%d' % (options.ip, options.port))

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
	o = options

	logging.debug("IP: " + o.ip)
	logging.debug("Port: " + str(o.port) )
	logging.debug("Connection timeout: " + str(o.connection_timeout) )
	logging.debug("Connection queue size: " + str(o.connection_queue_size))
	logging.debug("Multicast Group: " + o.multicast_group)
	logging.debug("Multicast Port: " + str(o.multicast_group_port))
	logging.debug("Multicast TTL: " + str(o.multicast_group_ttl))
	logging.debug("Logfile: " + str(o.logfile))

#
#
if __name__ == '__main__':

	parser = argparse.ArgumentParser(
				usage=globals()['__doc__'],
				version=__version__,
				description='Remote resource monitoring tool client')

	parser.add_argument('-ip', default='0.0.0.0', 
				help='server listen interface ip')

	parser.add_argument('-port', default=6666, type=int,
				help='server listen port')

	parser.add_argument('-cto', '--connection-timeout', default=3, type=float,
				help='client connection timeout')

	parser.add_argument('-cqs', '--connection-queue-size', default=100, 
				type=int, help="")

	parser.add_argument('-mg', '--multicast-group', default='227.123.456.789',
				help='multicast group ip')

	parser.add_argument('-mgp', '--multicast-group-port', default=7777,
				help='multicast group port')

	parser.add_argument('-mgttl', '--multicast-group-ttl', type=int, default=16,
				help='multicast group packets ttl')

	parser.add_argument('-lf', '--logfile', type=argparse.FileType('a'),
				default=sys.stderr, 
				help='Logging file (default [stderr])')

	parser.add_argument('-d', '--debug', action='store_true', default=False,
				help='sets the loggin leve to DEBUG')

	options = parser.parse_args()

	main()