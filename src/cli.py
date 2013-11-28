#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import common
import gdata
import logging
import argparse
import socket
import struct
import threading	
import time
import select
import helper


__program__ = "DREMO Client"
__version__ = '0.4'
__author__ = "Josep Pon Farreny, Marc Piñol Pueyo"
__license__ = "MIT"
__status__ = "Development"


def main():
	options = gdata.getCommandLineOptions()

	setUpLogger()
	logging.info('Logging set up')
	logging.debug('Host to connect to: %s ' % options.broker_host)
	logging.debug('Port to connect to: %s' % options.broker_port)

	sinfo = common.SysInfo()
	sinfo.update()
	awakener = threading.Event()

	mcsock, client_id = beginConnection(options.broker_host, options.broker_port, sinfo)

	auto_update = AutoUpdater(options.time_between_updates, options.broker_host, options.broker_port, client_id, sinfo, awakener)
	auto_update.start()

	sock = common.createServerTCPSocket('0.0.0.0', options.listen_port, options.connection_queue_size)
	in_socks = set([mcsock, sock])

	_acceptForever(in_socks, sock, mcsock, awakener, sinfo, client_id)

#
#
def _acceptForever(in_socks, sock, mcsock, awakener, sinfo, client_id):
	while True:
		i, o , e = select.select(in_socks, [], [])

		for s in i:
			if s is sock:
				ns, addr = s.accept()
				logging.info('New request from %s:%d' % addr)
				_processInstruction(ns, 'tcp', awakener, sinfo, client_id)
				
			elif s is mcsock:
				ns, addr = s.accept()
				logging.info('New multicast request')
				_processInstruction(ns, 'mc', awakener, sinfo, client_id)

#
#
def _processInstruction(sock, connection_type, awakener, sinfo, client_id):
	instruction = common.recvEnd(sock, '\n').strip()
	logging.debug('Received instruction %s by %s' % (instruction, connection_type))
	instruction, sec, params = instruction.partition(' ')

	if connection_type == 'tcp':
		if not params:
			_updateFromSelf(sock, instruction, awakener, sinfo, client_id)
		else:
			_updateFromOther(sock, instruction, params)

	else:
		_updateFromSelf(sock, instruction, awakener, sinfo, client_id, connection_type)

#
#
def _updateFromSelf(sock, instruction, awakener, sinfo, client_id, connection_type=''):
	if helper.isCmdUpdate(instruction):
			sock.sendall(helper.getOkMessage())
			awakener.set()
			logging.debug('Requested update sent')

	elif not connection_type and helper.isCmdGet(instruction):
		sock.sendall(helper.getOkMessage())
		sendXML(sock, sinfo, client_id, False)
		logging.debug('Requested get sent')
		
	else:
		sock.send(getUnknownCmdError('Unknown command'))
		logging.debug('Request error sent')

#
#
def _updateFromOther(sock, instruction, params):
	ip, port = params.strip().split(':')
	port = int(port)
	response = ''

	try:
		sock_to_other = socket.create_connection((ip, port))
		sock_to_other.sendall(instruction + '\n')

		msg = common.recvEnd(sock_to_other, '\n\n')	
		response_head, sep, rest = msg.partition(' ')

		if response_head == '200':
			msg = common.recvEnd(sock_to_other, gdata.ETX) + gdata.ETX
			msg += common.recvEnd(sock_to_other, gdata.ETX) + gdata.ETX

	except:
		response = helper.getMonitorUnreachableError('Connection failed')

	finally:
		try:
			sock_to_other.close()
			sendThroughSocket(sock, msg, wait_for_response=False)
			#sock.sendall(msg)
		except:
			logging.debug('Error sending other client\'s data')

#
#
def beginConnection(host, port, sinfo):
	hello = '%c %s %c %s %c' %(gdata.BEL, port, gdata.ETX, buildXML(sinfo), gdata.ETX)

	ret_code, detail, response = sendThroughSocket(socket.create_connection((host, port)), hello)
	
	if ret_code == '200':
		ret_id, multicast_group, multicast_port  = response.split()
		multicast_port = int(multicast_port)

		logging.debug('Received client ID: %s' % ret_id)
		logging.debug('Received multicast group: %s' % multicast_group)
		logging.debug('Received multicast port: %d' % multicast_port)

	else:
		if ret_code:
			logging.info('Error: %s' % ret_code)
		else:
			logging.info('Unknown error')
		sys.exit(1)

	mcsock = common.createMulticastSocket(multicast_port)
	common.joinMulticastGroup(mcsock, multicast_group)
	return mcsock, ret_id

#
#
def _initMulticast(group, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # more than one sock can use this port
	sock.bind(('', port))
	
	mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)

	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	logging.debug('Multicast socket connected to %s:%d' %(group, port))

	return sock

#
#
def sendThroughSocket(sock, to_send, delim='\n\n', wait_for_response=True):
	code = ''
	detail = ''
	msg = ''
	
	try:
		sock.sendall(to_send)
		logging.debug('Message sent to server')

		if wait_for_response:
			first, sep, msg = common.recvEnd(sock, delim).partition('\n')
			code, sep, detail = first.partition(' ')
			msg, sep, garbage = msg.partition('\n')

			code.strip()
			detail.strip()
			msg.strip()

			logging.debug('Response from the server (response code): %s %s' % (code, detail))
			logging.debug('Response from the server (response): %s' % msg)

	except:
		code = helper.getMonitorUnreachableError()
		msg = 'Connection timed out'

	return code.strip(), detail.strip(), msg.strip()

#
#
def buildXML(sinfo):
	XMLbuilder = common.sysinfoxml.SysInfoXMLBuilder()

	dao = sinfo.getSysInfoData()
	XMLbuilder.setXMLData(dao)

	return XMLbuilder.getAsString()

#
#
def sendXML(sock, sinfo, client_id, wait_for_response=True):
	xml = buildXML(sinfo)
	msg = '%c %s %c %s %c' % (gdata.SOH, client_id, gdata.ETX, xml, gdata.ETX)

	return sendThroughSocket(sock, msg, wait_for_response=wait_for_response)

#
#
def setUpLogger():
	"""setUpLogger(options) -> void

	Sets up the loggin module.

	"""
	options = gdata.getCommandLineOptions()

	lvl = logging.DEBUG if options.debug else logging.INFO
	#format = '[%(levelname)s] (%(asctime)s): %(message)s'
	format = '[%(levelname)s]: %(message)s'
	datefmt='%d/%m/%Y %H:%M:%S'

	logging.basicConfig(stream = options.logfile, level=lvl, format=format,
						datefmt=datefmt)

#
#
class AutoUpdater(threading.Thread):
	def __init__(self, tbu, host, port, client_id, sinfo, awakener):
		threading.Thread.__init__(self)

		self.tbu = tbu
		self.host = host
		self.port = port
		self.client_id = client_id
		self.sinfo = sinfo
		self.awakener = awakener

	#
	#
	def run(self):
		logging.debug('Updater thread started')

		while True:
			self.update(socket.create_connection((self.host, self.port)), self.sinfo, self.client_id)

			if self.awakener.wait(self.tbu): # sleep until tbu or someone calls awakener.set()
				self.awakener.clear() # reset the internal flag

	#
	#
	def update(self, sock, sinfo, client_id):  
	
		sinfo.update()
		sendXML(sock, sinfo, client_id)

#
#
if __name__ == '__main__':

	gdata.initCliCommandLineOptions(sys.argv[1:], __version__)

	main()