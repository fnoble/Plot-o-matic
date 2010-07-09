import plugins.io_drivers.test as td
import plugins.io_drivers.simple_file as sf
import plugins.decoders.csv_decoder as csvd
import plugins.decoders.null_decoder as nulld
import inspect as ins
from io_driver import IODriver
from data_decoder import DataDecoder


from enthought.traits.api \
    import HasTraits, Str, Regex, List, Instance
from enthought.traits.ui.api \
    import TreeEditor, TreeNode, View, Item, VSplit, \
           HGroup, Handler, Group
from enthought.traits.ui.menu \
    import Menu, Action, Separator
from enthought.traits.ui.wx.tree_editor \
    import NewAction, CopyAction, CutAction, \
           PasteAction, DeleteAction, RenameAction

class IODriverList(HasTraits, Handler):
  """
      Maintains the list of input drivers currently in use and provides
      facilities to add and remove drivers.
  """
  io_drivers = List(IODriver)
  
  remove_action = Action(name='Remove', action='handler.remove(editor,object)')
  new_action = Action(name='Add Input Driver', action='handler.new(editor,object)')
  
  def remove(self, editor, io_driver_object):
    io_driver_object.stop()
    io_driver.remove(io_driver_object)
    
  def new(self, editor, root_object):
    print "Adding IO driver"
    io_drivers += [IODriver()]

class Project(HasTraits):
  name = Str('foo')
  io_driver_list = Instance(IODriverList)
  
  # Tree editor
  tree_editor = TreeEditor(
    nodes = [
      TreeNode( 
        node_for  = [IODriverList],
        auto_open = True,
        children  = 'io_drivers',
        label     = '=Input Drivers',
        view      = View(),
        menu      = Menu(self.io_driver_list.new_action)
      ),
      TreeNode( 
        node_for  = [IODriver],
        auto_open = True,
        children  = '_decoders',
        label     = 'name',
        menu      = Menu( 
          NewAction,
          Separator(),
          self.io_driver_list.remove_action,
          Separator(),
          RenameAction
        ),
        add       = [DataDecoder]
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
      )
    ]
  )

  # The main view
  view = View(
    Group(
      Item(
        name = 'io_driver_list',
        editor = tree_editor,
        resizable = True,
        show_label = False
      )
    ),
    handler = self.io_driver_list,
    title = 'Plot-o-matic',
    resizable = True,
    width = .7,
    height = .5 
  )

a = td.TestDriver()
f = sf.SimpleFileDriver()

iodl = IODriverList(io_drivers = [a, f])
proj = Project(io_driver_list = iodl)
  
c = csvd.CSVDecoder()
n = nulld.NullDecoder()

a._register_decoder(c)
a._register_decoder(n)
a.start()
f.start()

proj.configure_traits()

a.stop()
f.stop()