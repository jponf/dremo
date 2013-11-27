# -*- coding: utf-8 -*-

# Imports
# -------

import gdata

def isCmdGreeting(msg):
	return msg.lower() == gdata.CMD_GREETING.lower()

def isCmdQuit(msg):
	return msg.lower() == gdata.CMD_QUIT.lower()

def isNewMonitor(msg):
	return msg == gdata.BEL

def isStartOfHead(msg):
	return msg == gdata.SOH

def getOkMessage(msg = ''):
	return ("%s OK\n%s\n" % (gdata.K_OK, msg))

def getGeneralError(msg = ''):
	return ("%s %s\n" % (gdata.K_ERR, msg))

def getMonitorNotFoundError(msg = ''):
	return ("%s %s\n" % (gdata.K_ERR_MONITOR_NOT_FOUND, msg))

def getMonitorUnreachableError(msg = ''):
	return ("%s %s\n" % (gdata.K_ERR_MONITOR_UNREACHABLE, msg))

def getBadMessageError(msg = ''):
	return ("%s %s\n" % (gdata.K_ERR_BAD_MESSAGE, msg))

def getTimeoutError(msg = ''):
	return ("%s %s\n" % (gdata.K_ERR_TIMEOUT, msg))