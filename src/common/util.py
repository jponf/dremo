#
# -*- coding: utf-8 -*-


#
#
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

#
#
def recvEnd(sock, end):
	"""recvEnd(sock, end) -> received_data[]

	Reads data from the socket until the 'end' data is received

	"""
	total_data='';data=''
	while True:
		try:
			data=sock.recv(1)
			if data:	
				if data == end:
					break
				else:
					total_data += data
			else:
				# No data implies disconnection
				break;
		except Exception, e:
			raise e
		
	return total_data

def assertType(var, types, msg):
	"""assertType(var, types, msg) -> void

	Check if var is of any type specified in types, if don't then raises a 
	TypeError exception with the message 'msg'.

	"""
	if not isinstance(var, types):
		raise TypeError(msg);

def assertAttribute(var, attrs, msg):
	"""assertAttribute(var, attrs, msg) -> void

	Tests if var has all the specified attributes, if don't then raises an
	AttributeError with the message 'msg'.

	"""
	if not hasattr(attrs, '__iter__'):
		attrs = (attrs,)

	for attr in attrs:
		if not hasattr(var, attr):
			raise AttributeError(msg)

def assertContainsType(variables, types, msg):
	"""assertContainsType(variables, types, msg) -> void

	Check if all the elements in variables are one of the given types, if don't 
	then raises a TypeError exception with the message 'msg'.

	"""
	assertAttribute(variables, '__iter__', 'Excpeted iterable')
	for v in variables:
		assertType(v, types, msg)