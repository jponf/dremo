#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import common
import logging
import argparse


__program__ = "DREMO Client"
__version__ = '0.1a'
__author__ = "Josep Pon Farreny, Marc Piñol Pueyo"
__license__ = "MIT"
__status__ = "Development"


def main():
	global options

	setUpLogger()
	logging.info('Logging set up')


def setUpLogger():
	"""setUpLogger(options) -> void

	Sets up the loggin module.

	"""
	global options

	lvl = logging.DEBUG if options.debug else logging.INFO
	#format = '[%(levelname)s] (%(asctime)s): %(message)s'
	format = '[%(levelname)s]: %(message)s'
	datefmt='%d/%m/%Y %H:%M:%S'

	logging.basicConfig(stream = options.logfile, level=lvl, format=format,
						datefmt=datefmt)

#
#
if __name__ == '__main__':

	parser = argparse.ArgumentParser(
				usage=globals()['__doc__'],
				version=__version__,
				description='Remote resource monitoring tool client')

	parser.add_argument('-host', required=True, help='server host name/ip')

	parser.add_argument('-port', required=True, type=int, help='server port')

	parser.add_argument('-lf', '--logfile', type=argparse.FileType('a'),
				default=sys.stderr, 
				help='logging file (default [stderr])')

	parser.add_argument('-d', '--debug', action='store_true', default=False,
				help='sets the loggin leve to DEBUG')

	options = parser.parse_args()

	main()