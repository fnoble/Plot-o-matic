from enthought.traits.api import HasTraits, Instance, Str
from variables import Variables

class DataDecoder(HasTraits):
  """
      Decodes the input stream into a dictionary of name, value pairs which will
      become the variables we can plot.
  """
  name = 'Decoder'
  _variables = Instance(Variables) 
  
  def decode(self, data):
    """
        This function gets called when some new data is received from
        the input, here you should decode it and return a dict containing
        variable names and values for the data. Return None if no new data
        is decoded.
    """
    return None
    
  def _receive_callback(self, data):
    new_vars = self.decode(data)
    if new_vars:
      self._variables.update_variables(new_vars)

  def get_config(self):
    print "Warning: using defualt get_config handler on decoder '%s' (which may not work)." % self.__class__.__name__
    state = self.__getstate__()
    for key in list(state.iterkeys()):
      if key.startswith('_'):
        del state[key]
    print "  config:", state
    return state

  def set_config(self, config):
    print "Warning: using defualt set_config handler on decoder '%s' (which may not work)." % self.__class__.__name__
    print "  config:", config
    self.__setstate__(config)

