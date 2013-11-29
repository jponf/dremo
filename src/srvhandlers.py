# -*- coding: utf-8 -*-

# Imports
# -------

import gdata
import common
import helper
import socket
import srvdata
import logging
import threading


# Classes
# -------

class ThreadWithRegister(threading.Thread):

    _reg_lock = threading.RLock()
    _reg = set()

    @staticmethod
    def _registerThread(cls, thread):
        cls._reg_lock.acquire()
        cls._reg.add(thread)
        cls._reg_lock.release()

    @staticmethod
    def _unregisterThread(cls, thread):
        cls._reg_lock.acquire()
        cls._reg.remove(thread)
        cls._reg_lock.release()

    @staticmethod
    def _waitAll(cls):
        cls._reg_lock.acquire()

        while len(cls._reg) > 0:
            rt = cls._reg.pop()
            cls._reg.add(rt)
            cls._reg_lock.release()
            rt.join()

            cls._reg_lock.acquire()
            if len(cls._reg) == 0:
                cls._reg_lock.release()
                break
#
#
class MonitorHandler(ThreadWithRegister):

    def __init__(self, sock, timeout):
        super(MonitorHandler, self).__init__()
        self.sock = sock
        self.timeout = timeout
        self.addr = sock.getpeername()  # Save socket address

    def run(self):
        """run() -> void

        Handles the communication events and errors with a resource monitor.

        """
        MonitorHandler._registerThread(MonitorHandler, self)
        sock = self.sock
        sock.settimeout( self.timeout )

        try:
            data = common.recvEnd(sock, gdata.ETX)

            if data:
                logging.debug("%s:%d Data:\n%s" % (self.addr[0], self.addr[1],
                                                    data))
                head, sep, body = data.partition(' ')
                head = head.strip()
                body = body.strip()

                if helper.isBEL(head):      # New monitor
                    self._newMonitor(body)
                elif helper.isSOH(head):    # Monitor data update
                    self._updateMonitor(body)
                else:                       # Unknown data
                    logging.info("Unknown monitor message '%s' from %s:%d" %
                                    (data, self.addr[0], self.addr[1]) )
                    sock.sendall( helper.getBadMessageError("Wrong message") )

        except socket.timeout:
            logging.debug("Socket TIMEOUT %s:%d" % self.addr)
            sock.sendall( helper.getTimeoutError(
                            "Reached timeout of %.1f seconds" % self.timeout) 
                        )
        except AttributeError, e:
            sock.sendall( helper.getGenericError(str(e)) )
        except ValueError, e:
            sock.sendall( helper.getGenericError(str(e)) )
        except IOError, e:
            logging.warning("Error sending data to (%s:%d)" 
                % self.addr)
        finally:
            sock.close()
            logging.debug("Monitor handler closed socket to %s:%s" % self.addr)
            MonitorHandler._unregisterThread(MonitorHandler, self)

    def _newMonitor(self, port):
        
        iport = int(port)
        if iport < gdata.SOCK_MIN_PORT or iport > gdata.SOCK_MAX_PORT:
            raise ValueError("Port value (%d) out of range [%d-%d]" 
                % (iport, gdata.SOCK_MIN_PORT, gdata.SOCK_MAX_PORT))

        mid = srvdata.initializeNewMonitorData(self.addr[0], port)

        opt = gdata.getCommandLineOptions()
        msg = helper.getOkMessage(
                "",
                "%s %s %d" 
                % (mid, opt.multicast_group, opt.multicast_group_port)
            )

        self.sock.sendall(msg)

        self._updateMonitor(mid)

    def _updateMonitor(self, mid):
        
        if srvdata.existsMonitorData(mid):
            srvdata.keepAliveMonitor(mid)

            data = common.recvEnd(self.sock, gdata.ETX).strip()
            #logging.debug("%s:%d Data:\n%s" % (self.addr[0], self.addr[1], data))

            infoparser = common.SysInfoXMLParser()
            infoparser.parseXML(data)
            infodao = infoparser.getSysInfoData()
            srvdata.updateMonitorData(mid, infodao)
            self.sock.sendall( helper.getOkMessage("Update successful") )                   
            logging.debug("Update %s successful" % mid)
        else:
            self.sock.sendall( 
                helper.getMonitorNotFoundError(
                    "There isn't any monitor with id: %s" % mid)
                )

    @staticmethod
    def waitAll():
        MonitorHandler._waitAll(MonitorHandler)

