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

def isCmdList(msg):
    """isCmdList(msg: str) -> bool

    Tests if the message is the command "LIST"

    """
    return msg.lower() == gdata.CMD_LIST.lower()

def isCmdGet(msg):
    """isCmdGet(msg: str) -> bool

    Tests if the message is the get command.

    """
    return msg.lower() == gdata.CMD_GET.lower()

def isCmdGetAll(msg):
    """isCmdGet(msg: str) -> bool

    Tests if the message is the get all command.

    """
    return msg.lower() == gdata.CMD_GET_ALL.lower()

def isCmdUpdate(msg):
    """isCmdUpdate(msg) -> bool

    Tests if the message is the update command.

    """
    return msg.lower() == gdata.CMD_UPDATE.lower()

def isCmdUpdateAll(msg):
    """isCmdUpdateAll(msg) -> bool

    Tests if the message is the update all command.

    """
    return msg.lower() == gdata.CMD_UPDATE_ALL.lower()

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

def getOkMessage(ok_desc = '', data = ''):
    """getOkMessage(msg = '') -> str

    Returns a ok message with the given text.

    """
    if data:
        return ("%s OK %s\n%s\n\n" % (gdata.K_OK, ok_desc, data))
    else:
        return ("%s OK %s\n\n" % (gdata.K_OK, ok_desc))

def getErrorMessage(err_code, err_msg):
    """getErrorMessage(err_code: str, err_msg: str) -> str

    Returns a formated error message.

    """
    return ("%s %s\n" % (err_code, err_msg))

def getGenericError(msg = ''):
    """getGenericError(msg = '') -> str

    Returns a generic error message with the given text.

    """
    return getErrorMessage(gdata.K_ERR, msg)

def getMonitorNotFoundError(msg = ''):
    """getMonitorNotFoundError(msg = '') -> str

    Returns a monitor not found error message with the given text.

    """
    return getErrorMessage(gdata.K_ERR_MONITOR_NOT_FOUND, msg)
    
def getMonitorUnreachableError(msg = ''):
    """getMonitorNotFoundError(msg = '') -> str

    Returns a monitor unreachable error message with the given text.

    """
    return getErrorMessage(gdata.K_ERR_MONITOR_UNREACHABLE, msg)
    
def getBadMessageError(msg = ''):
    """getMonitorNotFoundError(msg = '') -> str

    Returns a bad message error message with the given text.

    """
    return getErrorMessage(gdata.K_ERR_BAD_MESSAGE, msg)

def getTimeoutError(msg = ''):
    """getMonitorNotFoundError(msg = '') -> str

    Returns a timeout error message with the given text.

    """
    return getErrorMessage(gdata.K_ERR_TIMEOUT, msg)
    
def getUnknownCmdError(msg = ''):
    """getUnknownCmdError(msg = '') -> str

    Returns an unknown command error message with he given text

    """
    return getErrorMessage(gdata.K_ERR_UNKNOWN_CMD, msg)