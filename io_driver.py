import threading as t
from enthought.traits.api import HasTraits, Int, Str, List
from data_decoder import DataDecoder

class IODriver(t.Thread, HasTraits):
  """ 
      Base class for a generic input driver. Runs in its own thread and grabs input from the 
      source and passes it out to the decoding layer. 
  """
  _decoders = List(DataDecoder)
  _wants_to_terminate = False
  name = Str('Input Driver')
  
  def __init__(self, **kwargs):
    t.Thread.__init__(self)
    HasTraits.__init__(self, **kwargs)
  
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
        your input source. Return the received data to be passed to the data 
        decoding layer. This function is called repeatedly while the driver 
        is running and should not block indefinately (a timeout should be 
        used to allow the driver to stop). You can return None is no data is available.
    """
    return None
    
  def run(self):
    """ Used internally for the threading interface, you should put your code in receive. """
    while not self._wants_to_terminate:
      data = self.receive()
      if data:
        self.pass_data(data)
    self.close()
    
  def start(self):
    """ Used internally to start the thread for the input driver, if you have init code put it in open. """
    self.open()
    t.Thread.start(self)

  def stop(self):
    """ Used internally to stop the thread for the input driver, if you have clean-up code put it in close. """
    self._wants_to_terminate = True
   
  def _register_decoder(self, decoder):
    """ Used internally to register decoders so they receive data from the input driver. """
    self._decoders += [decoder]
    
  def pass_data(self, data):
    """ Pass data on to the decoding layer. """
    for decoder in self._decoders: #self._decoder_list.get_decoders():
      decoder._receive_callback(data)
