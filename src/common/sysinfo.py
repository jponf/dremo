#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import time
import util
import psutil          # https://code.google.com/p/psutil/wiki/Documentation
import platform


# Determines the operating system in module load time
PYTHON_SYSTEM = platform.system()
OS_IS_OSX = PYTHON_SYSTEM.lower() == 'darwin' and platform.mac_ver()[0]
OS_IS_WIN = PYTHON_SYSTEM.lower() == 'windows'
OS_IS_LINUX = PYTHON_SYSTEM.lower() == 'linux'

OS_NAME = ""
OS_VERSION = ""
osGetCPULoadAvg = None

if OS_IS_LINUX:
	OS_NAME, OS_VERSION, _ = platform.linux_distribution()
	osGetCPULoadAvg = os.getloadavg

elif OS_IS_OSX:
	OS_NAME = "Mac OS X"
	OS_VERSION, _, _ = platform.mac_ver()
	osGetCPULoadAvg = os.getloadavg

elif OS_IS_WIN:
	OS_NAME = "Windows"
	OS_VERSION, _, _, _ = platform.win32_ver()
	osGetCPULoadAvg = lambda : 0.0, 0.0, 0.0


## Encapsulate methods to retrieve system information
class SysInfo:

	def __init__(self):
		self._dao = SysInfoDAO()

	def update(self):
		"""update() -> void

		Updates information of the system state at the time of the call to 
		this function.

		"""
		self._updateCPU()
		self._updateMemory()
		self._updateProcesses()

		self._dao.setTimestamp(time.gmtime())

	def _updateMemory(self):
		"""_updateMemory() -> void

		Updates the system's memory stats.

		"""
		dao = self._dao

		vmem = map(int, psutil.virtual_memory())
		dao.setTotalVirtualMemory(vmem[0])
		dao.setAvaliableVirtualMemory(vmem[1])
		dao.setUsedVirtualMemory(vmem[3])
		dao.setFreeVirtualMemory(vmem[4])
		
		swap = map(int, psutil.swap_memory())
		dao.setTotalSwapMemory(swap[0])
		dao.setUsedSwapMemory(swap[1])
		dao.setFreeSwapMemory(swap[2])

	def _updateCPU(self, interval=0.1):
		"""_updateCPU() -> void

		Updates the system's cpu stats.

		"""
		self._dao.setUsedCPUPercentage( psutil.cpu_percent(interval, True) )
		self._dao.setCPULoadAvg( osGetCPULoadAvg() )
		

	def _updateProcesses(self):
		"""_updateProcesses() -> void

		Updates the set of current running and tasks that have finished and have
		started since the last call to this function.

		"""
		dao = self._dao

		run_procs = frozenset( [ (p.pid, p.name) \
								for p in psutil.process_iter()] )
		old_procs = dao.getRunningProcesses()

		started_procs = run_procs - old_procs if old_procs else frozenset()
		finished_procs = old_procs - run_procs if old_procs else frozenset()

		dao.setRunningProcesses(run_procs)
		dao.setStartedProcesses(started_procs)
		dao.setFinishedProcesses(finished_procs)

	def getSysInfoData(self):
		"""getSystemInfoData() -> SysInfoDAO

		Returns the internal reference to the DAO used to store the system
		information.

		"""
		# TODO: Copy?
		return self._dao


