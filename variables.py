from enthought.traits.api import HasTraits, Int, Dict, List, Property, Enum, Color, Any, on_trait_change
from enthought.traits.ui.api import View, Item, ValueEditor, TabularEditor
from enthought.traits.ui.tabular_adapter import TabularAdapter
import time

import math, numpy

class VariableTableAdapter(TabularAdapter):
  columns = [('Variable name', 0), ('Value', 1), ('Last update', 2)]
  
  def _get_bg_color(self):
    #value = int(0xFF * self.item[3]/10.0)
    value = 0xA0 if self.item[3] else 0xFF
    return (value, 0xFF, value)

class Variables(HasTraits):
  vars_pool = Dict()
  vars_pool_age = Dict() # has the same keys as vars_pool but maintains the sample number when last updated
  vars_list = List()
  vars_table_list = List()  # a list version of vars_pool maintained for the TabularEditor
  sample_number = Int(0)

  add_var_event = Any()

  view = View(
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
    
    # Make a new age dict for the updated vars and then update our global age dict
    data_dict_age = {}
    for key in data_dict.iterkeys():
      data_dict_age[key] = self.sample_number
    self.vars_pool_age.update(data_dict_age)
    
    # We update into a new dict rather than vars_pool due to pythons pass by reference
    # behaviour, we need a fresh object to put on our array
    new_vars_pool = {}
    new_vars_pool.update(self.vars_pool)
    new_vars_pool.update(data_dict)
    if '' in new_vars_pool: 
      del new_vars_pool[''] # weed out undesirables
    
    self.vars_pool = new_vars_pool
    self.vars_list += [(new_vars_pool, self.sample_number, time.time())]
  
  #@on_trait_change('add_var_event')
  #def add_var_to_plot(self, old, new):
  #  print "woot"

  @on_trait_change('vars_pool')
  def update_vars_table(self, old_pool, new_pool):
    self.vars_table_list = map(lambda (name, val): (name, repr(val), self.vars_pool_age[name], self.vars_pool_age[name] == self.sample_number), list(self.vars_pool.iteritems()))
    time.sleep(0.1)
    self.vars_table_list = map(lambda (name, val): (name, repr(val), self.vars_pool_age[name], False), list(self.vars_pool.iteritems()))
    
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
