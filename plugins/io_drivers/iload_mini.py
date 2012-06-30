from io_driver import IODriver
from enthought.traits.api import Str, Int, Button, Any, on_trait_change
from enthought.traits.ui.api import View, Item
import serial

class ILoadMiniDriver(IODriver):
  """
      Input driver for the iLoad Mini from Loadstar.
  """

  name = Str('iLoad Mini Driver')
  view = View(
    Item(name = 'serial_port', label='Serial port'),
    Item(name = 'connect', label='Connect'),
    Item(name = 'disconnect', label='Disconnect'),
    Item(name = 'tare', label='Tare'),
    title='iLoad Mini input driver'
  )

  serial_port = Str()
  connect = Button()
  disconnect = Button()
  tare = Button()

  _sp = Any()

  @on_trait_change('serial_port')
  @on_trait_change('connect')
  def do_connect(self):
    print 'iLoad Mini Connecting'
    self.close()
    try:
      self._sp = serial.Serial(self.serial_port, 9600, timeout=1)
      self._sp.write('O0W0\r')
    except IOError:
      self._sp = None

  @on_trait_change('disconnect')
  def do_disconnect(self):
    print 'iLoad Mini Disconnecting'
    if self._sp:
      self._sp.close()
      self._sp = None

  def receive(self):
    if self._sp:
      return self._sp.readline()
    else:
      return None

