#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil          # https://code.google.com/p/psutil/wiki/Documentation
import platform

# Determines the operating system in module load time
PYTHON_SYSTEM = platform.system()
OS_IS_OSX = PYTHON_SYSTEM.lower() == 'darwin' and platform.mac_ver()[0]
OS_IS_WIN = PYTHON_SYSTEM.lower() == 'windows'
OS_IS_LINUX = PYTHON_SYSTEM.lower() == 'linux'

OS_NAME = ""
OS_VERSION= ""

if OS_IS_LINUX:
	OS_NAME, OS_VERSION, _ = platform.linux_distribution()

elif OS_IS_OSX:
	OS_NAME = "Mac OS X"
	OS_VERSION, _, _ = platform.mac_ver()

elif OS_IS_WIN:
	OS_NAME = "Windows"
	OS_VERSION, _, _, _ = platform.win32_ver()

# Encapsualte system info data and methods to retrive it
class SysInfo:

	def __init__(self):
		self._machine_name = ""
		
		# Virtual memory stats in bytes
		self._total_mem = 0
		self._used_mem = 0
		self._free_mem = 0
		self._avaliable_mem = 0

		# Swap memory stats in bytes
		self._total_swap = 0
		self._used_swap = 0
		self._free_swap = 0

		self._cpu_usage_percent = [0] * psutil.NUM_CPUS

		self._cur_procs = frozenset()
		self._started_procs = frozenset()
		self._finished_procs = frozenset()

	def updateMemory(self):
		"""updateMemory() -> void

		Updates the system's memory stats.

		"""
		vmem = psutil.virtual_memory()
		self._total_mem = vmem[0]		
		self._avaliable_mem = vmem[1]
		self._free_mem = vmem[2]
		self._used_mem = vmem[3]

		swap = psutil.swap_memory()
		self._total_swap = swap[0]
		self._used_swap = swap[1]
		self._free_swap = swap[2]

	def updateCPU(self, interval=0.1):
		"""updateCPU() -> void

		Updates the system's cpu stats.

		"""
		self._cpu_usage_percent = psutil.cpu_percent(interval, percpu=True)

		# TODO: cpuload

	def updateProcesses(self):
		"""updateProcesses() -> void

		Updates the set of current running and tasks that have finished and have
		started since the last call to this function.

		"""
		cur_procs = frozenset( [ (p.pid, p.name) \
								for p in psutil.process_iter()] )

		self._started_procs = cur_procs - self._cur_procs
		self._finished_procs = self._cur_procs - cur_procs

		self._cur_procs = cur_procs

	def getOperatingSystemName(self):
		"""getOperatingSystemName() -> str

		Returns the name of the operating system 

		"""
		if OS_NAME: return OS_NAME

		raise Exception("Unknown operating system")

	def getOperatingSystemVersion(self):
		"""getOperatingSystemVersion() -> str

		Returns the version of the operating system

		"""
		if OS_VERSION: return OS_VERSION

		return OS_VERSION


	def getCPUPercentage(self):
		"""getCPUPercentage() -> [float]

		Returns a list or tuple filled with the cpu usage (%) at the last call 
		to updateCPU()

		"""
		return self._cpu_usage_percent

	def getVirtualMemoryInfo(self):
		"""getVirtualMemoryInfo() -> (total, used, free, avaliable)

		Returns a tuple with the total memory in the system, the used memory,
		the free memory and the avaliable memory.

		Note: In some systems the avaliable memory is not equals to free memory

		"""
		return (self._total_mem, self._used_mem, self._avaliable_mem, \
			self._free_mem)

	def getSwapMemoryInfo(self):
		"""getSwapMemoryInfo() -> (total, used, swap)

		Returns a tuple with the total swap memory, the used swap memory and 
		the free swap memory.

		"""
		return (self._total_swap, self._used_swap, self._free_swap)

	def getRunningProcesses(self):
		"""getRunningProcesses() -> set<(pid, name)>

		Returns a set filled with processes that were running at the last call
		to updateProcesses().

		"""
		return self._cur_procs

	def getStartedProcesses(self):
		"""getStartedProcesses() -> set<(pid, name)>

		Returns a set filled with the processes whose execution have started
		between two calls to updateProcesses()

		"""
		return self._started_procs

	def getFinishedProcesses(self):
		"""getFinishedProcesses() -> set<(pid, name)>

		Returns a set filled with the processes whose execution have finished
		between two calls to updateProcesses()

		"""
		return self._finished_procs

#
#
if __name__ == '__main__':

	import time

	def updateAllSysInfo(sinfo):
		sinfo.updateMemory()
		sinfo.updateCPU()
		sinfo.updateProcesses()

	sinfo = SysInfo()
	updateAllSysInfo(sinfo)

	time.sleep(5)

	updateAllSysInfo(sinfo)

	print "Operating System:", sinfo.getOperatingSystemName(), \
								sinfo.getOperatingSystemVersion()
	print
	print "Virtual Memory (total, used, free, avaliable)"
	print sinfo.getVirtualMemoryInfo()
	print
	print "Swap Memory (total, used, free)"
	print sinfo.getSwapMemoryInfo()
	print
	print "CPU use percentage"
	print sinfo.getCPUPercentage()
	print
	print "Finished processes:"
	for t in sinfo.getStartedProcesses():
		print "\t", t
	print
	print 'Started processes:'
	for t in sinfo.getFinishedProcesses():
		print "\t", t
	print
	print 'Running processes:'
	for t in sinfo.getRunningProcesses():
		print "\t", t
