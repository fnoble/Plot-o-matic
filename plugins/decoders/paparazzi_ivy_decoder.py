from enthought.traits.api import Str, Instance
from enthought.traits.ui.api import View, Item
from data_decoder import DataDecoder
import sys
import os

def ParseMessages():
  from lxml import etree
  paparazzi_home = os.getenv("PAPARAZZI_HOME")
  if not paparazzi_home:
    paparazzi_home = '%s/software/paparazzi' % os.getenv("HOME")
  messages_path = '%s/conf/messages.xml' % paparazzi_home
  message_dictionary = {}
  message_dictionary_types = {}
  message_dictionary_id_name = {}
  message_dictionary_name_id = {}
  tree = etree.parse( messages_path)
  for the_class in tree.xpath("//class[@name]"):
    class_name = the_class.attrib['name']
    if not message_dictionary.has_key(class_name):
      message_dictionary_id_name[class_name] = {}
      message_dictionary_name_id[class_name] = {}
      message_dictionary[class_name] = {}
      message_dictionary_types[class_name] = {}
    for the_message in the_class.xpath("message[@name]"):
      message_name = the_message.attrib['name']
      if the_message.attrib.has_key('id'):
        message_id = the_message.attrib['id']
      else:
        message_id = the_message.attrib['ID']
      if (message_id[0:2] == "0x"):
        message_id = int(message_id, 16)
      else:
        message_id = int(message_id)

      message_dictionary_id_name[class_name][message_id] = message_name
      message_dictionary_name_id[class_name][message_name] = message_id

      # insert this message into our dictionary as a list with room for the fields
      message_dictionary[class_name][message_name] = []
      message_dictionary_types[class_name][message_id] = []

      for the_field in the_message.xpath('field[@name]'):
        # for now, just save the field names -- in the future maybe expand this to save a struct?
        message_dictionary[class_name][message_name].append( the_field.attrib['name'])
        message_dictionary_types[class_name][message_id].append( the_field.attrib['type'])
  message_dictionary = message_dictionary['telemetry']
##-- extra code to only use the messages being used-----
#  actual_messages_path = '%s/conf/telemetry/mercuryX.xml' % paparazzi_home
#  actual_messages = []
#  tree = etree.parse( actual_messages_path)
#  for the_process in tree.xpath("//process[@name]"):
#    process_name = the_process.attrib['name']
#    for the_mode in the_process.xpath("mode[@name]"):
#      mode_name = the_mode.attrib['name']
#      for the_message in the_mode.xpath("message[@name]"):
#        message_name = the_message.attrib['name']
#        if not message_name in actual_messages:
#          actual_messages.append(message_name)
#  for the_message in message_dictionary.keys():
#    if not the_message in actual_messages:
#      del(message_dictionary[the_message])
##-------end of extra message filtering code-----
  return message_dictionary

def try_float(x):
  try:
    return float(x)
  except:
    return x

class PaparazziIvyDecoder(DataDecoder):
  """
      Decodes Ivy messages.
  """
  name = Str('Ivy Decoder')
  view = View(
    title='Ivy decoder'
  )

  _message_dict = ParseMessages()

  def decode(self, data):
    """
        Decode Ivy input data then assign variables based on a message formatter given by the paparazzi messages.xml (or mercuryX.xml) file.
    """
    data_list = data.split(' ')
    #ac_id = data_list[0]
    
    message_name = data_list[1] 
    values = map(try_float, data_list[2:])
    field_names = [message_name + '_' + s for s in self._message_dict[message_name]]

    data_dict = dict(zip(field_names, values)) 
    return data_dict
    
