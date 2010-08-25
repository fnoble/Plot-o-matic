from enthought.traits.api import Str, Bool
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
  pass_through = Bool(True)
  sub_re = re.compile('\W+')

  def decode(self, data):
    """
        Decode an input string of the form ~variable_name#value.
    """
    if self.pass_through:
      print data
    
    if data[0] != '~':
      return None

    var_name, val = data[1:].split('#')
    var_name = self.sub_re.sub('_', var_name)
    new_dict = {}

    try:
      new_dict[var_name] = float(val)
    except:
      new_dict[var_name] = val

    return new_dict
