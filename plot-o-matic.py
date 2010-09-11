#!/usr/bin/env python

# If wxversion is installed, make sure we are
# using wx >= 2.8
try:
  import wxversion
  wxversion.select('2.8')
except ImportError:
  pass

import plugins.io_drivers.test as td
import plugins.io_drivers.simple_file as sf
import plugins.io_drivers.udp as udpd
import plugins.io_drivers.stdin as stdind
import plugins.io_drivers.iv as iv
import plugins.decoders.csv_decoder as csvd
import plugins.decoders.regex_decoder as rxd
import plugins.decoders.null_decoder as nulld
import plugins.decoders.cstruct_decoder as structd
import plugins.decoders.simpleplot as sp
import plugins.decoders.jobysim_decoder as js
import plugins.decoders.paparazzi_ivy_decoder as pivd
import inspect as ins
from io_driver import IODriver
from data_decoder import DataDecoder
from variables import Variables
from plots import Plots, Plot, figure_view

from enthought.traits.api \
    import HasTraits, Str, Regex, List, Instance, DelegatesTo
from enthought.traits.ui.api \
    import TreeEditor, TreeNode, View, Item, VSplit, \
           HGroup, Handler, Group, Include, ValueEditor, HSplit, ListEditor, InstanceEditor
from enthought.traits.ui.menu \
    import Menu, Action, Separator
from enthought.traits.ui.wx.tree_editor \
    import NewAction, CopyAction, CutAction, \
           PasteAction, DeleteAction, RenameAction

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
  plots = DelegatesTo('plots_instance')
  plots_instance = Instance(Plots)
  
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
  plots = Instance(Plots)
  visible_plots = List(Plot)
  selected_plot = Instance(Plot)
  
  plot_node = TreeNode( 
    node_for  = [Plot],
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
        menu      = Menu(TreeHandler.new_io_driver_action)
      ),
      TreeNode( 
        node_for  = [IODriver],
        auto_open = True,
        children  = '_decoders',
        label     = 'name',
        menu      = Menu( 
          NewAction,
          Separator(),
          TreeHandler.remove_action,
          Separator(),
          RenameAction
        ),
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
        menu      = Menu(
          DeleteAction,
          Separator(),
          RenameAction
        ),
        icon_path = 'icons/',
        icon_item = 'decoder.png'
      ),
      TreeNode( 
        node_for  = [IODriverList],
        auto_open = True,
        children  = 'plots',
        label     = '=Plots',
        view      = View()
      ),
      plot_node
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
        #Item(
        #  name = 'visible_plots',
        #  style= 'custom',
        #  show_label = False,
        #  editor = ListEditor(
        #    use_notebook = True,
        #    deletable = True,
        #    export = 'DockShellWindow',
        #    page_name = '.name',
        #    view = 'figure_view',
        #    selected = 'selected_plot'
        #  )
        #),
        Item(
          name = 'selected_plot',
          style = 'custom',
          resizable = True,
          show_label = False,
          editor = InstanceEditor(
            view = 'figure_view'
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
    self.plot_node.on_select = self.click_plot
    
  def click_plot(self, plot):
    if plot not in self.visible_plots:
      self.visible_plots = [plot] + self.visible_plots
    self.selected_plot = plot
    self.plots.select_plot(plot)
      
vs = Variables()
pls = Plots(variables = vs)
#pls.add_plot('a+b')
#pls.add_plot('c+d')
#pls.add_plot('sv1,sv2,sv3,sv4,sv5,sv6,sv7,sv8,sv9,sv10,sv11,sv12,sv13,sv14,sv15,sv16,sv17,sv18,sv19,sv20,sv21,sv22,sv23,sv24,sv25,sv26,sv27,sv28,sv29,sv30,sv31,sv32', name='SNRs')
#pls.add_plot('a,b,c,d', name='SNRs')
#pls.add_plot('corrs[0],corrs[1],corrs[2],corrs[3],corrs[4],corrs[5],corrs[6],corrs[7],corrs[8],corrs[9],corrs[10],corrs[11],corrs[12],corrs[13],corrs[14],corrs[15],corrs[16],corrs[17],corrs[18],corrs[19],corrs[20],corrs[21],corrs[22],corrs[23],corrs[24],corrs[25],corrs[26],corrs[27],corrs[28],corrs[29],corrs[30],corrs[31]', name='Corrections')
#pls.add_plot('snrs[0],snrs[1],snrs[2],snrs[3],snrs[4],snrs[5],snrs[6],snrs[7],snrs[8],snrs[9],snrs[10],snrs[11],snrs[12],snrs[13],snrs[14],snrs[15],snrs[16],snrs[17],snrs[18],snrs[19],snrs[20],snrs[21],snrs[22],snrs[23],snrs[24],snrs[25],snrs[26],snrs[27],snrs[28],snrs[29],snrs[30],snrs[31]', name='SNRs')
#pls.add_plot('corrs[0]', name='Corrections')
#pls.add_plot('snrs[0]', name='SNRs')

pls.add_plot('', name='Plot0')
pls.add_plot('', name='Plot1')
pls.add_plot('', name='Plot2')
pls.add_plot('', name='Plot3')
pls.add_plot('', name='Plot4')

#a = td.TestDriver()
#f = sf.SimpleFileDriver()
#u = udpd.UDPDriver()
ivd = iv.IvyDriver()
#stdi = stdind.StdinDriver()

#iodl = IODriverList(io_drivers = [stdi], plots_instance = pls)
iodl = IODriverList(io_drivers = [ivd], plots_instance = pls)
proj = Project(io_driver_list = iodl, variables = vs, plots = pls)
  
#c = csvd.CSVDecoder(variables = vs)
#r = rxd.RegexDecoder(variables = vs)
#n = nulld.NullDecoder(variables = vs)
pd = pivd.PaparazziIvyDecoder(variables = vs)
#s = structd.CStructDecoder(variables = vs)
#spd = sp.SimplePlotDecoder(variables = vs)
#jsd = js.JobySimDecoder(variables = vs)

#f._register_decoder(c)
#u._register_decoder(s)
#u._register_decoder(spd)
#u._register_decoder(jsd)
#stdi._register_decoder(spd)
#f._register_decoder(n)
#f._register_decoder(r)
ivd._register_decoder(pd)

iodl.start_all()
pls.start()

proj.configure_traits()

pls.stop()
iodl.stop_all()

if PROFILE:
  print "Generating Statistics"
  yappi.stop()
  stats = yappi.get_stats(yappi.SORTTYPE_TTOTAL, yappi.SORTORDER_DESCENDING, 300) #yappi.SHOW_ALL)
  for stat in stats: 
      print stat
