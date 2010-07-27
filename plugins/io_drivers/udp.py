from enthought.traits.api import Str, Float, File, Int, on_trait_change
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
    Item(name = 'port', label='Port'),
    Item(name = 'ip', label='IP Address'),
    title='UDP input driver'
  )
  
  sock = socket.socket()

  port = Int(2222)
  ip = Str('127.0.0.1')
  
  def open(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.settimeout(1.0) # seconds
    self.sock.bind((self.ip, self.port))
    
  def close(self):
    self.sock.close()
  
  def receive(self):
    try:
      data, addr = self.sock.recvfrom(102400) # buffer size is 10kb
    except socket.timeout:
      return None
    
    #print "Received UDP message from %s, size %d bytes" % (addr[0], len(data))
    return data

  def rebind_socket(self):
    self.sock.close()
    self.sock.bind((self.ip, self.port))

  @on_trait_change('port')
  def change_port(self, old_port, new_port):
    self.rebind_socket()
    
  @on_trait_change('address')
  def change_address(self, old_address, new_address):
    self.rebind_socket()
    