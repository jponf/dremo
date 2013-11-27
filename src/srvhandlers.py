# -*- coding: utf-8 -*-

# Imports
# -------

import gdata
import common
import socket
import srvdata
import helpers
import logging
import threading


# Classes
# -------

#
#
class MonitorHandler(threading.Thread):

	running_threads = set()
	running_threads_lock = threading.RLock()

	def __init__(self, sock, mid, init_msg, timeout):
		super(MonitorHandler, self).__init__()
		self.sock = sock
		self.mid = mid
		self.init_msg = init_msg
		self.timeout = timeout

		
	def run(self):
		self._registerRunningThread()
		sock = self.sock
		sock.settimeout( self.timeout )

		# Send initial message (Notify the handler is now managing the socket)
		sock.sendall(self.init_msg)

		try:
			data = common.recvEnd( sock, gdata.EOD )
			stx, sep, xml = data.partition(' ')

			if stx != gdata.STX:
				sock.sendall(helpers.getBadMessageError(
					'Incorrect start of update message %s' % stx) )
			else:
				infoparser = common.SysInfoXMLParser()
				infoparser.parseXML(xml)
				infodao = infoparser.getSysInfoData()
				srvdata.updateMonitorData(self.mid, infodao)
				sock.sendall( helpers.getOkMessage() )
				logging.debug("Updated client [%s] sysinfo" % self.mid)

		except socket.timeout:
			sock.sendall(helpers.getTimeoutError('Reached timeout of %f' 
												% options.connection_timeout) )
		except AttributeError, e:
			sock.sendall( helpers.getGeneralError(str(e)) )
		except ValueError, e:
			sock.sendall( helpers.getGeneralError(str(e)) )

		finally:
			self._unregisterRunningThread()
			addr = sock.getpeername()
			sock.close()
			logging.debug("MonitorHandler closed %s:%d" % addr)

	def _registerRunningThread(self):
		MonitorHandler.running_threads_lock.acquire()
		MonitorHandler.running_threads.add(self)
		MonitorHandler.running_threads_lock.release()

	def _unregisterRunningThread(self):
		MonitorHandler.running_threads_lock.acquire()
		MonitorHandler.running_threads.remove(self)
		MonitorHandler.running_threads_lock.release()

	@staticmethod
	def waitAll():
		MonitorHandler.running_threads_lock.acquire()

		while len(MonitorHandler.running_threads) > 0:
			rt = MonitorHandler.running_threads.pop()
			MonitorHandler.running_threads.add(rt)
			MonitorHandler.running_threads_lock.release()
			rt.join()

			MonitorHandler.running_threads_lock.acquire()
			if len(MonitorHandler.running_threads) == 0:
				MonitorHandler.running_threads_lock.release()

#
#
class CommandHandler(threading.Thread):
	
	running_threads = set()
	running_threads_lock = threading.RLock()

	def __init__(self, sock, m_id):
		super(self, CommandHandler).__init__()

		self.listen_sock = listen_sock
		in_socks = set([listen_sock])
		out_socks = set()

	def run():
		self._registerRunningThread()


		self._unregisterRunningThread()

	def _registerRunningThread(self):
		CommandHandler.running_threads_lock.acquire()
		CommandHandler.running_threads.add(self)
		CommandHandler.running_threads_lock.release()

	def _unregisterRunningThread(self):
		CommandHandler.running_threads_lock.acquire()
		CommandHandler.running_threads.remove(self)
		CommandHandler.running_threads_lock.release()

	@staticmethod
	def waitAll():
		CommandHandler.running_threads_lock.acquire()

		while len(CommandHandler.running_threads) > 0:
			rt = CommandHandler.running_threads.pop()
			CommandHandler.running_threads.add(rt)
			CommandHandler.running_threads_lock.release()
			rt.join()

			CommandHandler.running_threads_lock.acquire()
			if len(CommandHandler.running_threads) == 0:
				CommandHandler.running_threads_lock.release()
