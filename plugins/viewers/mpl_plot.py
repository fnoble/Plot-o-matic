from enthought.traits.api import HasTraits, List, Str, Float, Bool, Instance, Enum, on_trait_change
from enthought.traits.ui.api import View, Item, ListEditor, HGroup, VGroup, TextEditor
from wx import CallAfter
from matplotlib.figure import Figure
import matplotlib.font_manager

from mpl_figure_editor import MPLFigureEditor

from viewers import Viewer
from variables import Expression

class MPLPlot(Viewer):
  """
      A plot, cointains code to display using a Matplotlib figure and to update itself
      dynamically from a Variables instance (which must be passed in on initialisation).
      The function plotted is calculated using 'expr' which should also be set on init
      and can be any python expression using the variables in the pool.
  """
  name = Str('MPL Plot')
  figure = Instance(Figure, ())
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
  
  legend_prop = matplotlib.font_manager.FontProperties(size=8)
  
  def start(self):
    # Init code creates an empty plot to be updated later.
    axes = self.figure.add_subplot(111)
    axes.plot([0], [0])
  
  def update(self):
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
        first = 0
        last = None
        if self.scroll and self.x_min_auto and self.x_max_auto:
          first = -self.scroll_width
        if not self.x_min_auto:
          first = int(self.x_min)
        if not self.x_max_auto:
          last = int(self.x_max) + 1

        ys = self.variables.new_expression(expr).get_array(first, last)
        
        if len(ys) != 0:
          xs = self.variables.new_expression('sample_num').get_array(first, last)
        else:
          xs = [0]
          ys = [0]

        if len(xs) != len(ys):
          print "MPL Plot: x and y arrays different sizes!!! Ignoring (but fix me soon)."
          return

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
  
      axes.set_xbound(upper=self.x_max, lower=self.x_min)
      axes.set_ybound(upper=self.y_max*1.1, lower=self.y_min*1.1)
      
      self.draw_plot()

  def get_exprs(self):
    return self.expr.split(',')

  def add_expr(self, expr):
    if self.expr == '' or self.expr[:-1] == ',':
      self.expr += expr
    else:
      self.expr += ',' + expr
    
  def draw_plot(self):
    if self.figure.canvas:
      CallAfter(self.figure.canvas.draw)
  
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
  
    if len(exprs) >= 1 and self.legend:
      axes.legend(lines[:len(exprs)], exprs, loc=self.legend_pos, prop=self.legend_prop)
    else:
      axes.legend_ = None
    
    self.draw_plot()
    
  #@on_trait_change('expr')
  #def update_expr(self, old_expr, new_expr):
  #  """ Called when 'expr' is changed, calls out to update_plot """
  #  if self.variables:
  #    self.update_plot()
  #    self.update_legend(None, None)
