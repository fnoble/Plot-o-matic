from enthought.traits.api import Str, Bool, Enum, Float, HasTraits, Instance, on_trait_change, List, Array, Property, DelegatesTo, Dict
from enthought.traits.ui.api import Group, VGroup, HGroup, Item, View, TextEditor, ListEditor

import enthought.chaco.api as chaco
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.tools.api import PanTool, ZoomTool, LegendTool, \
        TraitsTool, DragZoom

import threading as t
import time

from variables import Variables

figure_view = View(
  Item('plot', editor=ComponentEditor(), show_label=False),
  resizable = True,
  width = 400,
  height = 400
)
"""
colours_list = [
  (0xED,0xD4,0x00),
  (0xF5,0x79,0x00),
  (0xC1,0x7D,0x11),
  (0x73,0xD2,0x16),
  (0x34,0x65,0xA4),
  (0x75,0x50,0x7B),
  (0xCC,0x00,0x00),
  (0x2E,0x34,0x36),
]
"""
colours_list = ['red', 'blue', 'green']

class Plot(HasTraits):
  """
      A plot, cointains code to display using a Matplotlib figure and to update itself
      dynamically from a Variables instance (which must be passed in on initialisation).
      The function plotted is calculated using 'expr' which should also be set on init
      and can be any python expression using the variables in the pool.
  """
  plot = Instance(chaco.Plot)
  plot_data = Instance(chaco.ArrayPlotData)
  
  variables = Instance(Variables)
  expr_last_update = Dict
  name = Str('Plot')
  expr = Str
  
  x_label = Str
  x_max = Float
  x_max_auto = Bool(True)
  x_min = Float
  x_min_auto = Bool(True)
  
  y_label = Str
  y_max = Float
  y_max_auto = Bool(True)
  y_min = Float
  y_min_auto = Bool(True)
  
  scroll = Bool(True)
  scroll_width = Float(300)
  
  legend = Bool(False)
    
  traits_view = View(
    Item(name = 'name', label = 'Plot name'),
    Item(name = 'expr', label = 'Expression(s)', editor=TextEditor(enter_set=True, auto_set=False)),
    Item(label = 'Use commas\nfor multi-line plots.'),
    Item(name = 'legend', label = 'Show legend'),
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
      Item(name = 'x_label', label = 'Label'),
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
      Item(name = 'y_label', label = 'Label'),
      label = 'Y', show_border = True
    ),
    title = 'Plot settings',
    resizable = True
  )
  
  figure_view = figure_view
  visible = Bool(False)
  
  def __init__(self, **kwargs):
    HasTraits.__init__(self, **kwargs)
    self.plot_data = chaco.ArrayPlotData()
    self.plot = chaco.Plot(self.plot_data, title=self.name, auto_colors=colours_list)
    self.plot.value_range.tight_bounds = False
    #legend = chaco.Legend(component=self.plot, padding=10, align="ul")
    #legend.tools.append(LegendTool(legend, drag_button="right"))
    #self.plot.overlays.append(legend)
    self.update_expr(None, None)
    
  @on_trait_change('name')
  def update_name(self, new_name):
    self.plot.title = new_name
    self.plot.request_redraw()
    
  @on_trait_change('x_label')
  def update_x_label(self, new_name):
    self.plot.index_axis.title = new_name
    self.plot.request_redraw()
    
  @on_trait_change('y_label')
  def update_y_label(self, new_name):
    self.plot.value_axis.title = new_name
    self.plot.request_redraw()
    
  def update_plot_data(self, expr):
    data = self.variables.get_data_array(expr, first=self.expr_last_update[expr])
    self.expr_last_update[expr] += len(data)
    
    xs = []
    ys = []
    for y, point_no, point_time in data:
      xs += [point_no]
      ys += [y]
    
    if self.plot_data.get_data(expr):
      ys = self.plot_data.get_data(expr) + ys
    #if self.plot_data.get_data('x'):
    #  xs = self.plot_data.get_data('x') + xs
    self.plot_data.set_data(expr, ys)
    self.plot_data.set_data('x', range(len(ys)))
    
    #print zip(self.plot_data.get_data('x'), self.plot_data.get_data(expr))
  
  def update_plot(self):
    """
        Update the plot from the Variables instance.
    """
    if self.plot_data:
      for expr in self.get_exprs():
        self.update_plot_data(expr)
      self.plot.request_redraw()
    

  def get_exprs(self):
    return self.expr.split(',')

  def add_expr(self, expr):
    if self.expr == '' or self.expr[:-1] == ',':
      self.expr += expr
    else:
      self.expr += ',' + expr

  @on_trait_change('expr')
  def update_expr(self, old_expr, new_expr):
    """ Called when 'expr' is changed """
    if self.variables:
      exprs = self.get_exprs()
      plot_names = list(self.plot.plots.iterkeys())
      # add new expressions to plot
      for new_expr in [expr for expr in exprs if expr not in plot_names]:
        print "Adding lines:", new_expr
        self.expr_last_update[new_expr] = 0
        self.update_plot_data(new_expr)
        self.plot.plot(('x', new_expr), name = new_expr, style='line', color='auto')
      # remove old ones
      for old_plot in [plot_name for plot_name in plot_names if plot_name not in exprs]:
        print "Removing lines:", old_plot
        self.plot.delplot(old_plot)
        self.plot_data.del_data(old_plot)
        del self.expr_last_update[old_plot]
      self.update_plot()
      print self.plot_data.list_data()
      print list(self.plot.plots.iterkeys())
      print self.get_exprs()
  
  @on_trait_change('variables.vars_pool')
  def update_data(self):
    """ Called when 'vars_pool' is changed in the Variables instance, calls out to update_plot """
    if self.visible:
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
  
  @on_trait_change("variables.add_var_event")
  def add_to_curr_plot(self, evt):
    #print evt.item[0]
    if self.selected_plot:
      self.selected_plot.add_expr(evt.item[0])

  def run(self):
    """ Thread to update plots. """
    return
    while not self._wants_to_terminate:
      if self.selected_plot:
        self.selected_plot.update_plot()
      time.sleep(0.2)
  
  def select_plot(self, plot):
    if self.selected_plot:
      self.selected_plot.visible = False
    plot.visible = True
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




