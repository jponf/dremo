# -*- coding: utf-8 -*-

# Imports
# -------

import socket
import struct
import logging

# Functions
# ---------

def recvAll(sock):
    """recvEnd(sock) -> received_data[]

    Reads all the data from the socket

    """

    total_data=[];data=''

    while True:
        try:
            data=sock.recv(8192)
            if data:
                total_data.append( data )
            else:
                break
        finally:
            break

    return ''.join(total_data)


def recvEnd(sock, end):
    """recvEnd(sock, end) -> received_data[]

    Reads data from the socket until the 'end' data is received

    """
    total_data='';data=''
    while True:
        try:
            data=sock.recv(1)
            if data:    
                total_data += data
                if total_data.endswith(end):
                    total_data = total_data[:-len(end)]
                    break
            else:
                # No data implies disconnection
                break;
        except Exception, e:
            raise e
        
    return total_data


def createServerTCPSocket(host, port, listen_size):
    """createServerTCPSocket(host: str, port: int, listen_size: int) 
        -> socket.socket

    Creates a new TCP socket, binds it to the specified host and port with a
    queue of size 'listen_size'

    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind( (host, port) )
    sock.listen(listen_size)
    return sock


def createMulticastSocket(port, ttl=1):
    """
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Multicast-friendly
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # more than one sock can use this port
    if hasattr(socket, "SO_REUSEPORT"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    if port:
        sock.bind(('', port))
    
    return sock


def joinMulticastGroup(mcast_sock, group):
    """
    """
    mreq = struct.pack("=4sl", socket.inet_aton(group), socket.INADDR_ANY)
    mcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    logging.debug('Multicast socket joined group %s' % group)


def leaveMulticastGroup(mcast_sock, group):
    """
    """
    mreq = struct.pack("=4sl", socket.inet_aton(group), socket.INADDR_ANY)
    mcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
    logging.debug('Multicast socket leaved group %s' % group)
