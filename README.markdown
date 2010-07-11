Plot-o-matic
============

Plot-o-matic is a simple application for graphing and monitoring live streams of data from different sources. The aim is to make it easier to quickly visualise data when prototyping some new device or software.

It includes a plugin architecture to make it very easy to add new input sources and decoders for your own packet formats and, being written in python, it is easily modified or scripted for specific applications.

Eventually the aim is to include a number of general purpose plugins to read from serial ports, files, network sockets etc. and decoders for common data formats e.g. CSV, C structs etc.