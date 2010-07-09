import threading as t
from enthought.traits.api import HasTraits, Int, Str, List
from data_decoder import DataDecoder

class IODriver(t.Thread, HasTraits):
  """ 
      Base class for a generic input driver. Runs in its own thread and grabs input from the 
      source and passes it out to the decoding layer. 
  """
  # list of callback functions for the various listeners on this input
  _decoders = List(DataDecoder)
  _wants_to_terminate = False
  name = Str('Input Driver')
  
  def __init__(self):
    t.Thread.__init__(self)
    HasTraits.__init__(self)
  
  def open(self):
    """
        Here is a place to put any initialisation needed to start your driver, e.g. opening 
        a port or file.
    """
    pass

  def close(self):
    """
        Here is a place to put any code needed to cleanly stop your input driver e.g. closing a port
    """
    pass
  
  def receive(self):
    """ 
        In this function you should add the code to setup and read from
        your input source. Call pass_data somewhere here to pass the received
        data to the data decoding layer. This function is called repeatedly
        while the driver is running and should not block indefinately (a timeout
        should be used to allow the driver to stop).
    """
    pass
    
  def run(self):
    while not self._wants_to_terminate:
      self.receive()
    self.close()
    
  def start(self):
    self.open()
    t.Thread.start(self)

  def stop(self):
    self._wants_to_terminate = True
   
  def _register_decoder(self, decoder):
    self._decoders += [decoder]
    
  def pass_data(self, data):
    """
        Pass data on to the decoding layer.
    """
    for decoder in self._decoders:
      decoder._receive_callback(data)
      
