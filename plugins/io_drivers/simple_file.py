from io_driver import IODriver
from enthought.traits.api import Str, Range, File, Any, on_trait_change
from enthought.traits.ui.api import View, Item
import time

class SimpleFileDriver(IODriver):
  """
      Simple file input driver. Reads lines from a file periodically.
  """
  
  name = Str('Simple File Driver')
  view = View(
    Item(name = 'data_file', label='Input file'),
    Item(name = 'period_ms', label='Period / ms'),
    title='Simple file input driver'
  )

  data_file = File()
  period_ms = Range(10, 10000, 200)

  _fp = Any()
  
  def open(self):
    try:
      self._fp = open(self.data_file, 'r')
    except IOError:
      self._fp = None
    
  def close(self):
    if self._fp:
      self._fp.close()
  
  def receive(self):    
    if self._fp:
      time.sleep(self.period_ms / 1000.0)
      return self._fp.readline()
    else:
      return None
      
  @on_trait_change('data_file')
  def reopen_file(self):
    self.close()
    self.open()
