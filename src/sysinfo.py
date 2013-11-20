#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil          # https://code.google.com/p/psutil/wiki/Documentation
import platform

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

		self._cur_tasks = set()
		self._started_tasks = set()
		self._finished_tasks = set()

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

	def updateRunningTasks(self):
		"""updateCPU() -> void

		Updates the set of current running and tasks that have finished and have
		started since the last call to this function.

		"""
		cur_tasks = set(psutil.process_iter())

		self._started_tasks = cur_tasks - self._cur_tasks
		self._finished_tasks = self._cur_tasks - cur_tasks

		self._cur_tasks = cur_tasks

#
#
if __name__ == '__main__':

	import time

	def updateAllSysInfo(sinfo):
		sinfo.updateMemory()
		sinfo.updateCPU()
		sinfo.updateRunningTasks()

	sinfo = SysInfo()
	updateAllSysInfo(sinfo)

	time.sleep(5)

	updateAllSysInfo(sinfo)

	print "Finished tasks:"
	for t in sinfo._finished_tasks:
		print "\t", t

	print 'Started tasks:'
	for t in sinfo._started_tasks:
		print "\t", t
