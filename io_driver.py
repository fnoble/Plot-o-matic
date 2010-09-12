import threading as t
from enthought.traits.api import HasTraits, Int, Str, List, DelegatesTo, Instance
from data_decoder import DataDecoder

from variables import Variables
from viewers import Viewers

class IODriver(t.Thread, HasTraits):
  """ 
      Base class for a generic input driver. Runs in its own thread and grabs input from the 
      source and passes it out to the decoding layer. 
  """
  _decoders = List(DataDecoder)
  _wants_to_terminate = False
  _use_thread = True
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
    if self._use_thread:
      while not self._wants_to_terminate:
        data = self.receive()
        if data:
          self.pass_data(data)
      print "IO driver thread terminating:", self.name
      self.close()
    
  def start(self):
    """ Used internally to start the thread for the input driver, if you have init code put it in open. """
    self.open()
    t.Thread.start(self)

  def stop(self):
    """ Used internally to stop the thread for the input driver, if you have clean-up code put it in close. """
    if self._use_thread:
      self._wants_to_terminate = True
    else:
      self.close()
   
  def _add_decoder(self, decoder):
    """ Used internally to add decoders so they receive data from the input driver. """
    self._decoders += [decoder]

  def _remove_decoder(self, decoder):
    """ Used internally to remove decoders from an input driver. """
    self._decoders.remove(decoder)
    
  def pass_data(self, data):
    """ Pass data on to the decoding layer. """
    for decoder in self._decoders: #self._decoder_list.get_decoders():
      decoder._receive_callback(data)



class IODriverList(HasTraits):
  """
      Maintains the list of input drivers currently in use and provides
      facilities to add and remove drivers.
  """
  io_drivers = List(IODriver)
  viewers = DelegatesTo('viewers_instance')
  viewers_instance = Instance(Viewers)
  variables = Instance(Variables)
  
  def start_all(self):
    map(lambda d: d.start(), self.io_drivers)

  def stop_all(self):
    map(lambda d: d.stop(), self.io_drivers)

  def _remove_io_driver(self, io_driver):
    print "Removing IO driver:", io_driver.name
    io_driver.stop()
    self.io_drivers.remove(io_driver)

  def _add_io_driver(self, io_driver):
    print "Adding IO driver:", io_driver.name
    io_driver.start()
    self.io_drivers.append(io_driver)


