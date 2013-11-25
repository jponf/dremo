#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as etree
from datetime import datetime

#
#
class SysInfoXMLBuilder():

	tag_names = {
			'root' : 'client', 'ip' : 'ip', 'os' : 'os', 'cpu' : 'cpu',
			'arch' : 'arch', 'model' : 'model', 'used' : 'used',
			'free' : 'free', 'load1' : 'loadavg1' , 'load5' : 'loadavg5', 
			'load15' : 'loadavg15', 'name' : 'name','memory' : 'memory',
			'ram' : 'RAM', 'total' : 'total', 'swap' : 'swap',
			'processes' : 'processes', 'running' : 'running',
			'started' : 'started', 'finished' : 'finished',
			'avaliable' : 'avaliable', 'version' : 'version'
			}

	def setXMLData(self, sinfodao):
		"""setXMLData(sysinfo : SysInfo) -> void

		Sets the data for the XML returned by getXML()

		"""
		tag_names = SysInfoXMLBuilder.tag_names

		timestamp = datetime.now().isoformat().split('T')
		timestamp = timestamp[0] + ' ' + timestamp[1].split('.')[0]

		self.root = etree.Element( tag_names['root'] )

		self._setXMLDescriptiveData(sinfodao)
		self._setXMLCPUData(sinfodao)
		self._setXMLMemoryData(sinfodao)
		self._setXMLProcesessData(sinfodao)

	def getAsString(self):
		"""getAsString() -> str

		Returns the xml filled with the previous given data as a string.

		"""
		if self.root:
			return etree.tostring(self.root, "utf-8")

		raise Exception('There is no data to create the XML')

	def _setXMLDescriptiveData(self, dao):
		# Sets descriptive data such as operating system name
		# machine name, ...
		tag_names = SysInfoXMLBuilder.tag_names

		timestamp = datetime.now().isoformat().split('T')
		timestamp = timestamp[0] + ' ' + timestamp[1].split('.')[0]

		# Client name and data timestamp
		self.root.set('name', dao.getMachineName())
		self.root.set('timestamp', timestamp)

		# Operating system information
		os = etree.SubElement( self.root, tag_names['os'] )
		etree.SubElement( os, tag_names['name'] ).text = dao.getOSName()
		etree.SubElement( os, tag_names['version']).text = dao.getOSVersion()

	def _setXMLCPUData(self, dao):
		# Sets cpu data
		tag_names = SysInfoXMLBuilder.tag_names

		cpu = etree.SubElement( self.root, tag_names['cpu'] )
		etree.SubElement( cpu, tag_names['arch'] ).text = \
			str(dao.getCPUArchitecture())
		etree.SubElement( cpu, tag_names['model'] ).text = "MODELHERE"

		for cpu_usage in map(str, dao.getUsedCPUPercentage()):
			etree.SubElement( cpu, tag_names['used'] ).text = cpu_usage

		# CPU load average over 1, 5 and 15 minutes
		cpu_load = map(str, dao.getCPULoadAvg())
		etree.SubElement( cpu, tag_names['load1'] ).text = cpu_load[0]
		etree.SubElement( cpu, tag_names['load5'] ).text = cpu_load[1]
		etree.SubElement( cpu, tag_names['load15'] ).text = cpu_load[2]

	def _setXMLMemoryData(self, dao):
		# Sets memory data
		tag_names = SysInfoXMLBuilder.tag_names

		memory = etree.SubElement( self.root, tag_names['memory'] )
		ram = etree.SubElement( memory, tag_names['ram'] )
		swap = etree.SubElement( memory, tag_names['swap'] )

		vmem = map(str, dao.getVirtualMemory())
		etree.SubElement( ram, tag_names['total'] ).text = vmem[0]
		etree.SubElement( ram, tag_names['used'] ).text = vmem[1]
		etree.SubElement( ram, tag_names['free'] ).text = vmem[2]
		etree.SubElement( ram, tag_names['avaliable'] ).text = vmem[3]

		smem = map(str, dao.getSwapMemory())
		etree.SubElement( swap, tag_names['total'] ).text = smem[0]
		etree.SubElement( swap, tag_names['used'] ).text = smem[1]
		etree.SubElement( swap, tag_names['free'] ).text = smem[2]

	def _setXMLProcesessData(self, dao):
		# Sets processes data
		tag_names = SysInfoXMLBuilder.tag_names

		processes = etree.SubElement( self.root, tag_names['processes'] )

		for p in dao.getRunningProcesses():
			rp = etree.SubElement( processes, tag_names['running'] )
			rp.set('name', p[1])
			rp.text = str(p[0])

		for p in dao.getStartedProcesses():
			sp = etree.SubElement( processes, tag_names['started'] )
			sp.set('name', p[1])
			sp.text = str(p[0])

		for p in dao.getFinishedProcesses():
			fp = etree.SubElement( processes, tag_names['finished'] )
			fp.set('name', p[1])
			fp.text = str(p[0])

#
#
if __name__ == '__main__':

	import sysinfo

	sinfo = sysinfo.SysInfo()
	sinfoXML = SysInfoXMLBuilder()

	sinfo.updateMemory()
	sinfo.updateCPU()
	sinfo.updateProcesses()

	sinfoXML.setXMLData(sinfo.getSysInfoData())
	print sinfoXML.getAsString()



		


	