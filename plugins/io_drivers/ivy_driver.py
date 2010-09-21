from enthought.traits.api import Str, Int
from enthought.traits.ui.api import View, Item, TextEditor

import time
import socket
import logging
import os
from ivy.std_api import *

from io_driver import IODriver

class IvyDriver(IODriver):
  """
      Ivy input driver.
  """
  _use_thread = False
  _ivy_id = Int(0)

  name = Str('Ivy Driver')
  ivy_agent_name = Str('Plot-o-matic')
  ivy_bus = Str('')
  ivy_ready_msg = Str('READY')
  ivy_regex = Str('(.*)')

  view = View(
    Item('ivy_agent_name', label='Agent name', editor=TextEditor(enter_set=True, auto_set=False)),
    Item('ivy_bus', label='Ivy bus', editor=TextEditor(enter_set=True, auto_set=False)),
    Item('ivy_regex', label='Regex', editor=TextEditor(enter_set=True, auto_set=False)),
    Item('ivy_ready_msg', label='Ready message', editor=TextEditor(enter_set=True, auto_set=False)),
    title='Ivy input driver'
  )

  def open(self):
    IvyInit(self.ivy_agent_name, self.ivy_ready_msg)
    logging.getLogger('Ivy').setLevel(logging.ERROR)
    IvyStart(self.ivy_bus)
    self._ivy_id = IvyBindMsg(self.on_ivy_msg, self.ivy_regex)
    
  def close(self):
    IvyUnBindMsg(self._ivy_id)
    IvyStop()

  def reopen(self):
    self.close()
    self.open()

  def _ivy_agent_name_changed(self):
    self.reopen()
  def _ivy_bus_changed(self):
    self.reopen()
  def _ivy_ready_msg_changed(self):
    self.reopen()
  def _ivy_regex_changed(self):
    self.reopen()

  def on_ivy_msg(self, agent, *larg):
    if larg[0] != self.ivy_ready_msg:
      self.pass_data(larg[0])

