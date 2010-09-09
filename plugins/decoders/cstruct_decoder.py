from enthought.traits.api import Str
from enthought.traits.ui.api import View, Item
from data_decoder import DataDecoder
import struct

def unpack_with_arrays(format, data):
  """ Group arrays in a struct into an array in the output. """
  unpacked = struct.unpack(format, data)
  if format[0] in '@=!<>':
    format = format[1:]
  
  grouped = []
  while format:
    if format[0] not in '0123456789':
      grouped += [unpacked[0]]
      format = format[1:]
      unpacked = unpacked[1:]
    else:
      num = ''
      while format[0] in '0123456789':
        num += format[0]
        format = format[1:]
      num = int(num)
      grouped += [unpacked[:num]]
      format = format[1:]
      unpacked = unpacked[num:]
      
  return grouped

class CStructDecoder(DataDecoder):
  """
      Decodes binary C structs.
  """
  name = Str('C Struct Decoder')
  view = View(
    Item(name = 'struct_format', label='Format'),
    Item(label= "Each field in the struct is \nassigned to a variable \nin the list in order."),
    Item(name = 'variable_names', label='Field names'),
    Item(label= "(use '_' to ignore a field)"),
    title='C struct decoder'
  )
  struct_format = Str('=HIB32dd32d3d3di')
  variable_names = Str('type,len,chksum,corrs,timestamp,snrs,pos,vel,no_receivers')
  
  def decode(self, data):
    """
        Decode struct input data then assign variables based on a CSV format list
        list of names, using an '_' to ignore a field.
    """
    if len(data) != struct.calcsize(self.struct_format):
      #print "Struct decoder: Wanted %d bytes but got %d" % (struct.calcsize(self.struct_format), len(data))
      return None
    
    try:
      result = unpack_with_arrays(self.struct_format, data)
    except:
      result = None
    
    if result:
      var_names = self.variable_names.split(',')
      
      if len(result) == len(var_names):
        data_dict = {}
        for n, var in enumerate(var_names):
          if var != '_':
            data_dict[var] = result[n]
        return data_dict
      
    return None
    