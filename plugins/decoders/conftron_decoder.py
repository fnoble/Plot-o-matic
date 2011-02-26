from enthought.traits.api import Str, Bool, Enum, List
from enthought.traits.ui.api import View, Item
from data_decoder import DataDecoder
import re

class ConftronDecoder(DataDecoder):
  """
      Conftron lcm class decoder
  """
  name = Str('Conftron Decoder')
  
  view = View(
    title='Conftron Decoder'
  )
  
  _sub_re = re.compile('\W+')
  _names = List()

  def decode(self, data):
    """
        Decodes input from Conftron/LCM messages.
    """

    if len(data) > 0:
      print "Conftron message queue grew larger than 1"

    print data

#    print "decoding, yo"
#    if data['channel'] == 'pose':
#      print data

    return {'hi':0}

#      print self.messages[channel]['decoder'].decode(data)
#      print msg
#      print msg.r_n2b_n

#      print msg.__class__
#      for blah in msg:
#        print blah


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


