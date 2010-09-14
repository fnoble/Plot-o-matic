from enthought.traits.api import Str, Bool, Enum
from enthought.traits.ui.api import View, Item
from data_decoder import DataDecoder
import re

class JobySimDecoder(DataDecoder):
  """
      Decodes lines of text formatted using a simple format.
  """
  name = Str('JobySim Decoder')
  view = View(
    title='JobySim decoder'
  )
  sub_re = re.compile('\W+')

  def decode(self, data):
    """
        Decode an input string of the form ~variable_name#value.
    """

    mylist = data[0:].split('!')
    
    new_dict = {}

    for item in mylist:
      var_name, val = item.split('#')
      var_name = self.sub_re.sub('_', var_name)
      try:
        new_dict[var_name] = eval(val)
      except:
        new_dict[var_name] = val

    return new_dict
