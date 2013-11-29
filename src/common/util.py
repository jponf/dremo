#
# -*- coding: utf-8 -*-


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