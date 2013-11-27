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

# Hash algorithm

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



def initializeNewMonitorData(ip, port):
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
	common.assertType(mid, str, "Expected monitor id to be a string value")

	mdata = _getMonitor(mid)

	mdata[K_RWLOCK].acquireRead()
	sinfodao = mdata[K_SYSINFO]
	mdata[K_RWLOCK].release()

	return sinfodao

def getListOfMonitors():

	monitor_db_lock.acquireRead()
	midlist = [k for k in monitor_db.iterkeys()]
	monitor_db_lock.release()

	return midlist

def keepAliveMonitor(mid):
	common.assertType(mid, str, "Expected monitor id to be a string value")

	mdata = _getMonitor(mid)

	mdata[K_RWLOCK].acquireWrite()
	mdata[K_TIMESTAMP] = time.time()
	mdata[K_RWLOCK].release()

def existsMonitorData(mid):
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

def removeOldMonitorData(threshold):
	"""removeOldMonitorData(threshold: float) -> void

	Remove the data in the monitor's DB older than threshold seconds.

	"""
	common.assertType(mid, int, "Expected threshold to be a floating point value")

	monitor_db_lock.acquireWrite()
	cur_time = time.time()

	for mid in monitor_db.keys():
		if cur_time - monitor_db[mid][K_TIMESTAMP] > threshold:
			del monitor_db[mid]

	monitor_db_lock.release()