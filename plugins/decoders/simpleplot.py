from enthought.traits.api import Str, Enum
from enthought.traits.ui.api import View, Item
from data_decoder import DataDecoder
import re

class SimplePlotDecoder(DataDecoder):
  """
      Decodes lines of text formatted using a simple format.
  """
  
  name = Str('SimplePlot Decoder')
  
  view = View(
    Item(name="pass_through", label="Pass-through"),
    title='SimplePlot decoder'
  )
  
  pass_through = Enum('User messages', 'Plot-o-matic messages', 'Both', 'None')
  
  _sub_re = re.compile('\W+')

  def decode(self, data):
    """
        Decode an input string of the form ~variable_name#value.
    """
    if data[0] != '~':
      if self.pass_through == 'User messages' or self.pass_through == 'Both':
        print data[:-1]
      return None

    if self.pass_through == 'Plot-o-matic messages' or self.pass_through == 'Both':
      print data[:-1]

    var_name, val = data[1:].split('#')
    var_name = self._sub_re.sub('_', var_name)

    new_dict = {}
    try:
      new_dict[var_name] = float(val)
    except:
      new_dict[var_name] = val

    return new_dict
