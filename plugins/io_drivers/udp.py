from enthought.traits.api import Str, Float, File, Int, Bool, on_trait_change
from enthought.traits.ui.api import View, Item

import time
import socket

from io_driver import IODriver

class UDPDriver(IODriver):
  """
      UDP input driver.
  """
  
  name = Str('UDP Driver')
  view = View(
    Item(name='port', label='Port'),
    Item(name='filter_by_addr', label='Filter by remote address'),
    Item(name='filter_addr', label='Filter address'),    
    Item(name='ip', label='IP address to bind'),
    Item(label='(use 0.0.0.0 to bind \nto all interfaces)'),
    Item(name='show_debug_msgs', label='Show debug messages'),
    title='UDP input driver'
  )
  
  _sock = socket.socket()

  port = Int(5000)
  ip = Str('0.0.0.0')
  filter_by_addr = Bool(False)
  show_debug_msgs = Bool(False)
  filter_addr = Str('')
  
  def open(self):
    self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self._sock.settimeout(1.0) # seconds
    self._sock.bind((self.ip, self.port))
    
  def close(self):
    self._sock.close()
  
  def receive(self):
    try:
      (data, (addr, port)) = self._sock.recvfrom(102400) # buffer size is 10kb
      if self.show_debug_msgs:
        print "UDP driver: packet from '%s' size %u bytes" % (addr, len(data))
      if self.filter_by_addr and addr != self.filter_addr:
        return None
    except socket.timeout:
      return None
    return data

  def rebind_socket(self):
    self._sock.close()
    self.open()

  @on_trait_change('port')
  def change_port(self, old_port, new_port):
    self.rebind_socket()
    
  @on_trait_change('address')
  def change_address(self, old_address, new_address):
    self.rebind_socket()
    
