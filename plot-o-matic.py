#!/usr/bin/env python

# If wxversion is installed, make sure we are
# using wx >= 2.8
try:
  import wxversion
  wxversion.select('2.8')
except ImportError:
  pass

from io_driver import IODriver
from data_decoder import DataDecoder
from viewers import Viewer, Viewers
from variables import Variables

from plugins.io_drivers_all import *
from plugins.decoders_all import *
from plugins.viewers_all import *

from enthought.traits.api import HasTraits, Str, Regex, List, Instance, DelegatesTo
from enthought.traits.ui.api import TreeEditor, TreeNode, View, Item, VSplit, \
  HGroup, Handler, Group, Include, ValueEditor, HSplit, ListEditor, InstanceEditor
from enthought.traits.ui.menu import Menu, Action, Separator
#from enthought.traits.ui.wx.tree_editor import NewAction, CopyAction, CutAction, \
#  PasteAction, DeleteAction, RenameAction

PROFILE = False
if PROFILE:
  import yappi
  yappi.start()

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



class TreeHandler(Handler):

  remove_io_driver_action = Action(name='Remove', action='handler.remove_io_driver(editor,object)')
  add_io_driver_actions_menu = Instance(Menu)

  remove_decoder_action = Action(name='Remove', action='handler.remove_decoder(editor,object)')
  add_decoder_actions_menu = Instance(Menu)

  remove_viewer_action = Action(name='Remove', action='handler.remove_viewer(editor,object)')
  add_viewer_actions_menu = Instance(Menu)

  def _add_io_driver_actions_menu_default(self):
    actions = []
    for io_driver_plugin in find_io_driver_plugins():
      actions += [Action(
        name = io_driver_plugin.__name__,
        action = 'handler.add_io_driver(editor,object,"%s")' % io_driver_plugin.__name__
      )]
    return Menu(name = 'Add', *actions)

  def remove_io_driver(self, editor, io_driver_object):
    io_driver_list = editor._menu_parent_object
    io_driver_list._remove_io_driver(io_driver_object)
    editor.update_editor()

  def add_io_driver(self, editor, io_driver_list, new_io_driver_name):
    new_io_driver = get_io_driver_plugin_by_name(new_io_driver_name)()
    io_driver_list._add_io_driver(new_io_driver)
    editor.update_editor()

  def _add_decoder_actions_menu_default(self):
    actions = []
    for decoder_plugin in find_decoder_plugins():
      actions += [Action(
        name = decoder_plugin.__name__,
        action = 'handler.add_decoder(editor,object,"%s")' % decoder_plugin.__name__
      )]
    return Menu(name = 'Add', *actions)

  def remove_decoder(self, editor, decoder_object):
    parent_io_driver = editor._menu_parent_object
    parent_io_driver._remove_decoder(decoder_object)
    editor.update_editor()

  def add_decoder(self, editor, io_driver, decoder_name):
    io_driver_list = editor._menu_parent_object
    new_decoder = get_decoder_plugin_by_name(decoder_name)(variables = io_driver_list.variables)
    io_driver._add_decoder(new_decoder)
    editor.update_editor()
    
  def _add_viewer_actions_menu_default(self):
    actions = []
    for viewer_plugin in find_viewer_plugins():
      actions += [Action(
        name = viewer_plugin.__name__,
        action = 'handler.add_viewer(editor,object,"%s")' % viewer_plugin.__name__
      )]
    return Menu(name = 'Add', *actions)

  def remove_viewer(self, editor, viewer_object):
    viewers = editor._menu_parent_object.viewers_instance
    viewers._remove_viewer(viewer_object)
    editor.update_editor()

  def add_viewer(self, editor, object, viewer_name):
    new_viewer = get_viewer_plugin_by_name(viewer_name)()
    object.viewers_instance._add_viewer(new_viewer)
    editor.update_editor()
    

vs = Variables()
viewers = Viewers(variables = vs)

#a = TestDriver()
#f = SimpleFileDriver()
u = UDPDriver()
#stdi = StdinDriver()

iodl = IODriverList(io_drivers = [u], variables = vs, viewers_instance = viewers)

tree_handler = TreeHandler()

