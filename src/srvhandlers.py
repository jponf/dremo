# -*- coding: utf-8 -*-

# Imports
# -------

import gdata
import common
import helper
import socket
import srvdata
import logging
import threading


# Classes
# -------

class ThreadWithRegister(threading.Thread):

	_reg_lock = threading.RLock()
	_reg = set()

	@staticmethod
	def _registerThread(cls, thread):
		cls._reg_lock.acquire()
		cls._reg.add(thread)
		cls._reg_lock.release()

	@staticmethod
	def _unregisterThread(cls, thread):
		cls._reg_lock.acquire()
		cls._reg.remove(thread)
		cls._reg_lock.release()

	@staticmethod
	def _waitAll(cls):
		cls._reg_lock.acquire()

		while len(cls._reg) > 0:
			rt = cls._reg.pop()
			cls._reg.add(rt)
			cls._reg_lock.release()
			rt.join()

			cls._reg_lock.acquire()
			if len(cls._reg) == 0:
				cls._reg_lock.release()
				break
#
#
class MonitorHandler(ThreadWithRegister):

	def __init__(self, sock, timeout):
		super(MonitorHandler, self).__init__()
		self.sock = sock
		self.timeout = timeout
		self.addr = sock.getpeername()	# Save socket address

	def run(self):
		"""run() -> void

		Handles the communication events and errors with a resource monitor.

		"""
		MonitorHandler._registerThread(MonitorHandler, self)
		sock = self.sock
		sock.settimeout( self.timeout )

		try:
			data = common.recvEnd(sock, gdata.ETX)
			logging.debug("%s:%d Data:\n%s" % (self.addr[0], self.addr[1], data))
			head, sep, body = data.partition(' ')
			head = head.strip()
			body = body.strip()

			if helper.isBEL(head):		# New monitor
				self._newMonitor(body)
			elif helper.isSOH(head):	# Monitor data update
				self._updateMonitor(body)
			else:
				sock.sendall( helper.getBadMessageError("Unknown message") )

		except socket.timeout:
			sock.sendall( helper.getTimeoutError(
							"Reached timeout of %.1f seconds" % self.timeout) 
						)
		except AttributeError, e:
			sock.sendall( helper.getGenericError(str(e)) )
		except ValueError, e:
			sock.sendall( helper.getGenericError(str(e)) )

		finally:
			sock.close()
			logging.debug("Monitor handler closed socket to %s:%s" % self.addr)
			MonitorHandler._unregisterThread(MonitorHandler, self)

	def _newMonitor(self, port):
		
		iport = int(port)
		if iport < gdata.SOCK_MIN_PORT or iport > gdata.SOCK_MAX_PORT:
			raise ValueError("Port value (%d) out of range [%d-%d]" 
				% (iport, gdata.SOCK_MIN_PORT, gdata.SOCK_MAX_PORT))

		mid = srvdata.initializeNewMonitorData(self.addr[0], port)

		opt = gdata.getCommandLineOptions()
		msg = helper.getOkMessage(
				"%s %s %d" 
				% (mid, opt.multicast_group, opt.multicast_group_port)
			)

		self.sock.sendall(msg)

		self._updateMonitor(mid)

	def _updateMonitor(self, mid):
		
		if srvdata.existsMonitorData(mid):
			srvdata.keepAliveMonitor(mid)

			data = common.recvEnd(self.sock, gdata.ETX).strip()
			logging.debug("%s:%d Data:\n%s" % (self.addr[0], self.addr[1], data))

			infoparser = common.SysInfoXMLParser()
			infoparser.parseXML(data)
			infodao = infoparser.getSysInfoData()
			srvdata.updateMonitorData(mid, infodao)
			self.sock.sendall( helper.getOkMessage("Update successful") )
		
		else:
			self.sock.sendall( 
				helper.getMonitorNotFoundError(
					"There isn't any monitor with id: %s" % mid)
				)

	@staticmethod
	def waitAll():
		MonitorHandler._waitAll(MonitorHandler)

#
#
class CommandHandler(ThreadWithRegister):
	
	def __init__(self, sock):
		super(self, CommandHandler).__init__(self)

	@staticmethod
	def waitAll():
		MonitorHandler._waitAll(MonitorHandler)
