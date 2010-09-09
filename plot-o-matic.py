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
  
  def start_all(self):
    map(lambda d: d.start(), self.io_drivers)

  def stop_all(self):
    map(lambda d: d.stop(), self.io_drivers)

class TreeHandler(Handler):
  remove_action = Action(name='Remove', action='handler.remove(editor,object)')
  new_io_driver_action = Action(name='Add Input Driver', action='handler.new_io_driver(editor,object)')
  
  def remove(self, editor, object):
    io_driver_object.stop()
    io_drivers.remove(io_driver_object)
    
  def new_io_driver(self, editor, object):
    try:
      print "Adding IO driver"
      #object.io_drivers += [td.TestDriver()]
      print editor.__dict__
      editor.insert_child(0, td.TestDriver())
      print editor.nodes[0].get_children()
      print object.io_drivers
    except Exception as e:
      print e

class Project(HasTraits):
  io_driver_list = Instance(IODriverList)
  variables = Instance(Variables)
  viewers = Instance(Viewers)
  selected_viewer = Instance(Viewer)
  
  viewer_node = TreeNode( 
    node_for  = [Viewer],
    auto_open = True,
    label     = 'name',
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
        view      = View(),
      ),
      TreeNode( 
        node_for  = [IODriver],
        auto_open = True,
        children  = '_decoders',
        label     = 'name',
        add       = [DataDecoder],
        icon_path = 'icons/',
        icon_open = 'input.png',
        icon_group = 'input.png'
      ),
      TreeNode( 
        node_for  = [DataDecoder],
        auto_open = True,
        children  = '',
        label     = 'name',
        icon_path = 'icons/',
        icon_item = 'decoder.png'
      ),
      TreeNode( 
        node_for  = [IODriverList],
        auto_open = True,
        children  = 'viewers',
        label     = '=Viewers',
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
    handler = TreeHandler()
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
      
vs = Variables()
viewers = Viewers(variables = vs)

p0 = Plot(name='Plot0')
p1 = Plot(name='Plot1')
p2 = Plot(name='Plot2')
p3 = Plot(name='Plot3')
p4 = Plot(name='Plot4')

vv = TVTKViewer()

viewers.add_viewer(p0)
viewers.add_viewer(p1)
viewers.add_viewer(p2)
viewers.add_viewer(p3)
viewers.add_viewer(p4)
viewers.add_viewer(vv)

#a = TestDriver()
#f = SimpleFileDriver()
u = UDPDriver()
#stdi = StdinDriver()

#iodl = IODriverList(io_drivers = [stdi], viewers_instance = viewers)
iodl = IODriverList(io_drivers = [u], viewers_instance = viewers)
proj = Project(io_driver_list = iodl, variables = vs, viewers = viewers)
  
#c = CSVDecoder(variables = vs)
#r = RegexDecoder(variables = vs)
#n = NullDecoder(variables = vs)
#s = CStructDecoder(variables = vs)
#spd = SimplePlotDecoder(variables = vs)
jsd = JobySimDecoder(variables = vs)

#f._register_decoder(c)
#u._register_decoder(s)
#u._register_decoder(spd)
u._register_decoder(jsd)
#stdi._register_decoder(spd)
#f._register_decoder(n)
#f._register_decoder(r)

proj.start()
proj.configure_traits()
proj.stop()

if PROFILE:
  print "Generating Statistics"
  yappi.stop()
  stats = yappi.get_stats(yappi.SORTTYPE_TSUB, yappi.SORTORDER_DESCENDING, 300) #yappi.SHOW_ALL)
  for stat in stats: 
      print stat
