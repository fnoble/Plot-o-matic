from enthought.traits.api import Str, Float, File, Int, Bool, on_trait_change, Instance
from enthought.traits.ui.api import View, Item

import time
import socket
import logging
import os
from ivy.std_api import *

from io_driver import IODriver

class IvyMessagesInterface():
  def __init__(self, callback, initIvy = True):
    self.callback = callback
    self.ivy_id = 0
    self.InitIvy(initIvy)
  def Stop(self):
    IvyUnBindMsg(self.ivy_id)
  def __del__(self):
    try:
      IvyUnBindMsg(self.ivy_id)
    except:
      pass
  def InitIvy(self, initIvy):
    if initIvy:
      IvyInit("Messages %i" % os.getpid(), "READY", 0, lambda x,y: y, lambda x,y: y)
#      IvyInit("Messages %i" % os.getpid())
      logging.getLogger('Ivy').setLevel(logging.WARN)
      IvyStart("")
    self.ivy_id = IvyBindMsg(self.OnIvyMsg, "(.*)")
  def OnIvyMsg(self, agent, *larg):
    self.callback(larg[0])

class IvyDriver(IODriver):
  """
      Ivy input driver.
  """
  
  name = Str('Ivy Driver')
  view = View(
#    Item(name='foo', label='Foo'),
    title='Ivy input driver'
  )

#  foo = 'foobar'
  ivyInterface = Instance(IvyMessagesInterface)
  initd = Instance(bool,False)

  def open(self):
    if not self.initd:
      self.ivyInterface = IvyMessagesInterface(self.got_data,True)
      self.initd = True
    else:
      self.ivyInterface.InitIvy(True)
    
  def close(self):
    self.ivyInterface.Stop()

  def got_data(self,data):
    if not data=='READY':
      self.pass_data(data)

