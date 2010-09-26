from enthought.traits.api import Str
from enthought.traits.ui.api import View, Item, TextEditor
from data_decoder import DataDecoder
import re

class RegexDecoder(DataDecoder):
  """
      Decodes arbitrary text using regex.
  """
  name = Str('Regex Decoder')
  view = View(
    Item(name = 'regex', label='Regex', editor=TextEditor(enter_set=True, auto_set=False)),
    Item(label= "Each subgroup in the regex is \nassigned to a variable \nin the list in order."),
    Item(name = 'variable_names', label='Group names', editor=TextEditor(enter_set=True, auto_set=False)),
    Item(label= "(comma separated, use '_' to ignore a subgroup)"),
    title='Regex decoder'
  )
  regex = Str()
  variable_names = Str()
  
  def decode(self, data):
    """
        Decode CSV input data then assign variables based on a CSV format list
        list of names, using an '_' to ignore a field.
    """
    re_result = ''
    try:
      re_result = re.search(self.regex, data)
    except:
      return None
    
    if not re_result:
      return None

    re_groups = re_result.groups()
    var_names = self.variable_names.split(',')
    
    if len(re_groups) == len(var_names):
      data_dict = {}
      for n, var in enumerate(var_names):
        if var != '_':
          try:
            data_dict[var] = float(re_groups[n])
          except:
            data_dict[var] = re_groups[n]
      return data_dict
    
