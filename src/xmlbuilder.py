#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as tree
from datetime import datetime

#
#
class XMLBuilder():

	names = {'client' : 'client', 'ip' : 'ip', 'os' : 'os', 'cpu' : 'cpu', 'arch' : 'arch', 
			'model' : 'model', 'usage' : 'usage', 'load' : 'load' , 'name' : 'name', 
			'memory' : 'memory', 'ram' : 'ram', 'total' : 'total', 'swap' : 'swap', 
			'tasks' : 'tasks', 'add' : 'add', 'del' : 'del'}

	prevTasks = []

	#
	#
	def getAllInfo():
		timestamp = datetime.now().isoformat().split('T')
		timestamp = timestamp[0] + ' ' + timestamp[1].split('.')[0]

		root = tree.element(names['client'])
		root.set('timestamp', timestamp)

		ip = tree.SubElement(root, names['ip'])
		#ip.text(IPHERE)

		os = tree.SubElement(root, names['os'])
		#os.text(OSHERE)

		cpu = tree.SubElement(root, names['cpu'])
		cpuArch = tree.SubElement(cpu, names['arch'])
		cpuModel = tree.SubElement(cpu, names['model'])
		cpuUsage = tree.SubElement(cpu, names['usage'])
		cpuLoad = tree.SubElement(cpu, names['load'])
		# cpuArch.text(ARCHHERE)
		# cpuModel.text(MODELHERE)
		# cpuUsage.text(USAGEHERE)
		# cpuLoad.text(LOADHERE)

		systemName = tree.SubElement(root, names['name'])

		memory = tree.SubElement(root, names['memory'])
		ram = tree.SubElement(memory, names['ram'])
		swap = tree.SubElement(memory, names['swap'])
		totalRam = tree.SubElement(ram, names['total'])
		ramUsage = tree.SubElement(ram, names['usage'])
		totalSwap = tree.SubElement(swap, names['total'])
		swapUsage = tree.SubElement(swap, names['usage'])
		#totalRam.text(RAMHERE)
		#ramUsage.text(RAMUSHERE)
		#totalSwap.text(SWAPHERE)
		#swapUsage.text(SWAPUSHERE)

		#tasklist = LIST OF TASKS
		# tasks = tree.SubElement(root, names['tasks'])
		# for task in tasklist:
		# 	if task not in prevTasks:
		# 		toAdd = tree.SubElement(tasks, names['add']) 
		# 		toAdd.text(str(task))
		# for task in prevTasks:
		# 	if task not in tasklist:
		# 		toRemove = tree.SubElement(tasks, names['del'])
		# 		toRemove.text(str(task))

		# prevTasks = tasklist

