# ---------------------------------------------------------------------------------
# Traits editor for a Matplotlib Figure instance
# by Gael Varoquaux - BSD licensed
# http://code.enthought.com/projects/traits/docs/html/tutorials/traits_ui_scientific_app.html
# ---------------------------------------------------------------------------------

import wx
import matplotlib
# We want matplotlib to use a wxPython backend
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.api import BasicEditorFactory


class _MPLFigureEditor(Editor):
  """
      A traits UI editor for a Matplotlib Figure instance that displays the
      figure together with the Matplotlib navigation toolbar.
  """
  scrollable  = True

  def init(self, parent):
    """ Initialise the Editor. """
    self.control = self._create_canvas(parent)
    self.set_tooltip()

  def update_editor(self):
    """ 
        Called when the trait that we are editing is changed outside the
        the editor - use this function to update the display.
    """
    # For now we just do nothing as we never really change the figure instance,
    # might be worth adding something here eventually.
    pass

  def _create_canvas(self, parent):
    """ Create the Matplotlib canvas. """
    # The panel lets us add additional controls.
    panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
    sizer = wx.BoxSizer(wx.VERTICAL)
    panel.SetSizer(sizer)
    # Matplotlib commands to create a canvas
    mpl_control = FigureCanvas(panel, -1, self.value)
    sizer.Add(mpl_control, 1, wx.LEFT | wx.TOP | wx.GROW)
    toolbar = NavigationToolbar2Wx(mpl_control)
    sizer.Add(toolbar, 0, wx.EXPAND)
    self.value.canvas.SetMinSize((10,10))
    return panel

class MPLFigureEditor(BasicEditorFactory):
  """
      Editor factory for the _MPLFigureEditor editor class.
  """
  klass = _MPLFigureEditor



# ---------------------------------------------------------------------------------
# Traits editor test/example code
# ---------------------------------------------------------------------------------

if __name__ == "__main__":
  # Testing code:
  # Create a window to demo the editor
  
  from enthought.traits.api import HasTraits, Instance
  from enthought.traits.ui.api import View, Item
  from numpy import sin, cos, linspace, pi

  class Test(HasTraits):
    figure = Instance(Figure, ())

    view = View(
      Item(
        name = 'figure',
        editor = MPLFigureEditor(),
        show_label = False
      ),
      width=400,
      height=300,
      resizable=True
    )

    def __init__(self, **kwargs):
      HasTraits.__init__(self, **kwargs)
      axes = self.figure.add_subplot(111)
      t = linspace(0, 2*pi, 200)
      axes.plot(sin(t)*(1+0.5*cos(11*t)), cos(t)*(1+0.5*cos(11*t)))

  Test().configure_traits()