#
#
class CommandHandler(ThreadWithRegister):
    
    def __init__(self, sock, m_sock, mg_ip, mg_port, timeout):
        super(CommandHandler, self).__init__()
        self.sock = sock
        self.m_sock = m_sock
        self.mg_ip = mg_ip
        self.mg_port = mg_port
        self.timeout = timeout
        self.addr = sock.getpeername()


    def run(self):
        """run() -> void

        Handles the communication events and errors with a client.

        """
        CommandHandler._registerThread(CommandHandler, self)
        sock = self.sock
        sock.settimeout(self.timeout)

        try:
            while True:
                data = common.recvEnd(sock, '\n')
                # Connection closed
                if not data: break

                data = data.strip()

                if helper.isCmdQuit(data):          # QUIT
                    break

                elif helper.isCmdList(data):        # LIST
                    self._sendMonitorsList()

                elif helper.isCmdGetAll(data):      # GET ALL
                    self._sendGetAll()

                elif helper.isCmdUpdateAll(data):   # UPDATE ALL
                    self._sendUpdateAll()

                else:
                    cmd, sep, body = data.partition(' ')
                    body = body.strip()

                    if helper.isCmdGet(cmd):        # GET
                        self._handleGet(body)

                    elif helper.isCmdUpdate(cmd):   # UPDATE
                        self._handleUpdate(body)

                    else:
                        logging.info("Unknown command from %s:%d" % self.addr)
                        self.sock.sendall(
                                helper.getUnknownCmdError(
                                "Unknown command: %s" % data)
                            )           

        except socket.timeout:
            logging.debug("Socket TIMEOUT %s:%d" % self.addr)
            sock.sendall( helper.getTimeoutError(
                            "Reached timeout of %.1f seconds" % self.timeout) 
                        )
        except IOError:
            logging.warning("Error sending data to %s:%d" % self.addr)
        finally:
            sock.close()
            logging.debug("Command handler closed socket to %s:%s" % self.addr)
            CommandHandler._unregisterThread(CommandHandler, self)

    def _handleGet(self, mid):

        if srvdata.existsMonitorData(mid):
            sinfodao, ip, port = srvdata.getMonitorData(mid)
            xmlbuilder = common.SysInfoXMLBuilder()
            xmlbuilder.setXMLData(sinfodao)

            data = "IP: %s\nPORT: %s\n%s" % (ip, port, xmlbuilder.getAsString())

            msg = helper.getOkMessage('Data of %s' % mid, data)
            self.sock.sendall( msg )
        else:
            self.sock.sendall( 
                helper.getMonitorNotFoundError(
                    "Monitor %s is not registered" % mid)
                )

    ## Checks if the given monitor id exists and then tries to send the update
    ## message to the monitor
    def _handleUpdate(self, mid):
        if srvdata.existsMonitorData(mid):
            sinfodao, ip, port = srvdata.getMonitorData(mid)
            srvdata.keepAliveMonitor(mid)

            s = None
            try:
                self._sendUpdateToMonitor(ip, port)

            except socket.error:
                logging.debug("Error updating %s:%s" % (ip, port))
                self.sock.sendall(
                        helper.getMonitorUnreachableError(
                            "Error connecting to %s:%s" % (ip, port)
                        )
                    )
            except socket.timeout:
                logging.debug("Timeout updating %s:%s" % (ip, port))
                self.sock.sendall(
                        helper.getMonitorUnreachableError(
                            "Error connecting to %s:%s [Timeout]" % (ip, port)
                        )
                    )
            finally:
                if s: s.close()
        else:
            self.sock.sendall(
                        helper.getMonitorNotFoundError(
                            "Monitor %s does not exists" % mid)
                    )

    ## Sends the update message to the specified ip and port, waits for the
    ## response and propagate the response to the applicant
    def _sendUpdateToMonitor(self, ip, port):
        # Send Update to monitor and get response
        s = socket.create_connection( (ip, port), self.timeout )
        s.sendall("%s\n" % gdata.CMD_UPDATE)

        ret = common.recvEnd(s, '\n').strip()
        code, sep, desc = ret.partition(' ')

        # Send result to client
        msg = None
        if code == gdata.K_OK:
            msg = helper.getOkMessage(desc)
        else:
            msg = helper.getGenericError("Received error: %s" % ret)

        self.sock.sendall(msg)

    ## Generates and sends the response to the message get all
    def _sendGetAll(self):
        mlist = srvdata.getAllMonitorsData()
        xmlbuilder = common.SysInfoXMLBuilder()

        data = []
        for sinfodao, ip, port in mlist:
            xmlbuilder.setXMLData(sinfodao)
            data.append("IP: %s\nPORT: %s\n%s"
                        % (ip, port, xmlbuilder.getAsString()) )

        strdata = '\n'.join(data)
        msg = helper.getOkMessage('Here goes the data', strdata)
        self.sock.sendall( msg )

    ## Sends the update message throug the multicast channel
    def _sendUpdateAll(self):
        logging.debug("Sending update to the mulsticast group %s:%d" 
                        % (self.mg_ip, self.mg_port))

        msg = "%s\n" % gdata.CMD_UPDATE

        snt = self.m_sock.sendto(msg, (self.mg_ip, self.mg_port) )

        if snt == len(msg):
            self.sock.sendall( helper.getOkMessage('Update all sent') )
        else:
            self.sock.sendall( helper.getGenericError(
                                'Error sending to Multicast group'))

    ## Generates and sends a list with all the monitors id's
    def _sendMonitorsList(self):
        mlist = srvdata.getListOfMonitors()
        strlist = '\n'.join(mlist)
        msg = helper.getOkMessage('Here goes the list', strlist)
        self.sock.sendall( msg )

    @staticmethod
    def waitAll():
        CommandHandler._waitAll(CommandHandler)
