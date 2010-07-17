from enthought.traits.api import Str
from enthought.traits.ui.api import View, Item
from data_decoder import DataDecoder

class CSVDecoder(DataDecoder):
  """
      Decodes lines of CSV formatted text.
  """
  name = Str('CSV Decoder')
  view = View(
    Item(name = 'separator', label='Field separator'),
    Item(name = 'variable_names', label='Field names'),
    Item(label= "(use '_' to ignore a field)"),
    title='CSV decoder'
  )
  separator = Str(',')
  variable_names = Str('_,a,b,c,d')
  
  def decode(self, data):
    """
        Decode CSV input data then assign variables based on a CSV format list
        list of names, using an '_' to ignore a field.
    """
    data_list = data.split(self.separator)
    var_names = self.variable_names.split(',')
    
    if len(data_list) == len(var_names):
      data_dict = {}
      for n, var in enumerate(var_names):
        if var != '_':
          data_dict[var] = float(data_list[n])
      return data_dict
      
    return None
    