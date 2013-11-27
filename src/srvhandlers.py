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
		cls.reg_lock.acquire()
		cls.reg.add(thread)
		cls.reg_lock.release()

	@staticmethod
	def _unregisterThread(cls, thread):
		cls.reg_lock.acquire()
		cls.reg.remove(thread)
		cls.reg_lock.release()

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
		super(self, MonitorHandler).__init__(self)
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
			data = common.readEnd(sock, gdata.STX)
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
			sock.sendall( helper.getGenericerror(str(e)) )
		except ValueError, e:
			sock.sendall( helper.getGenericerror(str(e)) )

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
		msg = helpers.getOkMessage(
				"%s %s %d" 
				% (mid, opt.multicast_group, opt.multicast_group_port)
			)

		sock.sendall(msg)

		self._updateMonitor(mid)

	def _updateMonitor(self, mid):
		
		if srvdata.existsMonitorData(mid):
			srvdata.keepAliveMonitor(mid)

			data = common.readEnd(self.sock, gdata.ETX).strip()
			infoparser = common.SysInfoXMLParser()
			infoparser.parseXML(data)
			infodao = infoparser.getSysInfoData()
			srvdata.updateMonitorData(mid, infodao)
			self.sock.sendall( helpers.getOkMessage("Update successful") )
		
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
	
	@staticmethod
	def waitAll():
		MonitorHandler._waitAll(MonitorHandler)
