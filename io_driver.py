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
  _variables = Instance(Variables)
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
      try:
        self.close()       
      except Exception as e:
        print "Exception closing IO driver '%s':" % self.name, e
    
  def start(self):
    """ Used internally to start the thread for the input driver, if you have init code put it in open. """
    try:
      self.open()        
    except Exception as e:
      print "Exception opening IO driver '%s':" % self.name, e
      self.stop()
    t.Thread.start(self)

  def stop(self):
    """ Used internally to stop the thread for the input driver, if you have clean-up code put it in close. """
    if self._use_thread:
      self._wants_to_terminate = True
    else:
      try:
        self.close()       
      except Exception as e:
        print "Exception closing IO driver '%s':" % self.name, e
   
  def _add_decoder(self, decoder):
    """ Used internally to add decoders so they receive data from the input driver. """
    decoder._variables = self._variables
    self._decoders += [decoder]

  def _remove_decoder(self, decoder):
    """ Used internally to remove decoders from an input driver. """
    self._decoders.remove(decoder)

  def _remove_all_decoders(self):
    for decoder in self._decoders:
      self._remove_decoder(decoder)
    
  def pass_data(self, data):
    """ Pass data on to the decoding layer. """
    for decoder in self._decoders: #self._decoder_list.get_decoders():
      decoder._receive_callback(data)

  def get_config(self):
    print "Warning: using defualt get_config handler on io driver '%s' (which may not work)." % self.__class__.__name__
    state = self.__getstate__()
    for key in list(state.iterkeys()):
      if key.startswith('_'):
        del state[key]
    print "  config:", state
    return state

  def set_config(self, config):
    print "Warning: using defualt set_config handler on io driver '%s' (which may not work)." % self.__class__.__name__
    print "  config:", config
    self.__setstate__(config)

  def _get_config(self):
    # get decoders
    decoder_configs = []
    for decoder in self._decoders:
      decoder_config = {decoder.__class__.__name__: decoder.get_config()}
      decoder_configs.append(decoder_config)
    
    config = self.get_config()
    config.update({'decoders': decoder_configs})
    return config

  def _set_config(self, config):
    from plugin_manager import get_decoder_plugin_by_name
    # add decoders
    self._remove_all_decoders()
    for decoder_config in config['decoders']:
      decoder_plugin_name = list(decoder_config.iterkeys())[0]
      decoder_plugin_config = decoder_config[decoder_plugin_name]
      new_decoder = get_decoder_plugin_by_name(decoder_plugin_name)()
      self._add_decoder(new_decoder)
      new_decoder.set_config(decoder_plugin_config)

    del config['decoders']
    self.set_config(config)


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

  def _remove_all_io_drivers(self):
    for io_driver in self.io_drivers:
      self._remove_io_driver(io_driver)

  def _add_io_driver(self, io_driver):
    print "Adding IO driver:", io_driver.name
    io_driver._variables = self.variables
    io_driver.start()
    self.io_drivers.append(io_driver)

  def get_config(self):
    config = []
    for io_driver in self.io_drivers:
      io_driver_config = {io_driver.__class__.__name__: io_driver._get_config()}
      config.append(io_driver_config)
    return config

  def set_config(self, config):
    from plugin_manager import get_io_driver_plugin_by_name
    self._remove_all_io_drivers()
    for io_driver_config in config:
      io_driver_plugin_name = list(io_driver_config.iterkeys())[0]
      io_driver_plugin_config = io_driver_config[io_driver_plugin_name]
      new_io_driver = get_io_driver_plugin_by_name(io_driver_plugin_name)()
      self._add_io_driver(new_io_driver)
      new_io_driver._set_config(io_driver_plugin_config)


