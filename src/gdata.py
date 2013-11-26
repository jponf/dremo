#
# -*- coding: utf-8 -*-

# Greeting messages client/server 
SOH = 0x1
STX = 0x2
ETX = 0x3

# Fixed ports
SERVER_PORT = 6666

# Default multicast port
MULTICAST_PORT = 6668
CLIENT_PORT = 6667

# Client/Server commands
CMD_GREETING = 'hello'
CMD_UPDATE = 'update'
CMD_GET = 'get'

# Server commands
CMD_UPDATE_ALL = 'update all'
CMD_GET_ALL = 'get all'
CMD_LIST = 'list'

# Specific direct commands
CMD_QUIT = 'quit'
CMD_HELP = '?'

# Codes
C_OK = 200
C_ERR = 500
C_ERR_CLINET_NOT_FOUND = 501
C_ERR_CLIENT_UNREACHABLE = 502