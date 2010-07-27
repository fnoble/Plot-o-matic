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
    title='UDP input driver'
  )
  
  sock = socket.socket()

  port = Int(21212)
  ip = Str('0.0.0.0')
  filter_by_addr = Bool(False)
  filter_addr = Str('')
  
  #def _ip_default(self):
  #  print "UDP driver: my hostname '%s' (ip %s)" % (socket.gethostname(), socket.gethostbyname(socket.gethostname()))
  #  return socket.gethostbyname(socket.gethostname())
  
  def open(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.settimeout(1.0) # seconds
    self.sock.bind((self.ip, self.port))
    
  def close(self):
    self.sock.close()
  
  def receive(self):
    try:
      (data, (addr, port)) = self.sock.recvfrom(102400) # buffer size is 10kb
      print "UDP driver: packet from '%s' size %u bytes" % (addr, len(data))
      if self.filter_by_addr and addr != self.filter_addr:
        return None
    except socket.timeout:
      return None
    return data

  def rebind_socket(self):
    self.sock.close()
    self.open()

  @on_trait_change('port')
  def change_port(self, old_port, new_port):
    self.rebind_socket()
    
  @on_trait_change('address')
  def change_address(self, old_address, new_address):
    self.rebind_socket()
    