from enthought.traits.api import HasTraits, Int, Float, Bool, Dict, List, Property, Enum, Color, Instance, Str, Any, on_trait_change, Event, Button, BaseStr
from enthought.traits.ui.api import View, Item, ValueEditor, TabularEditor, HSplit, TextEditor
from enthought.traits.ui.tabular_adapter import TabularAdapter
import time

import math, numpy
import cPickle as pickle

expression_context = {}
expression_context.update(numpy.__dict__)


def update_context(context):
  expression_context.update(context)

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

  start_time = time.time()
  
  add_var_event = Event()

  expressions = List()

  vars_table_update = Bool(True)

  clear_button = Button('Clear')
  view = View(
           HSplit(
             Item(name = 'clear_button', show_label = False),
             Item(name = 'max_samples', label = 'Max samples'),
             Item(name = 'sample_count', label = 'Samples'),
             Item(name = 'vars_table_update', label = 'Update variables view')
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
    new_expression = Expression(self, expr)
    self.expressions.append(new_expression)
    return new_expression
    
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
    new_vars_pool.update({'sample_num': self.sample_number, 'system_time': time.time(), 'time': time.time() - self.start_time})
    if '' in new_vars_pool: 
      del new_vars_pool[''] # weed out undesirables

    self.vars_list.append(new_vars_pool)
    self.update_vars_list()

  def update_vars_list(self): 
    self.vars_pool = self.vars_list[-1]

    if time.time() - self.vars_table_list_update_time > 0.2:
      self.vars_table_list_update_time = time.time()
      self.update_vars_table()

    self.sample_count = len(self.vars_list)
    if self.sample_count > self.max_samples:
      self.vars_list = self.vars_list[-self.max_samples:]
      self.sample_count = self.max_samples
      
  @on_trait_change('clear_button')
  def clear(self):
    """ Clear all recorded data. """
    self.sample_number = 0
    self.vars_list = [{}]
    self.update_vars_list()
    self.update_vars_table()
    self.start_time = time.time()

    for expression in self.expressions:
      expression.clear_cache()

  def save_data_set(self, filename):
    fp = open(filename, 'wb')
    pickle.dump(self.vars_list, fp, True)
    fp.close() 

  def open_data_set(self, filename):
    fp = open(filename, 'rb')
    self.vars_list = pickle.load(fp)
    fp.close() 
    
    self.update_vars_list()
    self.update_vars_table()
    self.sample_number = self.sample_count
    # spoof start time so that we start where we left off
    self.start_time = time.time() - self.vars_list[-1]['time']

  def update_vars_table(self):
    if self.vars_table_update:
      vars_list_unsorted = [(name, repr(val)) for (name, val) in list(self.vars_pool.iteritems())]
      self.vars_table_list = sorted(vars_list_unsorted, key=(lambda x: x[0].lower()))
  
  def test_expr(self, expr):
    is_ok = (True, '')
    try:
      eval(expr, expression_context, self.vars_pool)
    except Exception as e:
      is_ok = (False, repr(e))
    return is_ok

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

    first, last = self.bound_array(first, last)
    vars_list_offset = self.sample_number - self.sample_count
    if expr in self.vars_pool:
      data = [vs.get(expr) for vs in self.vars_list[first-vars_list_offset:last-vars_list_offset]]
    else:
      data = [self._eval_expr(expr, vs) for vs in self.vars_list[first-vars_list_offset:last-vars_list_offset]]
    data = [0.0 if d is None else d for d in data]
    
    data_array = numpy.array(data)
    return data_array

class ExpressionString(BaseStr):
  default_value = ''

  def validate(self, object, name, value):
    value = BaseStr.validate(self, object, name, value)
    is_ok, self.info_text = object._vars.test_expr(value)
    if is_ok:
      return value
    #self.error(object, name, value) 
    return value

class Expression(HasTraits):
  _vars = Instance(Variables)
  _expr = ExpressionString('')
  _data_array_cache = None
  _data_array_cache_index = Int(0)

  view = View(
      Item('_expr', show_label = False, editor=TextEditor(enter_set=True, auto_set=False))
  )

  def __init__(self, variables, expr, **kwargs):
    HasTraits.__init__(self, **kwargs)
    self._vars = variables
    self.set_expr(expr)

  def set_expr(self, expr):
    if self._expr != expr:
      self._expr = expr

  def __expr_changed(self):
    self.clear_cache()

  def clear_cache(self):
    self._data_array_cache = numpy.array([])
    self._data_array_cache_index = 0

  def get_curr_value(self):
    return self._vars._eval_expr(self._expr)

  def get_array(self, first=0, last=None):
    first, last = self._vars.bound_array(first, last)
    if last > self._data_array_cache_index:
      #print "Cache miss of", (last - self._data_array_cache_index)
      new_data = self._vars._get_array(self._expr, self._data_array_cache_index, last)

      new_shape = list(new_data.shape)
      new_shape[0] = -1 # -1 lets the first index resize appropriately for the data length
      
      self._data_array_cache = numpy.append(self._data_array_cache, new_data)
      self._data_array_cache.shape = new_shape
      self._data_array_cache_index = last
      # use the global max_samples to limit our cache size
      self._data_array_cache = self._data_array_cache[-self._vars.max_samples:]
  
    return self._data_array_cache[first:last]

