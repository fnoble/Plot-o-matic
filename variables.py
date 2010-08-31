from enthought.traits.api import HasTraits, Int, Dict, List, Property, Enum, Color, Any, on_trait_change, Event, Button
from enthought.traits.ui.api import View, Item, ValueEditor, TabularEditor, HSplit
from enthought.traits.ui.tabular_adapter import TabularAdapter
import time

import math, numpy

class VariableTableAdapter(TabularAdapter):
  columns = [('Variable name', 0), ('Value', 1)]
  
  #def _get_bg_color(self):
  #  value = (0xFF * self.item[2])/4
  #  return (0xFF, value, value)
  #  pass

class Variables(HasTraits):
  vars_pool = Dict()
  vars_list = List()
  vars_table_list = List()  # a list version of vars_pool maintained for the TabularEditor
  sample_number = Int(0)
  sample_count = Int(0)
  max_samples = Int(20000)

  add_var_event = Event()

  clear_data_button = Button('Clear')
  view = View(
           HSplit(
             Item(name = 'clear_data_button', show_label = False),
             Item(name = 'max_samples', label = 'Max samples'),
             Item(name = 'sample_count', label = 'Samples')
           ),
           Item(
             name = 'vars_table_list',
             editor = TabularEditor(
               adapter = VariableTableAdapter(),
               editable = False,
               dclicked = "add_var_event"
             ),
             resizable = True,
             show_label = False
           ),
           title = 'Variable view',
           resizable = True,
           width = .7,
           height = .2
         )
  
  def update_variables(self, data_dict):
    """
        Receive a dict of variables from a decoder and integrate them
        into our global variable pool.
    """
    self.sample_number += 1
    # We update into a new dict rather than vars_pool due to pythons pass by reference
    # behaviour, we need a fresh object to put on our array
    new_vars_pool = {}
    new_vars_pool.update(self.vars_pool)
    new_vars_pool.update(data_dict)
    if '' in new_vars_pool: 
      del new_vars_pool[''] # weed out undesirables
    
    self.vars_pool = new_vars_pool
    self.vars_list += [(new_vars_pool, self.sample_number, time.time())]
    self.vars_list = self.vars_list[-self.max_samples:]
    self.sample_count = len(self.vars_list)
  
  @on_trait_change('clear_data_button')
  def clear_data(self):
    """ Clear all recorded data. """
    self.sample_number = 0
    self.vars_list = []
    self.vars_pool = {}

  @on_trait_change('vars_pool')
  def update_vars_table(self, old_pool, new_pool):
    vars_list_unsorted = map(lambda (name, val): (name, repr(val)), list(self.vars_pool.iteritems()))
    self.vars_table_list = sorted(vars_list_unsorted, key=(lambda (name, val): name.lower()))
    
  def reset_variables(self):
    self.vars_pool = {}
    
  def eval_expr(self, expr, vars_pool):
    """
        Returns the value of a python expression evaluated with 
        the variables in the pool in scope.
    """
    try:
      data = eval(expr, numpy.__dict__, vars_pool)
    except:
      data = None
    return data
    
  def get_data_array(self, expr, first=0, last=None):
    """
        Returns an array of tuples containing the all the values of an
        the supplied expression and the sample numbers and times corresponding to
        these values.
    """
    data_array = []
    if first < 0:
      first = self.sample_number + first
      if first < 0:
        first = 0
    if last and last < 0:
      last = self.sample_number - last
    for vars_list_item in self.vars_list:
      (vars_pool, sample_num, time) = vars_list_item
      if sample_num > first and (not last or sample_num<last):
        value = self.eval_expr(expr, vars_pool)
        if value != None:
          data_array += [(value, sample_num, time)]
    return data_array
