from enthought.traits.api import Str, Bool, Enum, List
from enthought.traits.ui.api import View, Item
from data_decoder import DataDecoder
import re

class LcmDecoder(DataDecoder):
  """
      Decodes lines of text formatted using a simple format.
  """
  name = Str('LCM Decoder')
  
  view = View(
    title='LCM Decoder'
  )
  
  _sub_re = re.compile('\W+')
  _names = List()

  def decode(self, data):
    """
        Decodes input from LCM messages.
    """
#    if data[0] == '#':
#      # list of names
#      self._names = [self._sub_re.sub('_', name) for name in data[1:].split('!')]
#      print "JobySimDecoder got names:", self._names
#      return None
#
#    vals = map(eval, data.split('!'))
#    d = dict(zip(self._names, vals))
#    return d

#    print data
    return data

#    return {'hi':0}
