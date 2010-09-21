from io_driver import IODriver
from data_decoder import DataDecoder
from viewers import Viewer

def find_io_driver_plugins():
  return IODriver.__subclasses__()
def get_io_driver_plugin_by_name(name):
  return filter(lambda x: x.__name__ == name, find_io_driver_plugins())[0]

def find_decoder_plugins():
  return DataDecoder.__subclasses__()
def get_decoder_plugin_by_name(name):
  return filter(lambda x: x.__name__ == name, find_decoder_plugins())[0]

def find_viewer_plugins():
  return Viewer.__subclasses__()
def get_viewer_plugin_by_name(name):
  return filter(lambda x: x.__name__ == name, find_viewer_plugins())[0]

