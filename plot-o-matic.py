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

class IODriverList(HasTraits):
  name = Str('bar')
  io_drivers = List(IODriver)

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
        menu      = Menu(NewAction),
        add       = [IODriver, td.TestDriver, sf.SimpleFileDriver]
      ),
      TreeNode( 
        node_for  = [IODriver],
        auto_open = True,
        children  = '_decoders',
        label     = 'name',
        menu      = Menu( 
          NewAction,
          Separator(),
          DeleteAction,
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