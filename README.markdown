Plot-o-matic
============

Plot-o-matic is a simple application for graphing and monitoring live streams of data from different sources. The aim is to make it easier to quickly visualise data when prototyping some new device or software.

It includes a plugin architecture to make it very easy to add new input sources and decoders for your own packet formats and, being written in python, it is easily modified or scripted for specific applications.

Eventually the aim is to include a number of general purpose plugins to read from serial ports, files, network sockets etc. and decoders for common data formats e.g. CSV, C structs etc.

Installation
============

Plot-o-matic requires the following python modules to be installed:

* numpy
* wx
* setupdocs (required by Traits)
* Traits
* TraitsGUI
* TraitsBackendWX (untested with the Qt backend)
* Chaco
* Mayavi
* Python VTK

You will probably also need the following packages:

* swig (required by Chaco/Enable)

Some step-by-step instructions for specific platforms are below but in general you can obtain these modules through easy_install.

Ubuntu
------

Install the common libraries through apt:

`sudo apt-get install python-dev python-setuptools python-setupdocs python-wxgtk2.8 python-numpy swig python-vtk`

Get Traits etc. through easy_install because the versions in Ubuntu's repos are quite old:

`sudo easy_install Traits TraitsGUI TraitsBackendWX Chaco Mayavi`

Running
=======

From the command-line:

`./plot-o-matic.py`

