# -*- coding: utf-8 -*-

# Imports
# -------

import time
import common
import hashlib
import logging
import threading

# Data
# ----

# Monitor data indices
K_IP = 0
K_PORT = 1
K_SYSINFO = 2
K_TIMESTAMP = 3
K_RWLOCK = 4

# Contains monitor information { id -> (ip, port, sysinfodao, time, rwlock) }
monitor_db = { }
# Exclusive acces to modify monitor_db
monitor_db_lock = common.ReadWriteLock()

# Functions
# ---------

def initializeNewMonitorData(ip, port):
	"""initializeNewMonitorData(ip: str, port: str) -> str

	Generates a monitor id with the given ip and port and initializes an 
	entry in the internal db for this new monitor id.

	Returns the generated monitor id.

	"""
	common.assertType(ip, str, "Expected ip to be a string value")
	common.assertType(port, str, "Expected port to be a string value")

	sha256 = hashlib.sha256()	
	sha256.update(ip)
	sha256.update(port)
	mid = sha256.hexdigest()

	monitor_db_lock.acquireWrite()
	monitor_db[mid] = [ip, port, None, time.time(), common.ReadWriteLock()]
	monitor_db_lock.release()

	return mid


def updateMonitorData(mid, sinfodao):
	"""updateMonitorData(mid: str, sinfodao: SysInfoDAO) -> void

	Updates the information of the specified client.

	"""
	common.assertType(mid, str, "Expeced monitor id to be a string value")
	common.assertType(sinfodao, common.SysInfoDAO, "Expected SysInfoDAO")

	mdata = _getMonitor(mid)

	mdata[K_RWLOCK].acquireWrite()
	mdata[K_SYSINFO] = sinfodao
	mdata[K_TIMESTAMP] = time.time()
	mdata[K_RWLOCK].release()

def getMonitorData(mid):
	"""getMonitorData(mid: str) -> SysInfoDAO, str, str

	Returns the stored data of a monitor or raises a KeyError exception if the
	monitor does not exist.

	Returns the tuple (SysInfoDAO, ip, port)

	"""
	common.assertType(mid, str, "Expected monitor id to be a string value")

	mdata = _getMonitor(mid)

	mdata[K_RWLOCK].acquireRead()
	sinfodao = mdata[K_SYSINFO]
	port = mdata[K_PORT]
	ip = mdata[K_IP]
	mdata[K_RWLOCK].release()

	return sinfodao, ip, port

def getAllMonitorsData():
	"""getAllMonitorsData() -> [ (SysInfoDAO, str, str) ]

	Returns a list with all the SysInfoDAO on the DB.

	Returns a list of tuples with (SysInfoDAO, ip, port)

	"""
	monitor_db_lock.acquireRead()
	mdatal = [ (v[K_SYSINFO], v[K_IP], v[K_PORT])
					for k, v in monitor_db.iteritems() ]
	monitor_db_lock.release()

	return mdatal

def getListOfMonitors():
	"""getListOfMonitors() -> [str]

	Returns a list filled with the id of all the stored monitors.

	"""
	monitor_db_lock.acquireRead()
	midlist = [k for k in monitor_db.iterkeys()]
	monitor_db_lock.release()

	return midlist

def keepAliveMonitor(mid):
	"""keepAliveMonitor(mid: str) -> void

	Prolongs the life of a monitor 'data_life_time'.

	"""
	common.assertType(mid, str, "Expected monitor id to be a string value")

	mdata = _getMonitor(mid)

	mdata[K_RWLOCK].acquireWrite()
	mdata[K_TIMESTAMP] = time.time()
	mdata[K_RWLOCK].release()

def existsMonitorData(mid):
	"""existsMonitorData(mid: str) -> bool

	Returns true if the DB contains data of the specified monitor

	"""
	common.assertType(mid, str, "Expected monitor id to be a string value")

	monitor_db_lock.acquireRead()
	ret = mid in monitor_db
	monitor_db_lock.release()

	return ret

# Get an internal reference to a monitor data
def _getMonitor(mid):

	monitor_db_lock.acquireRead()
	mdata = monitor_db[mid]
	monitor_db_lock.release()

	return mdata

def removeOldMonitorData(max_time):
	"""removeOldMonitorData(max_time: float) -> void

	Remove data in the monitor's DB older than max_time seconds.

	"""
	monitor_db_lock.acquireWrite()
	cur_time = time.time()

	for mid in monitor_db.keys():
		if cur_time - monitor_db[mid][K_TIMESTAMP] > max_time:
			del monitor_db[mid]
			logging.debug("Droped data of: %s" % mid)
	monitor_db_lock.release()

#
## Cleans the database every data life time
class DBGarbageCollector(threading.Thread):

	def __init__(self, gc_time, data_life_time):
		super(DBGarbageCollector, self).__init__()

		self._gc_time = gc_time
		self._data_time = data_life_time
		self._awakener = threading.Event()
		self._mutex = threading.RLock()
		self._active = True

	## Override
	def run(self):

		self._setRunState()

		self._mutex.acquire() # lock and check active state
		while self._active:
			self._mutex.release() # unlock and wait

			if self._awakener.wait(self._gc_time):
				self._awakener.clear()	# Resets the internal flag

			removeOldMonitorData(self._data_time)

			self._mutex.acquire() # lock to check the active state

		self._mutex.release() # comes out with the mutex acquired


	## Sets internal data to a consistent state before starting the run loop
	def _setRunState(self):
		self._awakener.clear()	# Clears internal flag before first wait
		
		self._mutex.acquire()
		self._active = True
		self._mutex.release()

	@staticmethod
	def stop(db_gc):
		"""stop() -> void

		Given a DBGarbageCollector instance set the stop flag and waits
		until the collector thread termination.

		"""
		db_gc._mutex.acquire()
		db_gc._active = False
		db_gc._awakener.set()
		db_gc._mutex.release()
		db_gc.join()