## Encapsualte system information data 
class SysInfoDAO:

	def __init__(self):
		self._timestamp = time.gmtime(0) # Time in UTC format

		self._os_name = OS_VERSION
		self._os_version = OS_NAME
		self._cpu_arch = int(math.log(sys.maxsize, 2) + 1)
		self._machine_name = platform.node()
		
		# Virtual memory stats in bytes
		self._total_mem = 0
		self._used_mem = 0
		self._free_mem = 0
		self._avaliable_mem = 0

		# Swap memory stats in bytes
		self._total_swap = 0
		self._used_swap = 0
		self._free_swap = 0

		# CPU stats
		self._cpu_usage_percent = [0] * psutil.NUM_CPUS
		self._cpu_load_avg = (0.0, 0.0, 0.0)

		self._cur_procs = frozenset()
		self._started_procs = frozenset()
		self._finished_procs = frozenset()

	#
	# Getters
	#
	def getTimestamp(self):
		return self._timestamp

	def getMachineName(self):
		return self._machine_name

	def getOSName(self):
		"""getOperatingSystemName() -> str

		Returns the name of the operating system 

		"""
		if OS_NAME: return OS_NAME

	def getOSVersion(self):
		"""getOperatingSystemVersion() -> str

		Returns the version of the operating system

		"""
		if OS_VERSION: return OS_VERSION

	def getCPUArchitecture(self):
		"""getCPUArchitecture() -> int

		Returns the number of bits of the machine architecture.

		"""
		return self._cpu_arch

	def getTotalVirtualMemory(self):
		return self._total_mem

	def getUsedVirtualMemory(self):
		return self._used_mem

	def getFreeVirtualMemory(self):
		return self._free_mem

	def getAvaliableVirtualMemory(self):
		return self._avaliable_mem

	def getVirtualMemory(self):
		"""getVirtualMemory -> (int, int, int ,int)

		Returns a tuple with all the vmemory information in this SysInfoDAO.

		Tupe order: total, used, free, avaliable

		"""
		return (self._total_mem, self._used_mem, self._free_mem, \
			self._avaliable_mem)

	def getTotalSwap(self):
		return self._total_swap

	def getUsedSwap(self):
		return self._used_swap

	def getFreeSwap(self):
		return self._free_swap

	def getSwapMemory(self):
		"""getVirtualMemory -> (int, int, int ,int)

		Returns a tuple with all the swap information in this SysInfoDAO.

		Tupe order: total, used, free

		"""
		return (self._total_swap, self._used_swap, self._free_swap)

	def getUsedCPUPercentage(self):
		return self._cpu_usage_percent

	def getCPULoadAvg(self):
		"""getCPUAverageLoad() -> (float, float, float)

		Returns the number of processes in the system run queue averaged over
		the last 1, 5 and 15 minutes.

		"""
		return self._cpu_load_avg

	def getRunningProcesses(self):
		return self._cur_procs

	def getStartedProcesses(self):
		return self._started_procs

	def getFinishedProcesses(self):
		return self._finished_procs

	#
	# Setters
	#
	def setTimestamp(self, tstamp):
		util.assertType(tstamp, time.struct_time, "Expected struct_time")
		self._timestamp = tstamp

	def setMachineName(self, name):
		util.assertType(name, str, "Expected string value")
		self._machine_name = name

	def setOSName(self, os_name):
		util.assertType(os_name, str, "Expected string value")
		self._os_name = os_name

	def setOSVersion(self, os_version):
		util.assertType(os_version, str, "Expected string value")
		self._os_version = os_version

	def setCPUArchitecture(self, arch):
		"""getCPUArchitecture(arch: int|long)

		Sets the CPU architecture. 'arch' is the number of bits of the architecture

		"""
		util.assertType(arch, int, "Expected int value")
		self._cpu_arch = arch

	def setTotalVirtualMemory(self, mem): 
		util.assertType(mem, (int, long), "Expected integer value")
		self._total_mem = mem
		
	def setUsedVirtualMemory(self, mem):
		util.assertType(mem, (int, long), "Expected integer value")
		self._used_mem = mem

	def setFreeVirtualMemory(self, mem):
		util.assertType(mem, (int, long), "Expected integer value")
		self._free_mem = mem

	def setAvaliableVirtualMemory(self, mem):
		util.assertType(mem, (int, long), "Expected integer value")
		self._avaliable_mem = mem

	def setTotalSwapMemory(self, mem):
		util.assertType(mem, (int, long), "Expected integer value")
		self._total_swap = mem

	def setUsedSwapMemory(self, mem):
		util.assertType(mem, (int, long), "Expected integer value")
		self._used_swap = mem

	def setFreeSwapMemory(self, mem):
		util.assertType(mem, (int, long), "Expected integer value")
		self._free_swap = mem

	def setUsedCPUPercentage(self, cpu_usage):
		util.assertContainsType(cpu_usage, float, \
			"Expected floating point numbers")

		self._cpu_usage_percent = tuple( used for used in cpu_usage )

	def setCPULoadAvg(self, cpu_load):
		util.assertContainsType(cpu_load, float, \
			"Expected floating point numbers")
		if len(cpu_load) != 3:
			raise Exception("Expected a tuple of 3 float values")

		self._cpu_load_avg = cpu_load

	def setRunningProcesses(self, procs):
		util.assertAttribute(procs, '__iter__', "Expected procs to be iterable")

		if isinstance(procs, frozenset):
			self._cur_procs = procs
		else:
			self._cur_procs = frozenset(procs)

	def setStartedProcesses(self, procs):
		util.assertAttribute(procs, '__iter__', "Expected procs to be iterable")

		if isinstance(procs, frozenset):
			self._started_procs = procs
		else:
			self._started_procs = frozenset(procs)

	def setFinishedProcesses(self, procs):
		util.assertContainsType(procs, tuple, "Expected tuples (int, str)")

		if isinstance(procs, frozenset):
			self._finished_procs = procs
		else:
			self._finished_procs = frozenset(procs)
#
#
if __name__ == '__main__':

	import time

	sinfo = SysInfo()
	sinfo.update()
	dao = sinfo.getSysInfoData()

	time.sleep(1)

	sinfo.update()

	print "Timestamp:", dao.getTimestamp()
	print
	print "Machine name:", dao.getMachineName()
	print "Operating System:", dao.getOSName(), dao.getOSVersion()
	print
	print "Virtual Memory"
	print "\tTotal:", dao.getTotalVirtualMemory()
	print "\tUsed:", dao.getUsedVirtualMemory()
	print "\tFree:", dao.getFreeVirtualMemory()
	print "\tAvaliable:", dao.getAvaliableVirtualMemory()
	print
	print "Swap Memory (total, used, free)"
	print "\tTotal:", dao.getTotalSwap()
	print "\tUsed:", dao.getUsedSwap()
	print "\tFree:", dao.getFreeSwap()
	print
	print "CPU (", dao.getCPUArchitecture(), "bits )"
	print "\tUsage:", dao.getUsedCPUPercentage(), "%"
	print "\tAvg Load:", dao.getCPULoadAvg()
	print
	# print "Finished processes:"
	# for t in dao.getStartedProcesses():
	# 	print "\t", t
	# print
	# print 'Started processes:'
	# for t in dao.getFinishedProcesses():
	# 	print "\t", t
	# print
	# print 'Running processes:'
	# for t in dao.getRunningProcesses():
	# 	print "\t", t
