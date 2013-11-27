# -*- coding: utf-8 -*-

# Imports
# -------

import gdata
import common
import select
import socket
import helpers
import logging
import srvdata
import srvhandlers

# Global variables
# ----------------

# Sockets we want to read from
in_socks = set()
# Sockets we want to write to
out_socks = set()
# Data to send {socket -> str}
out_data = {}
# Finalized sockets will send their remaining data and close
finalized_socks = set()

# Functions
# ---------

def mainLoop(listen_sock, mgroup_sock):
	common.assertType(listen_sock, socket.socket, "Expected socket.socket")
	common.assertType(mgroup_sock, socket.socket, "Expected socket.socket")

	run = True
	timeout = gdata.getCommandLineOptions().connection_timeout
	in_socks.add(listen_sock)
	
	try:
		while run:
			i, o, e = select.select(in_socks, out_socks, [], timeout)

			# In sockets
			for s in i:
				if s is listen_sock:
					handleNewConnection(s)
				else:
					ndata = common.recvEnd(s, gdata.EOD).strip()

					if ndata:
						handleSocketInput(s, ndata)
					elif s is not sys.stdin:
						handleDisconnection(s)
						
			# Out sockets
			for s in o:
				handleSocketOutput(s)
									
	except KeyboardInterrupt:
		logging.info("Finishing due to keyboard interruption")
	finally:
		waitThreads()
		closeSockets()

def handleSocketInput(sock, data):

	if helpers.isCmdGreeting(data):
		createCommandHandler(sock)

	else:
		head, sep, body = data.partition(' ')

		if helpers.isNewMonitor(head):
			handleNewMonitor(sock, body.strip())
	
		elif helpers.isStartOfHead(head):
			createMonitorHandler(sock, body.strip(), helpers.getOkMessage())
		else:
			setSocketAsFinalized(sock, 
				helpers.getBadMessageError('Unexpected message %s' % data))

def handleSocketOutput(sock):
	tosend = out_data.get(sock)	# gets data in the queue

	if tosend:
		nsnt = sock.send(tosend)
		tosend = tosend[nsnt:]
		# Save remaining data or remove buffer
		if tosend:
			out_data[s] = tosend
		else:
			# Remove socket from select lists
			if sock in finalized_socks:
				handleDisconnection(sock)
			else:
				if sock in out_data: del out_data[sock]
				if sock in out_socks: out_socks.remove(sock)

def handleNewMonitor(sock, port):
	try:
		iport = int(port) # Just to check port range
		if iport < 1 or iport > 49152:
			raise ValueError("Port value (%d) out of range [1-49152]" % iport)

		mid = srvdata.initializeNewMonitorData(sock.getpeername()[0], port)

		in_socks.remove(sock)

		options = gdata.getCommandLineOptions()
		mg = options.multicast_group
		mgp = options.multicast_group_port

		msg = helpers.getOkMessage("%s %s %d" % (mid, mg, mgp))
		createMonitorHandler(sock, mid, msg)

	except ValueError, e:
		setSocketAsFinalized(sock, 
			helpers.getGeneralError(str(e)) )


def handleDisconnection(sock):
	if sock in in_socks: in_socks.remove(sock)
	if sock in out_socks: out_socks.remove(sock)
	if sock in out_data: del out_data[sock]

	addr = sock.getpeername()

	if sock in finalized_socks:
		sock.close()
		finalized_socks.remove(sock)
		logging.debug("Finalized socket %s:%d" % addr)
	else:
		logging.debug("Disconnection from %s:%d" % addr )

def handleNewConnection(sock):
	ns, addr = sock.accept()
	in_socks.add(ns)
	logging.debug("New connection: %s" + str(addr))

def createMonitorHandler(sock, mid, init_msg):
	
	if srvdata.existsMonitorData(mid):
		srvdata.keepAliveMonitor(mid)

		timeout = gdata.getCommandLineOptions().connection_timeout

		mhandler = srvhandlers.MonitorHandler(sock, mid, init_msg, timeout)
		mhandler.start()

	else:
		setSocketAsFinalized(sock, helpers.getMonitorNotFoundError(
							"There isn't any monitor with id: %s" % mid) )

def createCommandHandler(sock):
	pass

def setSocketAsFinalized(sock, last_data):
	if sock in in_socks: in_socks.remove(sock)

	finalized_socks.add(sock)
	addSocketOutData(sock, last_data)	

def addSocketOutData(sock, data):
	if sock not in out_socks: out_socks.add(sock)
	out_data[sock] = out_data.get(sock, '') + data

def closeSockets():
	logging.info("Closing main loop input sockets")
	for s in in_socks:
		s.close()
	logging.info("Main loop input sockets closed")

	logging.info("Closing main loop output sockets")
	for s in out_socks:
		s.close()
	logging.info("Main loop output sockets closed")

def waitThreads():
	logging.info("Waiting for all monitor handlers")
	srvhandlers.MonitorHandler.waitAll()
	logging.info("All monitor handlers finished")

	logging.info("Waiting for all command handlers")
	srvhandlers.CommandHandler.waitAll()
	logging.info("All command handlers finished")
