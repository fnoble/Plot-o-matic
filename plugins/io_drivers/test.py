from io_driver import IODriver
from enthought.traits.api import Str, Float
from enthought.traits.ui.api import View, Item
import time

class TestDriver(IODriver):
  """
      Simple driver for testing, sends the same string periodically.
  """
  name = Str('Test Driver')
  view = View(
    Item(name = 'data', label='Test string'),
    Item(name = 'period_ms', label='Period / ms'),
    title='Test input driver'
  )
  
  data = Str('Data,2,4,6,7.8')
  period_ms = Float(1000.0)
  
  def receive(self):    
    time.sleep(self.period_ms / 1000.0)
    return self.data