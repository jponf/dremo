#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sysinfo

import xml.etree.cElementTree as etree
from xml.etree.cElementTree import ParseError

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

attr_names = {
				'name' : 'name', 'timestamp' : 'timestamp'
				}

timestamp_format = "%d/%m/%Y %H:%M:%S %Z"

#
#
class SysInfoXMLBuilder():

	

	def setXMLData(self, sinfodao):
		"""setXMLData(sysinfo : SysInfo) -> void

		Sets the data for the XML returned by getXML()

		"""
		self.root = etree.Element( tag_names['root'] )

		self._setXMLDescriptiveData(sinfodao)
		self._setXMLOSData(sinfodao)
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
		# Sets descriptive machine name and timestamp
		timestamp = time.strftime(timestamp_format, dao.getTimestamp())

		# Client name and data timestamp
		self.root.set(attr_names['name'], dao.getMachineName())
		self.root.set(attr_names['timestamp'], timestamp)

	def _setXMLOSData(self, dao):
		# Sets Operating system information
		os = etree.SubElement( self.root, tag_names['os'] )
		etree.SubElement( os, tag_names['name'] ).text = dao.getOSName()
		etree.SubElement( os, tag_names['version']).text = dao.getOSVersion()

	def _setXMLCPUData(self, dao):
		# Sets cpu data

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

		processes = etree.SubElement( self.root, tag_names['processes'] )

		for p in dao.getRunningProcesses():
			rp = etree.SubElement( processes, tag_names['running'] )
			rp.set(attr_names['name'], p[1])
			rp.text = str(p[0])

		for p in dao.getStartedProcesses():
			sp = etree.SubElement( processes, tag_names['started'] )
			sp.set(attr_names['name'], p[1])
			sp.text = str(p[0])

		for p in dao.getFinishedProcesses():
			fp = etree.SubElement( processes, tag_names['finished'] )
			fp.set(attr_names['name'], p[1])
			fp.text = str(p[0])

