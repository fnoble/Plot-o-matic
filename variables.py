from enthought.traits.api import HasTraits, Int, Float, Dict, List, Property, Enum, Color, Instance, Str, Any, on_trait_change, Event, Button
from enthought.traits.ui.api import View, Item, ValueEditor, TabularEditor, HSplit, TextEditor
from enthought.traits.ui.tabular_adapter import TabularAdapter
import time

import math, numpy

expression_context = {}
expression_context.update(numpy.__dict__)


class VariableTableAdapter(TabularAdapter):
  columns = [('Variable name', 0), ('Value', 1)]

class Variables(HasTraits):
  vars_pool = {}
  vars_list = List()
  vars_table_list = List()  # a list version of vars_pool maintained for the TabularEditor
  vars_table_list_update_time = Float(0)
  sample_number = Int(0)
  sample_count = Int(0)
  max_samples = Int(20000)

  add_var_event = Event()

  clear_button = Button('Clear')
  view = View(
           HSplit(
             Item(name = 'clear_button', show_label = False),
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
  
  def new_expression(self, expr):
    return Expression(self, expr)
    
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
    new_vars_pool.update({'sample_num': self.sample_number, 'system_time': time.time()})
    if '' in new_vars_pool: 
      del new_vars_pool[''] # weed out undesirables

    self.vars_pool = new_vars_pool

    if time.time() - self.vars_table_list_update_time > 0.2:
      self.vars_table_list_update_time = time.time()
      self.update_vars_table()

    self.vars_list.append(new_vars_pool)
    self.sample_count = len(self.vars_list)
    if self.sample_count > self.max_samples:
      self.vars_list = self.vars_list[-self.max_samples:]
      self.sample_count = self.max_samples
  
  @on_trait_change('clear_button')
  def clear(self):
    """ Clear all recorded data. """
    self.sample_number = 0
    self.sample_count = 0
    self.vars_list = []
    self.vars_pool = {}
    self.vars_table_list = []

  def update_vars_table(self):
    vars_list_unsorted = [(name, repr(val)) for (name, val) in list(self.vars_pool.iteritems())]
    self.vars_table_list = sorted(vars_list_unsorted, key=(lambda x: x[0].lower()))
    
  def _eval_expr(self, expr, vars_pool=None):
    """
        Returns the value of a python expression evaluated with 
        the variables in the pool in scope. Used internally by
        Expression. Users should use Expression instead as it
        has caching etc.
    """
    if vars_pool == None:
      vars_pool = self.vars_pool

    try:
      data = eval(expr, expression_context, vars_pool)
    except:
      data = None
    return data

  def bound_array(self, first, last):
    if first < 0:
      first += self.sample_number
      if first < 0:
        first = 0
    if last and last < 0:
      last += self.sample_number
    if last == None:
      last = self.sample_number

    return (first, last)

  def _get_array(self, expr, first=0, last=None):
    """
        Returns an array of tuples containing the all the values of an
        the supplied expression and the sample numbers and times corresponding to
        these values. Used internally by Expression, users should use Expression
        directly as it has caching etc.
    """
    data_array = []
    first, last = self.bound_array(first, last)

    data = [self._eval_expr(expr, vs) for vs in self.vars_list[first:last]]
    data = [d for d in data if d is not None]
    
    #try:
    #  data = [try: eval(expr, expression_context, vs); except: pass; for vs in self.vars_list[first:last]]
    #except Exception as e:
    #  print e
    #  data = []

    data_array = numpy.array(data)
    return data_array

class Expression(HasTraits):
  _vars = Instance(Variables)
  _expr = Str('')
  _data_array_cache = numpy.array([])
  _data_array_cache_index = Int(0)

  view = View(Item('_expr', show_label = False, editor=TextEditor(enter_set=True, auto_set=False)))

  def __init__(self, variables, expr, **kwargs):
    HasTraits.__init__(self, **kwargs)
    self._vars = variables
    self.set_expr(expr)

  def set_expr(self, expr):
    if self._expr != expr:
      self._data_array_cache = numpy.array([])
      self._data_array_cache_index = 0
      self._expr = expr

  def get_curr_value(self):
    return self._vars._eval_expr(self._expr)

  def get_array(self, first=0, last=None):
    first, last = self._vars.bound_array(first, last)
    
    if last > self._data_array_cache_index:
      #print "Cache miss of", (last - self._data_array_cache_index)
      self._data_array_cache = numpy.append(self._data_array_cache, self._vars._get_array(self._expr, self._data_array_cache_index, last))
      self._data_array_cache_index = last

    return self._data_array_cache[first:last]
