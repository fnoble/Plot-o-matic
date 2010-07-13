from enthought.traits.api import HasTraits, Int, Dict, List, Property, Enum, Color, on_trait_change
from enthought.traits.ui.api import View, Item, ValueEditor, TabularEditor
from enthought.traits.ui.tabular_adapter import TabularAdapter
import time

class VariableTableAdapter(TabularAdapter):
  columns = [('Variable name', 0), ('Value', 1)]
  
  def _get_bg_color(self):
    #value = (0xFF * self.item[2])/4
    #return (0xFF, value, value)
    pass

vars_table_editor = TabularEditor(
  adapter = VariableTableAdapter(),
  editable = False
  #images  = [ ImageResource( 'red_flag', search_path = search_path ) ]
)

class Variables(HasTraits):
  vars_pool = Dict()
  vars_list = List()
  vars_table_list = List()  # a list version of vars_pool maintained for the TabularEditor
  sample_number = Int(0)

  view = View(
           Item(
             name = 'vars_table_list',
             editor = vars_table_editor,
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
    self.vars_pool = new_vars_pool
    self.vars_list += [(new_vars_pool, self.sample_number, time.time())]
    
  @on_trait_change('vars_pool')
  def update_vars_table(self, old_pool, new_pool):
    self.vars_table_list = list(self.vars_pool.iteritems())
    
  def reset_variables(self):
    self.vars_pool = {}
    
  def eval_expr(self, expr, vars_pool):
    """
        Returns the value of a python expression evaluated with 
        the variables in the pool in scope.
    """
    try:
      data = eval(expr, vars_pool)
    except:
      data = None
    return data
    
  def get_data_array(self, expr):
    """
        Returns an array of tuples containing the all the values of an
        the supplied expression and the sample numbers and times corresponding to
        these values.
    """
    data_array = []
    for vars_list_item in self.vars_list:
      (vars_pool, sample_num, time) = vars_list_item
      value = self.eval_expr(expr, vars_pool)
      if value:
        data_array += [(value, sample_num, time)]
    return data_array