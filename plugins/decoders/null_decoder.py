from enthought.traits.api import Str
from enthought.traits.ui.api import View, Item
from data_decoder import DataDecoder

class NullDecoder(DataDecoder):
  """
      Doesn't do anything, just prints what it received to the console.
  """
  
  name = Str('Null Decoder')
  
  view = View(
    Item(label= "The null decoder just prints the data \nit receives to the console for testing."),
    title='Null decoder'
  )
  
  def decode(self, data):
    print data
    return None
    