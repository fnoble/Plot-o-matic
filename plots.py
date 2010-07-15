from enthought.traits.api import HasTraits, List, Str, Float, Bool, Instance, on_trait_change
from enthought.traits.ui.api import View, Item, ListEditor, HGroup, VGroup
from wx import CallAfter
from matplotlib.figure import Figure

from mpl_figure_editor import MPLFigureEditor
from variables import Variables

figure_view = View(
  Item(
    name = 'figure',
    editor = MPLFigureEditor(),
    show_label = False
  ),
  width = 400,
  height = 400,
  resizable = True
)

class Plot(HasTraits):
  """
      A plot, cointains code to display using a Matplotlib figure and to update itself
      dynamically from a Variables instance (which must be passed in on initialisation).
      The function plotted is calculated using 'expr' which should also be set on init
      and can be any python expression using the variables in the pool.
  """
  
  figure = Instance(Figure, ())
  variables = Instance(Variables)
  name = Str('Plot')
  expr = Str
  
  x_max = Float
  x_max_auto = Bool(True)
  x_min = Float
  x_min_auto = Bool(True)
  y_max = Float
  y_max_auto = Bool(True)
  y_min = Float
  y_min_auto = Bool(True)
  
  scroll = Bool(True)
  scroll_width = Float
    
  traits_view = View(
    Item(name = 'name', label = 'Plot name'),
    Item(name = 'expr', label = 'Plot expression'),
    VGroup(
      HGroup(
        Item(name = 'x_max', label = 'Max'),
        Item(name = 'x_min', label = 'Min')
      ),
      HGroup(
        Item(name = 'x_max_auto', label = 'Auto Max'),
        Item(name = 'x_min_auto', label = 'Auto Min'),
      ),
      HGroup(
        Item(name = 'scroll', label = 'Scroll'),
        Item(name = 'scroll_width', label = 'Scroll Width'),
      ),      
      label = 'X', show_border = True
    ),
    HGroup(
      Item(name = 'y_max', label = 'Max'),
      Item(name = 'y_max_auto', show_label = False),
      Item(name = 'y_min', label = 'Min'),
      Item(name = 'y_min_auto', show_label = False),
      label = 'Y', show_border = True
    ),
    title = 'Plot settings',
    resizable = True
  )
  
  figure_view = View(
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
    # Init code creates an empty plot to be updated later.
    HasTraits.__init__(self, **kwargs)
    axes = self.figure.add_subplot(111)
    axes.plot([0], [0])
  
  def update_plot(self):
    """
        Update the plot from the Variables instance and make a call to wx to
        redraw the figure.
    """
    axes = self.figure.gca()
    lines = axes.get_lines()
    
    if lines:
      data = self.variables.get_data_array(self.expr)
      
      xs = [0]
      ys = [0]
      for y, point_no, point_time in data:
        xs += [point_no]
        ys += [y]

      lines[0].set_xdata(xs)
      lines[0].set_ydata(ys)
      
      if self.x_max_auto:
        self.x_max = max(xs)
      if self.x_min_auto:
        self.x_min = min(xs)
      if self.y_max_auto:
        self.y_max = max(ys)
      if self.y_min_auto:
        self.y_min = min(ys)
      
      axes.set_ybound(upper=self.y_max, lower=self.y_min)
      axes.set_xbound(upper=self.x_max, lower=self.x_min)
      
      if self.figure.canvas:
        CallAfter(self.figure.canvas.draw) # wx thread safe call
    
  @on_trait_change('expr')
  def update_expr(self, old_expr, new_expr):
    """ Called when 'expr' is changed, calls out to update_plot """
    if self.variables:
      self.update_plot()
  
  @on_trait_change('variables.vars_pool')
  def update_data(self, old_vars_pool, new_vars_pool):
    """ Called when 'vars_pool' is changed in the Variables instance, calls out to update_plot """
    self.update_plot()




class Plots(HasTraits):
  """
      The plots class maintains the list of plots currently being used and provides the
      tabbed view of all the different plots. It will also include functionality to add,
      remove and manage plots. Make sure you initialise it with a Variables instance.
  """
  
  plots = List(Plot)
  variables = Instance(Variables) # Variables instance to provide the data context for all of our plots
  
  view = View(
    Item(
      name = 'plots',
      style= 'custom',
      show_label = False,
      editor = ListEditor(
        use_notebook = True,
        deletable = True,
        export = 'DockShellWindow',
        page_name = '.name'
      )
    )
  )
  
  def add_plot(self, plot_expr, name = None):
    """
        Add a plot to the seesion. The plot name defaults to the plot expression.
    """
    if not name:
      name = plot_expr
    plot = Plot(name = name, expr = plot_expr, variables = self.variables)
    self.plots += [plot]




