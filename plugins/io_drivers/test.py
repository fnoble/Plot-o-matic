from enthought.traits.api import Str, Range
from enthought.traits.ui.api import View, Item, TextEditor

import time

from io_driver import IODriver

class TestDriver(IODriver):
  """
      Simple driver for testing, sends the same string periodically.
  """

  name = Str('Test Driver')
  view = View(
    Item(name = 'data', label='Test string', editor=TextEditor(enter_set=True, auto_set=False)),
    Item(name = 'period_ms', label='Period / ms'),
    title='Test input driver'
  )
  
  data = Str('')
  period_ms = Range(10, 10000, 200)
  
  def receive(self):
    time.sleep(self.period_ms / 1000.0)
    return self.data


