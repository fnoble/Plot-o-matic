from io_driver import IODriver
from enthought.traits.api import Str, Float, File, on_trait_change
from enthought.traits.ui.api import View, Item
import time

class SimpleFileDriver(IODriver):
  """
      Simple file input driver.
  """
  
  name = Str('Simple File Driver')
  view = View(
    Item(name = 'data_file', label='Input file'),
    Item(name = 'period_ms', label='Period / ms'),
    title='Simple file input driver'
  )

  data_file = File('test1')
  period_ms = Float(1000.0)
  _fp = file
  
  def open(self):
    self._fp = open(self.data_file, 'r')
    
  def close(self):
    self._fp.close()
  
  def receive(self):    
    time.sleep(self.period_ms / 1000.0)
    return self._fp.readline()
      
  @on_trait_change('data_file')
  def reopen_file(self, old_file, new_file):
    self._fp.close()
    self._fp = open(self.data_file, 'r')
