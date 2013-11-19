#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import platform
import time

#
#
class SysInfoPosix(threading.Thread):

	SYS_INFO_DIR = '/proc'
	MEMORY_FILE = SYS_INFO_DIR + '/meminfo'
	CPU_FILE = SYS_INFO_DIR + '/cpuinfo'
	PROCESSORS = 'Processors'
	VMEMORY_TOTAL = 'MemTotal'
	VMEMORY_FREE = 'MemFree'
	SMEMORY_TOTAL = 'SwapTotal'
	SMEMORY_FREE = 'SwapFree'

	DEF_UDPATE_TIME = 1 		# second(s)
	
	def __init__(self):
		# Init thread
		super(SysInfoPosix, self).__init__()

		# System information
		self._sysinfo = {}
		
		# Thread control
		self._updateTime = SysInfoPosix.DEF_UDPATE_TIME
		self._enabled = False
		self._opLock = threading.RLock()
		self._flagLock = threading.RLock()


	def getComputerName(self):
		""" getComputerName() -> str
	
		Returns the computer's name

		"""
		return platform.node()

	def getSystemName(self):
		""" getSystemName() -> str

		Returns the name of the O.S, e.g: Linux, Windows, ...

		"""
		return platform.system()
		
	def getOsArchitecture(self):
		""" getOsArchitecture() -> str

		Returns the O.S architecture, 64bit, 32bit, ...

		"""
		return platform.architecture()[0]
	
	def getTotalMemory(self):
		""" getTotalMemory() -> int
	
		Returns the system's total memory
	
		"""
		return self._sysinfo[SysInfoPosix.VMEMORY_TOTAL]
		
	def getFreeMemory(self):
		""" getFreeMemory() -> int
	
		Returns the system's free memory
	
		"""
		return self._sysinfo[SysInfoPosix.VMEMORY_FREE]  
	  
	def getUsedMemory(self):
		""" getUsedMemory() -> int
	
		Returns the system's used memory
		
		"""
		return self.getTotalMemory() - self.getFreeMemory()
		
	def getTotalSwap(self):
		""" getTotalSwap() -> int
	
		Returns the system's total swap
		
		"""
		return self._sysinfo[SysInfoPosix.SMEMORY_TOTAL]
		
	def getFreeSwap(self):
		""" getFreeSwap() -> int
	
		Returns the system's free swap
	
		"""
		return self._sysinfo[SysInfoPosix.SMEMORY_FREE]
	
	def getUsedSwap(self):
		""" getFreeSwap() -> int
	
		Returns the system's used swap
	
		"""
		return self.getTotalSwap() - self.getFreeSwap()
		
	def getCpu(self):
		pass

	def getCpuUse(self):
		pass

	def getCpuLoad(self):
		pass

	def getRunningTasks(self):
		pass


	def _read_meminfo(self):    
		with open(SysInfoPosix.MEMORY_FILE) as f:
			for line in f:
				key, value = line.split(':')
				self._sysinfo[key] = int(value.split()[0])

	def _read_cpuinfo(self):
		cpu_info_lst = []
		cpu_info = {}
	
		with open(SysInfoPosix.CPU_FILE) as f:
			for line in f:
				 if not line.strip():
					 cpu_info_lst.append(cpu_info)
					 cpu_info = {}
				 else:
					 lvalues = line.split(':')
					 if len(lvalues) == 2:
						 cpu_info[lvalues[0].strip()] = lvalues[1].strip()
					 else:
						 cpu_info[lvalues[0].strip()] = ''
						 
			if cpu_info:
				cpu_info_lst.append(cpu_info)
			  
		self._sysinfo[SysInfoPosix.PROCESSORS] = cpu_info_lst

	#
	# Thread helpers
	#
	
	def startAtomicOperations(self):
		""" startAtomicOperations() -> void

		Blocks the thread to allow atomic operations on the collected 
		information

		WARNING: Must be followed by a call to endAtomicOperations()

		"""
		self._opLock.acquire()

	def endAtomicOperations(self):
		""" endAtomicOperations() -> void

		Releases the thread

		"""
		self._opLock.release()

	def stop(self):
		""" stop() -> void

		Sets the thread stop flag and waits until it finally finishes

		"""
		self._flagLock.acquire()
		self._enabled = False
		self._flagLock.release()	
		self.join()

	def getUpdateTime(self):
		""" getUpdateTime() -> void

		Gets the time between updates. This is an atomic operation it is not
		altered during its call by setUpdateTime or internal thread operations

		"""
		self._flagLock.acquire()
		ut = self._updateTime
		self._flagLock.release()
		return ut

	def setUpdateTime(self, uptime_sec):
		""" setUpdateTime() -> void

		Sets the new time between updates.

		Atomic operation see getUpdateTime.

		"""
		self._flagLock.acquire()
		self._updateTime = uptime_sec
		self._flagLock.release()

	#
	# Override Thread
	#

	def start(self):
		self._read_cpuinfo()	# Only once
		self._read_meminfo()

		if not self.isAlive():
			super(SysInfoPosix, self).start()

	def isAlive(self):
		return self._enabled and super(SysInfoPosix, self).isAlive()

	def run(self):
		self._enabled = True

		while self._enabled:
			self.startAtomicOperations()
			
			self._read_meminfo()

			self.endAtomicOperations()

			sleepTime = self.getUpdateTime()
			time.sleep(sleepTime)



   
########################################################################################    
#     import os
# pids= [pid for pid in os.listdir('/proc') if pid.isdigit()]

# for pid in pids:
#     print open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()

#
#
if __name__ == '__main__':

	sip = SysInfoPosix()

	sip.start()

	sip.startAtomicOperations()	
	print 'System:', sip.getSystemName()
	print 'Architecture:', sip.getOsArchitecture()
	print 'Computer Name:', sip.getComputerName()
	print
	print 'Total Memory:', sip.getTotalMemory(), 'kB'
	print 'Free Memory:', sip.getFreeMemory(), 'kB'
	print 'Used Memory:', sip.getUsedMemory(), 'kB'
	print
	print 'Total Swap:', sip.getTotalSwap(), 'kB'
	print 'Free Swap:', sip.getFreeSwap(), 'kB'
	print 'Used Swap:', sip.getUsedSwap(), 'kB'
	sip.endAtomicOperations()

	i = 0

	while sip.isAlive():
		sip.startAtomicOperations()

		print
		print 'Free Memory:', sip.getFreeMemory(), 'kB'
		print 'Used Memory:', sip.getUsedMemory(), 'kB'
		print
		print 'Free Swap:', sip.getFreeSwap(), 'kB'
		print 'Used Swap:', sip.getUsedSwap(), 'kB'
		print 
		print i

		sip.endAtomicOperations()


		if i >= 10:
			sip.stop()
		else:
			i+=1
			time.sleep(sip.getUpdateTime())		