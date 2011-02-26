from enthought.traits.api import Str, Float, Range, Int, Bool, on_trait_change
from enthought.traits.ui.api import View, Item
import sys
import os
from xml.etree import ElementTree as ET
import xml.parsers.expat as expat

from io_driver import IODriver

import lcm

class ConftronDriver(IODriver):
  """
      Conftron input driver.
  """
  _use_thread = True

  name = Str('Conftron Driver')
  view = View(
    Item(name='show_debug_msgs', label='Show debug messages'),
    title='Conftron input driver'
  )
  
  show_debug_msgs = Bool(True)

  def lcm_handler(self, channel, data):

    to_decoder = {}
    to_decoder['class'] = self.messages[channel]['class']
    to_decoder['name'] = self.messages[channel]['name']
    to_decoder['type'] = self.messages[channel]['type']
    to_decoder['channel'] = self.messages[channel]['channel']
    to_decoder['message'] = self.messages[channel]['decoder'].decode(data)

    self.queued_messages.append(to_decoder)

  def open(self):
    self.queued_messages = []

    # set up paths
    self.ap_project_root = os.environ.get('AP_PROJECT_ROOT')
    if self.ap_project_root == None:
      raise NameError("please set the AP_PROJECT_ROOT environment variable to use Conftron driver")
    sys.path.append( self.ap_project_root+"/conftron/python" )

    # create lcm instance
    self.lc = lcm.LCM()

    # parse telemetry.xml
    self.messages = {}
    for cl in ET.ElementTree().parse( self.ap_project_root+"/conf/telemetry.xml").getchildren():
      # import the class modules, like ap/sim/vis/etc
      exec("import "+cl.attrib['name'])
      class_module = eval(cl.attrib['name'])

      for msg in cl.getchildren():
        m = {}
        # the attributes right of of telemetry.xml
        m['class'] = cl.attrib['name']
        m['type'] = msg.attrib['type']
        m['name'] = msg.attrib['name']

        # create the channel name if one isn't explicitely specified
        try:
          m['channel'] = msg.attrib['channel']
        except KeyError:
          m['channel'] = m['class']+"_"+m['type']+"_"+m['name']

        # get the decoder
        m['decoder'] = eval("class_module."+m['type'])

        # subscribe to the channel
        m['subscription'] = self.lc.subscribe(m['channel'], self.lcm_handler )

        # add this entry to the messages dictionary
        self.messages[m['channel']] = m

  def close(self):
    for msg in self.messages.values():
      self.lc.unsubscribe(msg['subscription'])

  def receive(self):
    self.lc.handle()

    # empty self.queued_messages
    if len(self.queued_messages) > 0:
      qm = self.queued_messages
      self.queued_messages = []
      return qm

#  @on_trait_change('show_debug_messages')
#  def change_port(self):
#    self.rebind_socket()
    

if __name__ == '__main__':
  cd = ConftronDriver()
  cd.open()
  try:
    while True:
        cd.lc.handle()
  except KeyboardInterrupt:
    pass

  for msg in cd.messages.values():
    cd.lc.unsubscribe(msg['subscription'])
