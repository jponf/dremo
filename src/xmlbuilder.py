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
			'free' : 'free', 'load' : 'load' , 'name' : 'name',
			'memory' : 'memory', 'ram' : 'RAM', 'total' : 'total',
			'swap' : 'swap', 'tasks' : 'tasks', 'add' : 'add', 'del' : 'del', 
			'avaliable' : 'avaliable', 'version' : 'version'
			}

	def setXMLData(self, sysinfo):
		"""setXMLData(sysinfo : SysInfo) -> void

		Sets the data for the XML returned by getXML()

		"""
		tag_names = SysInfoXMLBuilder.tag_names

		timestamp = datetime.now().isoformat().split('T')
		timestamp = timestamp[0] + ' ' + timestamp[1].split('.')[0]

		self.root = etree.Element( tag_names['root'] )

		self._setXMLDescriptiveData(sysinfo)
		self._setXMLCPUData(sysinfo)
		self._setMemoryData(sysinfo)

	def getAsString(self):
		"""getAsString() -> str

		Returns the xml filled with the previous given data as a string.

		"""

		if self.root:
			return etree.tostring(self.root, "utf-8")

		raise Exception('There is no data to create the XML')

		#tasklist = LIST OF TASKS
		# tasks = tree.SubElement(root, tag_names['tasks'])
		# for task in tasklist:
		# 	if task not in prevTasks:
		# 		toAdd = tree.SubElement(tasks, tag_names['add']) 
		# 		toAdd.text(str(task))
		# for task in prevTasks:
		# 	if task not in tasklist:
		# 		toRemove = tree.SubElement(tasks, tag_names['del'])
		# 		toRemove.text(str(task))

		# prevTasks = tasklist

	def _setXMLDescriptiveData(self, sinfo):
		# Sets descriptive data such as operating system name
		# machine name, ...
		tag_names = SysInfoXMLBuilder.tag_names

		os = etree.SubElement( self.root, tag_names['os'] )
		etree.SubElement( os, tag_names['name'] ).text = sinfo.getOSName()
		etree.SubElement( os, tag_names['version']).text = sinfo.getOSVersion()
		

	def _setXMLCPUData(self, sinfo):
		# Sets cpu data
		tag_names = SysInfoXMLBuilder.tag_names

		cpu = etree.SubElement( self.root, tag_names['cpu'] )
		etree.SubElement( cpu, tag_names['arch'] ).text = \
			str(sinfo.getCPUArchitecture())
		etree.SubElement( cpu, tag_names['load'] ).text = "LOADHERE"
		etree.SubElement( cpu, tag_names['model'] ).text = "MODELHERE"

		for cpu_usage in map(str, sinfo.getCPUPercentage()):
			etree.SubElement( cpu, tag_names['used'] ).text = cpu_usage


	def _setMemoryData(self, sinfo):
		# Sets memory data
		tag_names = SysInfoXMLBuilder.tag_names

		memory = etree.SubElement( self.root, tag_names['memory'] )
		ram = etree.SubElement( memory, tag_names['ram'] )
		swap = etree.SubElement( memory, tag_names['swap'] )

		vmem = map(str, sinfo.getVirtualMemoryInfo())
		etree.SubElement( ram, tag_names['total'] ).text = vmem[0] 
		etree.SubElement( ram, tag_names['used'] ).text = vmem[1]
		etree.SubElement( ram, tag_names['free'] ).text = vmem[2]
		etree.SubElement( ram, tag_names['avaliable'] ).text = vmem[3]

		smem = map(str, sinfo.getSwapMemoryInfo())
		etree.SubElement( swap, tag_names['total'] ).text = smem[0]
		etree.SubElement( swap, tag_names['used'] ).text = smem[1]
		etree.SubElement( swap, tag_names['free'] ).text = smem[2]


#
#
if __name__ == '__main__':

	import sysinfo

	sinfo = sysinfo.SysInfo()
	sinfoXML = SysInfoXMLBuilder()

	sinfo.updateMemory()
	sinfo.updateCPU()
	sinfo.updateProcesses()

	sinfoXML.setXMLData(sinfo)
	print sinfoXML.getAsString()



		


	