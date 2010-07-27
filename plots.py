from enthought.traits.api import HasTraits, List, Str, Float, Bool, Instance, Enum, on_trait_change
from enthought.traits.ui.api import View, Item, ListEditor, HGroup, VGroup, TextEditor
from wx import CallAfter
from matplotlib.figure import Figure
import threading as t
import time

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
  scroll_width = Float(300)
  
  legend = Bool(False)
  legend_pos = Enum(
    'upper left', 'upper right', 'lower left', 
    'lower right', 'right', 'center left', 'center right', 
    'lower center', 'upper center', 'center', 'best'
  )
    
  traits_view = View(
    Item(name = 'name', label = 'Plot name'),
    Item(name = 'expr', label = 'Expression(s)', editor=TextEditor(enter_set=True, auto_set=False)),
    Item(label = 'Use commas\nfor multi-line plots.'),
    HGroup(
      Item(name = 'legend', label = 'Show legend'),
      Item(name = 'legend_pos', show_label = False),
    ),
    VGroup(
      HGroup(
        Item(name = 'x_max', label = 'Max'),
        Item(name = 'x_max_auto', label = 'Auto')
      ),
      HGroup(
        Item(name = 'x_min', label = 'Min'),
        Item(name = 'x_min_auto', label = 'Auto')
      ),
      HGroup(
        Item(name = 'scroll', label = 'Scroll'),
        Item(name = 'scroll_width', label = 'Scroll width'),
      ),      
      label = 'X', show_border = True
    ),
    VGroup(
      HGroup(
        Item(name = 'y_max', label = 'Max'),
        Item(name = 'y_max_auto', label = 'Auto')
      ),
      HGroup(
        Item(name = 'y_min', label = 'Min'),
        Item(name = 'y_min_auto', label = 'Auto')
      ),     
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
      exprs = self.get_exprs()
      if len(exprs) > len(lines):
        for i in range(len(exprs) - len(lines)):
          axes.plot([0], [0])
        lines = axes.get_lines()
      
      max_xs = max_ys = min_xs = min_ys = 0
      
      for n, expr in enumerate(exprs):
        data = self.variables.get_data_array(expr)
      
        xs = [0]
        ys = [0]
        for y, point_no, point_time in data:
          xs += [point_no]
          ys += [y]

        lines[n].set_xdata(xs)
        lines[n].set_ydata(ys)
        
        max_xs = max_xs if (max(xs) < max_xs) else max(xs)
        max_ys = max_ys if (max(ys) < max_ys) else max(ys)
        min_xs = min_xs if (min(xs) > min_xs) else min(xs)
        min_ys = min_ys if (min(ys) > min_ys) else min(ys)
      
      if self.x_max_auto:
        self.x_max = max_xs
      if self.x_min_auto:
        if self.scroll and self.x_max_auto:
          scroll_x_min = self.x_max - self.scroll_width
          self.x_min = scroll_x_min if (scroll_x_min >= 0) else 0
        else:
          self.x_min = min_xs
      if self.y_max_auto:
        self.y_max = max_ys
      if self.y_min_auto:
        self.y_min = min_ys
      
      axes.set_ybound(upper=self.y_max, lower=self.y_min)
      axes.set_xbound(upper=self.x_max, lower=self.x_min)
      
      if self.figure.canvas:
        CallAfter(self.figure.canvas.draw) # wx thread safe call
  
  def get_exprs(self):
    return self.expr.split(',')
  
  @on_trait_change('legend_pos')
  def update_legend_pos(self, old, new):
    """ Move the legend, calls update_legend """
    self.update_legend(None, None)
  
  @on_trait_change('legend')
  def update_legend(self, old, new):
    """ Called when we change the legend display """
    axes = self.figure.gca()
    lines = axes.get_lines()
    exprs = self.get_exprs()
    
    if len(exprs) > 1 and self.legend:
      axes.legend(lines[:len(exprs)], exprs, loc=self.legend_pos)
    else:
      axes.legend_ = None
    
    if self.figure.canvas:
      CallAfter(self.figure.canvas.draw) # wx thread safe call  
    
  @on_trait_change('expr')
  def update_expr(self, old_expr, new_expr):
    """ Called when 'expr' is changed, calls out to update_plot """
    if self.variables:
      self.update_plot()
      self.update_legend(None, None)
  
  @on_trait_change('variables.vars_pool')
  def update_data(self, old_vars_pool, new_vars_pool):
    """ Called when 'vars_pool' is changed in the Variables instance, calls out to update_plot """
    self.update_plot()




class Plots(HasTraits, t.Thread):
  """
      The plots class maintains the list of plots currently being used and provides the
      tabbed view of all the different plots. It will also include functionality to add,
      remove and manage plots. Make sure you initialise it with a Variables instance.
  """
  
  plots = List(Plot)
  variables = Instance(Variables) # Variables instance to provide the data context for all of our plots
  selected_plot = Instance(Plot)
  
  name = Str("Plots") # for thread debugging
  
  _wants_to_terminate = False
  
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
  
  def __init__(self, **kwargs):
    t.Thread.__init__(self)
    HasTraits.__init__(self, **kwargs)
  
  def run(self):
    """ Thread to update plots. """
    while not self._wants_to_terminate:
      if self.selected_plot:
        self.selected_plot.update_plot()
      time.sleep(0.01)
  
  def select_plot(self, plot):
    self.selected_plot = plot
    
  def stop(self):
    self._wants_to_terminate = True
  
  def add_plot(self, plot_expr, name = None):
    """
        Add a plot to the seesion. The plot name defaults to the plot expression.
    """
    if not name:
      name = plot_expr
    plot = Plot(name = name, expr = plot_expr, variables = self.variables)
    self.plots += [plot]




