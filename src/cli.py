#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import common
import gdata
import logging
import argparse
import socket
import struct


__program__ = "DREMO Client"
__version__ = '0.1a'
__author__ = "Josep Pon Farreny, Marc Piñol Pueyo"
__license__ = "MIT"
__status__ = "Development"


def main():
	global options

	setUpLogger()
	logging.info('Logging set up')

	host = options.host 
	port = options.port
	sinfo = common.SysInfo()
	logging.info('Host to connect to: %s ' % host)
	logging.info('Port to connect to: %s' % port)

	mcsock = beginConnection(host, port)
	update(host, port, sinfo)

#
#
def beginConnection(host, port):
	hello = '%c %s' %(gdata.SOH, port)

	response = communicateWithServer(host, port, hello)

	if response[0] == '200 OK':
		multicast_group, multicast_port = response[1].split()
		multicast_port = int(multicast_port)
		logging.debug('Received multicast group: %s' % multicast_group)
		logging.debug('Received multicast port: %d' % multicast_port)

	else:
		logging.info('Error: %s' % response[0])
		sys.exit(1)

	return initMulticast(multicast_group, multicast_port)

#
#
def initMulticast(group, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # more than one sock can use this port
	sock.bind(('', port))
	mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)

	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	return sock

#
#
def communicateWithServer(host, port, msg):
	sock = socket.socket()
	sock.settimeout(3) # TODO: REMOVE MAGIC NUMBER
	sock.connect((host, port))
	sock.send(msg+'\n')

	logging.debug('Message \'%s\' sent' % msg)

	response = common.util.recvEnd(sock, '\n')

	logging.debug('Response from the server (response code): %s' % response)

	if response:
		if response[0] == '200 OK':
			resp = common.util.recvEnd(sock, '\n')
			response.extend(resp)

			if not resp: response = ['Unknown error']

			logging.debug('Response from the server (response): %s' % resp)
	else:
		response = ['Unknown error']

	logging.debug('Total response from the server: %s' % response)

	return response

#
#
def update(host, port, sinfo):
	
	sinfo.update()
	sendXML(host, port, sinfo)

#
#
def sendXML(host, port, sinfo):
	XMLbuilder = common.sysinfoxml.SysInfoXMLBuilder()

	dao = sinfo.getSysInfoData()
	XMLbuilder.setXMLData(dao)
	
	msg = '%c %s %c' % (gdata.STX, XMLbuilder.getAsString(), gdata.ETX)

	response = communicateWithServer(host, port, msg)

	if response[0] != '200 OK':
		logging.info('Server error %s' % response[0])

#
#
def setUpLogger():
	"""setUpLogger(options) -> void

	Sets up the loggin module.

	"""
	global options

	lvl = logging.DEBUG if options.debug else logging.INFO
	#format = '[%(levelname)s] (%(asctime)s): %(message)s'
	format = '[%(levelname)s]: %(message)s'
	datefmt='%d/%m/%Y %H:%M:%S'

	logging.basicConfig(stream = options.logfile, level=lvl, format=format,
						datefmt=datefmt)

#
#
if __name__ == '__main__':

	parser = argparse.ArgumentParser(
				usage=globals()['__doc__'],
				version=__version__,
				description='Remote resource monitoring tool client')

	parser.add_argument('-host', required=True, help='server host name/ip')

	parser.add_argument('-port', required=True, type=int, help='server port')

	parser.add_argument('-lf', '--logfile', type=argparse.FileType('a'),
				default=sys.stderr, 
				help='logging file (default [stderr])')

	parser.add_argument('-d', '--debug', action='store_true', default=False,
				help='sets the loggin leve to DEBUG')

	options = parser.parse_args()

	main()