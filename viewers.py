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

  def add_expr(self, expr):
    pass

  def get_config(self):
    print "Warning: calling get_config on viewer '%s' that doesn't implement it." % self.__class__.__name__
    return {'name': self.name, 'refresh_rate': self.refresh_rate}

  def set_config(self, config):
    print "Warning: calling set_config on viewer '%s' that doesn't implement it." % self.__class__.__name__
    print "  config was:", config
    self.name = config['name']
    self.refresh_rate = config['refresh_rate']


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
        try:
          self.selected_viewer.update()
        except Exception as e:
          print "Exception in viewer '%s':" % self.selected_viewer.name, e
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

  def _remove_all_viewers(self):
    for viewer in self.viewers:
      self._remove_viewer(viewer)

  def get_config(self):
    config = []
    for viewer in self.viewers:
      viewer_config = {viewer.__class__.__name__: viewer.get_config()}
      config.append(viewer_config)
    return config

  def set_config(self, config):
    from plugin_manager import get_viewer_plugin_by_name
    self._remove_all_viewers()
    for viewer_config in config:
      viewer_plugin_name = list(viewer_config.iterkeys())[0]
      viewer_plugin_config = viewer_config[viewer_plugin_name]
      new_viewer = get_viewer_plugin_by_name(viewer_plugin_name)()
      self._add_viewer(new_viewer)
      new_viewer.set_config(viewer_plugin_config)

