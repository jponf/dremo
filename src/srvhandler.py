#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gdata
import common
import select
import socket
import logging
import threading

#
#
def mainLoop(listen_sock, mgroup_sock, options):
	common.assertType(listen_sock, socket.socket, "Expected socket.socket")
	common.assertType(mgroup_sock, socket.socket, "Expected socket.socket")

	run = True
	in_socks = set([listen_sock, sys.stdin])
	out_socks = set()

	try:
		while run:
			i, o, e = select.select(in_socks, out_socks, [], 
								options.connection_timeout)

			for s in i:
				if s is listen_sock:
					ns, addr = s.accept()
					in_socks.add(s)
					logging.info("New connection")
					logging.debug("From Address: " + addr)

				elif s is sys.stdin:
					indata = s.readline().strip().lower()
					# Handle input, returns false on quit command
					run = handleUserInput(indata)

				else:
					ndata = common.recvEnd(s, '\n').srip()

					if ndata == gdata.CMD_GREETING:
						# Create a new command handler
						pass
					elif ndata.startswith(gdata.SOH):
						# Create a new monitor handler
						pass

	except KeyboardInterrupt:
		logging.info("Finishing due to keyboard interruption")
		pass # Ctrl+C

	finally:
		logging.info("Waiting for all monitor handlers")
		MonitorHandler.waitAll()
		logging.info("All monitor handlers finished")

		logging.info("Waiting for all command handlers")
		CommandHandler.waitAll()
		logging.info("All command handlers finished")

		logging.info("Closing main loop input sockets")
		for s in in_socks:
			s.close()
		logging.info("Main loop input sockets closed")
		logging.info("Closing main loop output sockets")
		for s in out_socks:
			s.close()
		logging.info("Main loop output sockets closed")


def handleUserInput(indata):
	"""handleUserInput(indata:str) -> bool

	Returns False if the quit command is received, True otherwise

	"""

	if indata == gdata.CMD_QUIT:
		return False

#
#
class MonitorHandler(threading.Thread):

	running_threads = set()
	running_threads_mtx = None

	def __init__(self):
		super(self).__init__()

		self.listen_sock = listen_sock
		in_socks = set([listen_sock])
		out_socks = set()

	def run():
		pass

	@staticmethod
	def waitAll():
		pass

#
#
class CommandHandler(threading.Thread):
	
	running_threads = set()
	running_threads_mtx = None 

	def __init__(self, sock):
		super(self, Acceptor).__init__()

		self.listen_sock = listen_sock
		in_socks = set([listen_sock])
		out_socks = set()

	def run():
		pass

	@staticmethod
	def waitAll():
		pass
