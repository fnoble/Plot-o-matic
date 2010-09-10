from enthought.traits.api import Str, Bool, Range, HasTraits, Instance, on_trait_change, List
from enthought.traits.ui.api import Item, View

import threading as t
import time

from variables import Variables


class Viewer(HasTraits):
  name = Str('Viewer')
  refresh_rate = Range(0.5, 30, 10)
  variables = Instance(Variables)

  view = View(
    Item(label='Viewer')
  )

  traits_view = View(
    Item(name = 'name'),
    Item(name = 'refresh_rate'),
    title = 'Viewer'
  )

  def start(self):
    pass

  def stop(self):
    pass

  def show(self):
    pass

  def hide(self):
    pass

  def update(self):
    pass


class Viewers(HasTraits, t.Thread):
  viewers = List(Viewer)
  variables = Instance(Variables) # Variables instance to provide the data context for all of our viewers
  selected_viewer = Instance(Viewer)
  name = Str('Viewers') # for thread debugging
  _wants_to_terminate = Bool(False)
  
  def __init__(self, **kwargs):
    t.Thread.__init__(self)
    HasTraits.__init__(self, **kwargs)
  
  @on_trait_change('variables.add_var_event')
  def add_expr_to_viewer(self, evt):
    if self.selected_viewer:
      self.selected_viewer.add_expr(evt.item[0])

  def run(self):
    """ Thread to update viewers. """
    while not self._wants_to_terminate:
      if self.selected_viewer:
        self.selected_viewer.update()
        time.sleep(1.0/self.selected_viewer.refresh_rate)
      else:
        time.sleep(0.5)
    self._stopped()
  
  def select_viewer(self, viewer):
    if self.selected_viewer:
      self.selected_viewer.hide()
    self.selected_viewer = viewer
    viewer.show()
    
  def stop(self):
    self._wants_to_terminate = True
  
  def _stopped(self):
    """ 
        Called after thread finally stops, use internally
        for final clean-up.
    """
    map(lambda v: v.stop(), self.viewers)

  def _add_viewer(self, viewer):
    viewer.variables = self.variables
    self.viewers += [viewer]
    viewer.start()

  def _remove_viewer(self, viewer):
    viewer.stop()
    self.viewers.remove(viewer)

