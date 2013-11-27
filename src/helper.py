# -*- coding: utf-8 -*-

# Imports
# -------

import gdata

def isCmdGreeting(msg):
	"""isCmdGreeting(msg: str) -> bool

	Tests if the message is the command "GREETING".

	"""
	return msg.lower() == gdata.CMD_GREETING.lower()

def isCmdQuit(msg):
	"""isCmdQuit(msg: str) -> bool

	Tests if the message is the command "QUIT"

	"""
	return msg.lower() == gdata.CMD_QUIT.lower()

def isBEL(msg):
	"""isNewMonitor(msg: str) -> bool

	Tests if the message is the one sended by a new monitor.

	"""
	return msg == gdata.BEL

def isSOH(msg):
	"""isStartOfHead(msg: str) -> bool

	Tests if the message is the start of a monitor message header.

	"""
	return msg == gdata.SOH

def getOkMessage(msg = ''):
	"""getOkMessage(msg = '') -> str

	Returns a ok message with the given text.

	"""
	return ("%s OK\n%s\n" % (gdata.K_OK, msg))

def getGenericError(msg = ''):
	"""getGenericError(msg = '') -> str

	Returns a generic error message with the given text.

	"""
	return ("%s %s\n" % (gdata.K_ERR, msg))

def getMonitorNotFoundError(msg = ''):
	"""getMonitorNotFoundError(msg = '') -> str

	Returns a monitor not found error message with the given text.

	"""
	return ("%s %s\n" % (gdata.K_ERR_MONITOR_NOT_FOUND, msg))

def getMonitorUnreachableError(msg = ''):
	"""getMonitorNotFoundError(msg = '') -> str

	Returns a monitor unreachable error message with the given text.

	"""
	return ("%s %s\n" % (gdata.K_ERR_MONITOR_UNREACHABLE, msg))

def getBadMessageError(msg = ''):
	"""getMonitorNotFoundError(msg = '') -> str

	Returns a bad message error message with the given text.

	"""
	return ("%s %s\n" % (gdata.K_ERR_BAD_MESSAGE, msg))

def getTimeoutError(msg = ''):
	"""getMonitorNotFoundError(msg = '') -> str

	Returns a timeout error message with the given text.

	"""
	return ("%s %s\n" % (gdata.K_ERR_TIMEOUT, msg))