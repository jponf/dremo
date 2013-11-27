# -*- coding: utf-8 -*-

# Imports
# -------

import gdata
import select
import logging
import srvhandlers

# Global variables
# ----------------

def mainLoop(mon_sock, cli_sock, m_sock):
	
	opt = gdata.getCommandLineOptions()

	insocks = set([mon_sock, cli_sock])

	logging.info("Server running press Ctrl+C to Quit!")

	try:
		while True:
			i, o , e = select.select(insocks, [], [])

			for s in i:
				t = None
				if s is mon_sock:
					t = srvhandlers.MonitorHandler(sock, opt.timeout)
				else:
					pass # Same as above with ClientHandler

	except KeyboardInterrupt:
		logging.info("Finishing due to KeyboardInterrupt")
	finally:
		logging.info("Waiting threads termination")
		waitThreads()
		logging.info("All threads terminated")




def waitThreads():
	srvhandlers.MonitorHandler.waitAll()
	srvhandlers.CommandHandler.waitAll()