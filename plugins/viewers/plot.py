from enthought.traits.api import Str, Range, HasTraits, Instance, Dict, Float, Bool, on_trait_change, List
from enthought.traits.ui.api import Item, View, HGroup, VGroup, TextEditor

import enthought.chaco.api as chaco
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.tools.api import PanTool, ZoomTool, LegendTool, TraitsTool, DragZoom

from viewers import Viewer
from variables import Expression

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


class Plot(Viewer):
  name = Str('Plot')

  plot = Instance(chaco.Plot)
  plot_data = Instance(chaco.ArrayPlotData)
  
  y_exprs = List(Instance(Expression))
  x_expr = Instance(Expression)
  
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
    Item(label = 'Use commas\nfor multi-line plots.'),
    Item(name = 'legend', label = 'Show legend'),
    VGroup(
      Item(name = 'x_expr', label = 'Expression', style = 'custom'),
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
      Item(name = 'y_exprs', label = 'Expression(s)', style = 'custom'),
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
  
  view = View(
    Item('plot', editor=ComponentEditor(), show_label=False),
    resizable = True
  )

  @on_trait_change('name')
  def update_name(self, new_name):
    self.plot.title = new_name
    self.plot.request_redraw()

  @on_trait_change('x_label')
  def update_x_label(self, new_name):
    return
    self.plot.index_axis.title = new_name
    self.plot.request_redraw()
    
  @on_trait_change('y_label')
  def update_y_label(self, new_name):
    return
    self.plot.value_axis.title = new_name
    self.plot.request_redraw()

  def start(self):
    self.plot_data = chaco.ArrayPlotData()
    self.plot = chaco.Plot(self.plot_data, title=self.name, auto_colors=colours_list)
    self.plot.value_range.tight_bounds = False
    #legend = chaco.Legend(component=self.plot, padding=10, align="ul")
    #legend.tools.append(LegendTool(legend, drag_button="right"))
    #self.plot.overlays.append(legend)
    #self.update_expr()
    self.x_expr = self.variables.new_expression('i')
    self.y_exprs = [self.variables.new_expression('0.5')]
    ys = self.y_exprs[0].get_array()
    self.plot_data.set_data('y', ys)
    self.plot_data.set_data('x', range(len(ys)))
    self.plot.plot(('x', 'y'), name = 'y', style='line', color='auto')

  @on_trait_change('y_exprs')
  def update_y_exprs(self):
    self.update()

  @on_trait_change('x_expr')
  def update_x_expr(self):
    self.update()

  def update(self):
    if len(self.y_exprs) >= 1:
      ys = self.y_exprs[0].get_array()
      xs = range(len(ys))
      self.plot_data.set_data('y', ys)
      self.plot_data.set_data('x', xs)
      self.plot.request_redraw()


