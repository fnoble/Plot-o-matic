from enthought.traits.api import Str, Float, Range, Int, Bool, on_trait_change
from enthought.traits.ui.api import View, Item

import time
import socket
import sys
import os
import re
from io_driver import IODriver

# get lcm stuff
jakobi_path = os.environ.get('AP_PROJECT_ROOT')

if jakobi_path == None:
  raise NameError("please set the AP_PROJECT_ROOT environment variable")

sys.path.append( jakobi_path+"/autobuild" )

import lcm

class LcmDriver(IODriver):
  """
      LCM input driver.
  """
  _use_thread = True

  name = Str('LCM Driver')
  view = View(
    Item(name='show_debug_msgs', label='Show debug messages'),
    title='LCM input driver'
  )
  
  show_debug_msgs = Bool(False)
  
  def lcm_handler(self, channel, data):
    print "\nprint channel"
    print channel

    decoder = self.decoders[channel]
    field_names = self.field_names[channel]

    msg = decoder.decode(data)

    print [eval("msg."+x) for x in field_names]
        
#    self.pass_data( dict( zip(names, vals) ) )

  def open(self):

    jakobi_path = os.environ.get('AP_PROJECT_ROOT')
    if jakobi_path == None:
      raise NameError("please set the AP_PROJECT_ROOT environment variable")

    # get classes from classes.dat
    file = open(jakobi_path+"/autobuild/classes.dat","r")
    classes = file.readline()
    classes = classes.split(" ")
    if classes[len(classes)-1] == '':
      classes = classes[0:len(classes)-1]
    file.close()
    self.lcm_class_names = classes
      

    # find out what types are in each class and put the list in lcm_channels
    self.lcm_channels = []

    for lcm_class_name in self.lcm_class_names:
      # import each class
      exec("import "+lcm_class_name)

      # store each type
      for entry in os.listdir(jakobi_path+"/autobuild/"+lcm_class_name):
        rs_entry = entry.rstrip(".py")
        if ((re.search('__init__', rs_entry) == None) and (re.search('^\w*[.]pyc', rs_entry) == None)):
          # if it's not .pyc or __init__, then grab the field names (called __slots__)
          file = open(jakobi_path+"/autobuild/"+lcm_class_name+"/"+entry)
          for line in file:
            m = re.match('    __slots__ = (\[[^]]*\])\n', line)
            if m != None:
              field_names = m.group(1)
          file.close()

          self.lcm_channels.append( (lcm_class_name,rs_entry, eval(field_names)) )

    self.lc = lcm.LCM()

    # now subscribe to ALL OF THEM
    self.subscriptions = []
    subscription_decoders = []
    for lcm_channel in self.lcm_channels:
      self.subscriptions.append(self.lc.subscribe(lcm_channel[0]+"_"+lcm_channel[1], self.lcm_handler))
      subscription_decoders.append(eval(lcm_channel[0]+"."+lcm_channel[1]))
#      print "haaaha"
#      print subscription_decoders[0]
#      print simple_model_sim.aircraft_pe_t
#
#      print subscription_decoders
#      print sldfkjsf

    # make one to one map of channel names to decoders

    self.decoders = dict( zip(map( lambda x: x[0]+"_"+x[1], self.lcm_channels ), subscription_decoders ))
    self.field_names = dict( map( lambda x: (x[0]+"_"+x[1],x[2] ), self.lcm_channels ))

    print "lcm finished opening"

  def close(self):
    self.lc.unsubscribe(self.subscription)


  def receive(self):
    self.lc.handle()

#  @on_trait_change('show_debug_messages')
#  def change_port(self):
#    self.rebind_socket()
    