#
#
class SysInfoXMLParser:
	
	def __init__(self):
		self._dao = sysinfo.SysInfoDAO()

	def parseXML(self, xml_string):
		"""parseXML() -> void

		Parses the data directly of the given xml string. 

		Raises an Exception if the xml can't be understood.

		Warning: Does not detect extra data mixed with the xml.

		"""
		try:
			root = etree.fromstring(xml_string)
			dao = sysinfo.SysInfoDAO()			# Work over isolated DAO

			self._parseDescriptiveData(dao, root)
			self._parseOSData(dao, root)
			self._parseCPUData(dao, root)
			self._parseMemoryData(dao, root)
			self._parseProcessesData(dao, root)

			self._dao = dao # Once the data is consistend store the new DAO
		except ParseError, e:
			raise AttributeError(str(e))


	def getSysInfoData(self):
		"""getSystemInfoData() -> SysInfoDAO

		Returns the internal reference to the DAO used to store the system
		information.

		"""
		return self._dao

	def _parseDescriptiveData(self, dao, root):
		
		try:
			timestamp = root.attrib[ attr_names['timestamp'] ]
			timestamp = time.strptime(timestamp, timestamp_format)

			dao.setMachineName(root.attrib[ attr_names['name'] ])
			dao.setTimestamp(timestamp)

		except KeyError, e:
			raise AttributeError("Missing XML name or timestamp attributes")
		
	def _parseOSData(self,dao, root):
		# Parses data between os tags
		os = root.find( tag_names['os'] )
		name = ""
		version = ""

		if os:
			name_el = os.find( tag_names['name'] )
			version_el = os.find( tag_names['version'] )
			
			if name_el != None and version_el != None:
				name = name_el.text.strip()
				version = version_el.text.strip()
			else:
				raise AttributeError("Missing XML OS name or version")
		else:
			raise AttributeError("Missing XML tag: Operating System")

		dao.setOSName(name)
		dao.setOSVersion(version)

	def _parseCPUData(self, dao, root):
		# Parses data between cpu tags
		cpu = root.find( tag_names['cpu'] )

		if cpu:
			arch_el = cpu.find( tag_names['arch'] )
			#model_el = cpu.find( tag_names['model'] )
			load1_el = cpu.find( tag_names['load1'] )
			load5_el = cpu.find( tag_names['load5'] )
			load15_el = cpu.find( tag_names['load15'] )
			used_el = cpu.findall( tag_names['used'] )

			if arch_el != None:				
				dao.setCPUArchitecture( int(arch_el.text) )
			else:
				raise AttributeError("Missing XML tag: CPU architecture")

			if load1_el != None and load5_el != None and load15_el != None:
				load = ( float(load1_el.text), float(load5_el.text), 
							float(load15_el.text) )
				dao.setCPULoadAvg( load )
			else:
				raise AttributeError("Missing XML tag: CPU load")

			if len(used_el) > 0:
				used = tuple( float(uel.text) for uel in used_el )
				dao.setUsedCPUPercentage( used )

			else:
				raise AttributeError("Missing XML tag: CPU usage")
		else:
			raise AttributeError("Missing XML tag: CPU")


	def _parseMemoryData(self, dao, root):
		# Parses data between memory tags
		mem = root.find( tag_names['memory'] )

		if mem:
			self._parseVirtualMemoryData(dao, mem)
			self._parseSwapMemoryData(dao, mem)
		else:
			raise AttributeError("Missing XML tag: memory")

	def _parseVirtualMemoryData(self, dao, mem):
		# Parses data between virtual memory tags
		main_tag = tag_names['ram']
		vmem = mem.find( main_tag )

		tags_setfunc = ((tag_names['total'], dao.setTotalVirtualMemory),
						(tag_names['used'], dao.setUsedVirtualMemory),
						(tag_names['free'], dao.setFreeVirtualMemory),
						(tag_names['avaliable'], dao.setAvaliableVirtualMemory))

		if vmem:
			for tag, setfunc in  tags_setfunc:
				tag_el = vmem.find(tag)
				if tag_el != None:
					setfunc( int(tag_el.text) )
				else:
					raise AttributeError( "Missing XML tag under %s: %s" % 
										  (main_tag, tag) )
		else:
			raise AttributeError("Missing XML tag: %s" % main_tag)

	def _parseSwapMemoryData(self, dao, mem):
		# Parses data between swap memory tags
		main_tag = tag_names['swap']
		smem = mem.find( tag_names['swap'] )

		tags_setfunc = ((tag_names['total'], dao.setTotalSwapMemory),
						(tag_names['used'], dao.setUsedSwapMemory),
						(tag_names['free'], dao.setFreeSwapMemory) )

		if smem:
			for tag, setfunc in  tags_setfunc:
				tag_el = smem.find(tag)
				if tag_el != None:
					setfunc( int(tag_el.text) )
				else:
					raise AttributeError( "Missing XML tag under %s: %s" % 
										  (main_tag, tag) )
		else:
			raise AttributeError("Missing XML tag: %s" % main_tag)

	def _parseProcessesData(self, dao, root):
		# Parses data between processes tags
		main_tag = tag_names['processes']
		processes = root.find(main_tag)

		if processes != None:
			self._parseProcessesDataSubElements(processes, tag_names['running'],
													dao.setRunningProcesses )
			self._parseProcessesDataSubElements(processes, tag_names['started'],
													dao.setStartedProcesses )
			self._parseProcessesDataSubElements(processes, tag_names['finished'],
													dao.setFinishedProcesses )
		else:
			raise AttributeError("Missing XML tag: %s" % main_tag)

	def _parseProcessesDataSubElements(self, processes, subtag, setfunc):
		proc_el = processes.findall(subtag)

		name_attr = attr_names['name']

		procs = frozenset(
				[ (int(prel.text), prel.attrib[name_attr]) for prel in proc_el])
		setfunc(procs)



#
#
if __name__ == '__main__':

	sinfo = sysinfo.SysInfo()
	sinfoXML = SysInfoXMLBuilder()
	sinfoParser = SysInfoXMLParser()

	sinfo.update()
	odao = sinfo.getSysInfoData()

	sinfoXML.setXMLData(odao)
	sinfoParser.parseXML(sinfoXML.getAsString())

	ndao = sinfoParser.getSysInfoData()

	print "Match timestamp:", odao.getTimestamp() == ndao.getTimestamp()
	print "Match client name:", odao.getMachineName() == ndao.getMachineName()
	print "Match os name:", odao.getOSName() == ndao.getOSName()
	print "Match os version:", odao.getOSVersion() == ndao.getOSVersion()
	print "Match cpu arch:", odao.getCPUArchitecture() == ndao.getCPUArchitecture()
	print "Match cpu load avg:", odao.getCPULoadAvg() == ndao.getCPULoadAvg()
	print "Match cpu usage %:", odao.getUsedCPUPercentage() == ndao.getUsedCPUPercentage()
	print "Match virtual mem:", odao.getVirtualMemory() == ndao.getVirtualMemory()
	print "Match swap mem:", odao.getSwapMemory() == ndao.getSwapMemory()
	print "Match running procs:", odao.getRunningProcesses() == ndao.getRunningProcesses()
	print "Match started procs:", odao.getStartedProcesses() == ndao.getStartedProcesses()
	print "Match finished procs:", odao.getFinishedProcesses() == ndao.getFinishedProcesses()

