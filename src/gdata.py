#
# -*- coding: utf-8 -*-

# 
SOCK_MIN_PORT = 512
SOCK_MAX_PORT = 49152

# Greeting messages client/server 
SOH = '%c' % 0x1
STX = '%c' % 0x2
ETX = '%c' % 0x3
BEL = '%c' % 0x7

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
K_OK = '200'
K_ERR = '500'
K_ERR_MONITOR_NOT_FOUND = '501'
K_ERR_MONITOR_UNREACHABLE = '502'
K_ERR_BAD_MESSAGE = '503'
K_ERR_TIMEOUT = '504'



# Command line options
# --------------------
import argparse
import logging
import sys

options = None

#
#
def initSrvCommandLineOptions(cmd_line_options, version):
	"""initSrvCommandLineOptions(cmd_line_options: [str], version: int) -> void

	Initializes the server options using the given cmd_line_options and makes 
	them accessible throug getCommandLineOptions()

	"""
	global options

	parser = argparse.ArgumentParser(
				usage=globals()['__doc__'],
				version=version,
				description='Remote resource monitoring tool client')

	parser.add_argument('-ip', default='0.0.0.0', 
				help='server listen interface ip')

	parser.add_argument('-mon_port', default=6666, type=int,
				help='monitors listen port')

	parser.add_argument('-cli_port', default=6665, type=int,
				help='clients listen port')

	parser.add_argument('-cto', '--connection-timeout', default=3, type=float,
				help='client connection timeout')

	parser.add_argument('-cqs', '--connection-queue-size', default=100, 
				type=int, help="")

	parser.add_argument('-mg', '--multicast-group', default='227.123.456.789',
				help='multicast group ip')

	parser.add_argument('-mgp', '--multicast-group-port', default=7777,
				type=int, help='multicast group port')

	parser.add_argument('-mgttl', '--multicast-group-ttl', type=int, default=16,
				help='multicast group packets ttl')

	parser.add_argument('-dlt', '--data-life-time', type=float, default=10.0,
				help='monitors data life time before discard it')

	parser.add_argument('-lf', '--logfile', type=argparse.FileType('a'),
				default=sys.stderr, 
				help='Logging file (default [stderr])')

	parser.add_argument('-d', '--debug', action='store_true', default=False,
				help='sets the loggin leve to DEBUG')

	options = parser.parse_args(cmd_line_options)

	if options.data_life_time < options.connection_timeout * 2:
		logging.critical(
			"Data life time must be at least twice the connection life time")
		sys.exit(-1)

#
#
def getCommandLineOptions():
	if options:
		return options

	raise Exception("Must call initCommandLineOptions() before get the options")