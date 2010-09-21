from enthought.traits.api import Str, Bool, Enum, List
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
  names = List()

  def decode(self, data):
    """
        Decode an input string of the form ~variable_name#value.
    """
    if data[0] == '#':
      # list of names
      self.names = [self.sub_re.sub('_', name) for name in data[1:].split('!')]
      #print "JobySimDecoder got names:", self.names
      return None

    vals = map(eval, data.split('!'))
    d = dict(zip(self.names, vals))
    #print d
    return d
