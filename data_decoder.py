from enthought.traits.api import HasTraits, Str

class DataDecoder(HasTraits):
  """
      Decodes the input stream into a dictionary of name, value pairs which will
      become the variables we can plot.
  """
  name = 'Decoder'
  data_dict = {}
  
  def receive(self, data):
    """
        This function gets called when some new data is received from
        the input, here you should decode it and update the variables you
        are decoding
    """
    pass
    
  def _receive_callback(self, data):
    self.receive(data)
    self.send_update()
    
  def send_update(self):
    print self.data_dict