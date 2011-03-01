from enthought.traits.api import Str, Bool, Enum, List
from enthought.traits.ui.api import View, Item
from data_decoder import DataDecoder

import os
import sys

from xml.etree import ElementTree as ET
import xml.parsers.expat as expat

class ConftronDecoder(DataDecoder):
#class ConftronDecoder():
  """
      Conftron lcm class decoder
  """
  name = Str('Conftron Decoder')
  
  view = View(
    title='Conftron Decoder'
  )
  
  _names = List()

  def struct_of_xml(self, xml_struct):
    struct = []
    # get attributes for each member of the struct
    for field in xml_struct.getchildren():
      attributes = {}
      attributes['name']=field.attrib['name']
      attributes['type']=field.attrib['type']
      try:
        attributes['array']=eval("["+field.attrib['array']+"]")
      except KeyError:
        attributes['array']=None
      try:
        attributes['alt_unit']=field.attrib['alt_unit']
      except KeyError:
        attributes['alt_unit']=None
      try:
        attributes['alt_unit_coeff']=float(field.attrib['alt_unit_coeff'])
      except KeyError:
        attributes['alt_unit_coeff']=None
      struct.append(attributes)
    return struct


  def __init__(self):

    # set up paths
    self.ap_project_root = os.environ.get('AP_PROJECT_ROOT')
    if self.ap_project_root == None:
      raise NameError("please set the AP_PROJECT_ROOT environment variable to use Conftron driver")
    sys.path.append( self.ap_project_root+"/conftron/python" )

    # parse types.xml
    self.structs = {}
    self.enums = []

    for a_type in ET.ElementTree().parse( self.ap_project_root+"/conf/types.xml").getchildren():
      # if it's a struct and we haven't seen it yet, parse it
      if a_type.tag == "message" and a_type.attrib['name'] not in self.structs.keys():
        self.structs[a_type.attrib['name']] = self.struct_of_xml(a_type)
    
      # if it's an enum, and we haven't seen it, parse it
      elif a_type.tag == "enum" and a_type.attrib['name'] not in self.enums:
        self.enums.append(a_type.attrib['name'])

      # if it's a class, loop through the structs/enums and if we haven't seen it yet, parse it
      elif a_type.tag == "class":
        for a_class_type in a_type.getchildren():
          if a_class_type.tag == "message" and a_class_type.attrib['name'] not in self.structs.keys():
            self.structs[a_class_type.attrib['name']] = self.struct_of_xml(a_class_type)
          elif a_class_type.tag == "enum" and a_class_type.attrib['name'] not in self.enums:
            self.enums.append(a_class_type.attrib['name'])


    # write the struct --> dict library
    try:
        os.mkdir(self.ap_project_root+"/conftron/plot-o-matic_autogen")
    except OSError as (errno, strerror):
        if strerror == "File exists":
            pass

    primitive_types = ['double', 'float', 'int8_t', 'int16_t', 'int32_t']

    file = open(self.ap_project_root+"/conftron/plot-o-matic_autogen/dict_of_struct.py",'w')

    # enums
    for enum in self.enums:
      file.write("\ndef "+enum+"(struct):   # enum\n")
      file.write("  return struct.val\n")

    # structs
    for name,struct in self.structs.iteritems():
      file.write("\ndef "+name+"(struct):\n")
      file.write("  str_dict = {}\n")

      for member in struct:
        # primitive types
        if member['type'] in primitive_types:
          file.write("  str_dict[\'"+member['name']+"\'] = struct."+member['name']+"  # primitive type "+member['type']+"\n")          
        
        # non-primitive types
        else:
          # scalars
          if member['array'] == None:
            file.write("  str_dict[\'"+member['name']+"\'] = "+member['type']+"(struct."+member['name']+")\n")
          # arrays
          elif len(member['array']) == 1:
            file.write("  str_dict[\'"+member['name']+"\'] = ["+member['type']+"(_hoochie_momma) for _hoochie_momma in struct."+member['name']+"] # non-primitive array\n")
          # don't handle non-primitive type tensors of order 2 or higher
          else:
            print "Ignoring none-primitive tensor:"
            print member
            file.write("  str_dict[\'"+member['name']+"\'] = None\n")
      file.write("  return str_dict\n")

    file.close()
  
    sys.path.append(self.ap_project_root+"/conftron/plot-o-matic_autogen")
    import dict_of_struct

  def decode(self, message):
    """
        Decodes input from Conftron/LCM messages.
    """

    sys.path.append(self.ap_project_root+"/conftron/plot-o-matic_autogen")

    import dict_of_struct
    try:
      amd = dict_of_struct.__dict__[message['type']](message['message'])
    except TypeError as err:
      print str(err)+", probably something in types.xml changed"
      return None

    # re-enable this when pom can handle structs
    #return {message['name']:amd}

    # for now flatten into a list
    return self.awesome_multilayer_dict_to_boring_flat_dict(message['name'],amd)

  def awesome_multilayer_dict_to_boring_flat_dict(self, top_name, amd):
    bfd = {}
    for name,entry in amd.iteritems():
      if isinstance(entry, dict):
        bfd.update(self.awesome_multilayer_dict_to_boring_flat_dict(top_name+"_"+name, entry))
      elif isinstance(entry, list):
        for k in range(0, len(entry)):
          bfd.update(self.awesome_multilayer_dict_to_boring_flat_dict(top_name+"_"+name+"_"+str(k), entry[k]))
      elif isinstance(entry, tuple):
        for k in range(0, len(entry)):
          bfd.update({top_name+"_"+str(k): entry[k]})
      else:
        bfd[top_name+"_"+name] = entry
    return bfd

  def get_config(self):
    return {'hi':'there'}

  def set_config(self, config):
    return None

if __name__ == '__main__':
  cd = ConftronDecoder()
