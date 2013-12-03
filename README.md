dremo
=====
Simple test of an application to monitorize different machines

## Structure ##

The "monitor" have two main components the broker and the monitors.

To run the broker simply execute the the file:

	src/srv.py

To run a monitor execute the file:

	src/cli.py
	
To see all the possible parameters add the flag **-h** when executing any of the components.

## Requirements ##

libraries:

- psutil 1.1.3

The quickest way to install the required libraries is using pip and installing
the libraries listed in requirements.txt:

	pip install -r requirements.txt

## Tools ##

In order to avoid polluting your python environment we strongly recommend the 
usage of virtualenv to try dremo.

There are packages to install virtualenv for some linux distributions. But if 
your system does not have any specific way to do it you can use pip:

	pip install virtualenv