class PlotOMatic(HasTraits):
  io_driver_list = Instance(IODriverList)
  variables = Instance(Variables)
  viewers = Instance(Viewers)
  selected_viewer = Instance(Viewer)
  

  viewer_node = TreeNode( 
    node_for  = [Viewer],
    auto_open = True,
    label     = 'name',
    menu      = Menu( tree_handler.remove_viewer_action ),
    icon_path = 'icons/',
    icon_item = 'plot.png'
  )
 
  tree_editor = TreeEditor(
    nodes = [
      TreeNode( 
        node_for  = [IODriverList],
        auto_open = True,
        children  = 'io_drivers',
        label     = '=Input Drivers',
        menu      = Menu( tree_handler.add_io_driver_actions_menu ),
        view      = View(),
      ),
      TreeNode( 
        node_for  = [IODriver],
        auto_open = True,
        children  = '_decoders',
        label     = 'name',
        add       = [DataDecoder],
        menu      = Menu(
          tree_handler.remove_io_driver_action,
          tree_handler.add_decoder_actions_menu
        ),
        icon_path = 'icons/',
        icon_open = 'input.png',
        icon_group = 'input.png'
      ),
      TreeNode( 
        node_for  = [DataDecoder],
        auto_open = True,
        children  = '',
        label     = 'name',
        menu      = Menu( tree_handler.remove_decoder_action ),
        icon_path = 'icons/',
        icon_item = 'decoder.png'
      ),
      TreeNode( 
        node_for  = [IODriverList],
        auto_open = True,
        children  = 'viewers',
        label     = '=Viewers',
        menu      = Menu( tree_handler.add_viewer_actions_menu ),
        view      = View()
      ),
      viewer_node
    ],
    hide_root = True,
    orientation = 'vertical'
  )

  view = View(
    HSplit(
      Item(
        name = 'io_driver_list',
        editor = tree_editor,
        resizable = True,
        show_label = False,
        width = .32
      ),
      VSplit(
        Item(
          name = 'selected_viewer',
          style = 'custom',
          resizable = True,
          show_label = False,
          editor = InstanceEditor(
            view = 'view'
          )
        ),
        Item(
          name = 'variables', 
          show_label = False,
          style = 'custom',
          height = .3
        )
      )
    ),
    title = 'Plot-o-matic',
    resizable = True,
    width = 1000,
    height = 600,
    handler = tree_handler
  )
  
  def __init__(self, **kwargs):
    HasTraits.__init__(self, **kwargs)
    self.viewer_node.on_select = self.click_viewer
    
  def click_viewer(self, viewer):
    self.selected_viewer = viewer
    self.viewers.select_viewer(viewer)

  def start(self):
    self.io_driver_list.start_all()
    self.viewers.start()

  def stop(self):
    self.viewers.stop()
    self.io_driver_list.stop_all()
      

p0 = Plot(name='Plot0')
p1 = MPLPlot(name='Plot1')
p2 = Plot(name='Plot2')
p3 = Plot(name='Plot3')
p4 = Plot(name='Plot4')

vv = TVTKViewer()

viewers._add_viewer(p0)
viewers._add_viewer(p1)
viewers._add_viewer(p2)
viewers._add_viewer(p3)
viewers._add_viewer(p4)
viewers._add_viewer(vv)

#iodl = IODriverList(io_drivers = [stdi], viewers_instance = viewers)
proj = PlotOMatic(io_driver_list = iodl, variables = vs, viewers = viewers)
  
#c = CSVDecoder()
#r = RegexDecoder()
#n = NullDecoder()
#s = CStructDecoder()
#spd = SimplePlotDecoder()
jsd = JobySimDecoder()

#f._add_decoder(c)
#u._add_decoder(s)
#u._add_decoder(spd)
u._add_decoder(jsd)
#stdi._add_decoder(spd)
#f._add_decoder(n)
#f._add_decoder(r)

proj.start()
proj.configure_traits()
proj.stop()

if PROFILE:
  print "Generating Statistics"
  yappi.stop()
  stats = yappi.get_stats(yappi.SORTTYPE_TSUB, yappi.SORTORDER_DESCENDING, 300) #yappi.SHOW_ALL)
  for stat in stats: 
      print stat
