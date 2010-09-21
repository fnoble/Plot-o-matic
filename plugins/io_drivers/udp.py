from enthought.traits.api import Str, Float, Range, Int, Bool, on_trait_change
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
    Item(name='buffer_size', label='Buffer size / kb'),
    Item(name='timeout', label='Timeout / s'),
    title='UDP input driver'
  )
  
  _sock = socket.socket()

  port = Range(1024, 65535, 5000)
  buffer_size = Range(1, 4096, 10) # no reason not to go above 4MB but there should be some limit.
  timeout = Float(1.0)
  ip = Str('0.0.0.0')
  filter_by_addr = Bool(False)
  show_debug_msgs = Bool(False)
  filter_addr = Str('')
  
  def open(self):
    self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self._sock.settimeout(self.timeout) # seconds
    self._sock.bind((self.ip, self.port))
    
  def close(self):
    self._sock.close()
  
  def receive(self):
    try:
      (data, (addr, port)) = self._sock.recvfrom(1024*self.buffer_size)
      if self.show_debug_msgs:
        print "UDP driver: packet from '%s' size %u bytes" % (addr, len(data))
      if self.filter_by_addr and addr != self.filter_addr:
        return None
    except socket.timeout:
      return None
    return data

  def rebind_socket(self):
    self.close()
    self.open()

  @on_trait_change('port')
  def change_port(self):
    self.rebind_socket()
    
  @on_trait_change('address')
  def change_address(self):
    self.rebind_socket()

  @on_trait_change('timeout')
  def change_timeout(self):
    self.rebind_socket()
    
