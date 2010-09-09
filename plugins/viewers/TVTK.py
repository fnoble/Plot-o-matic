from enthought.tvtk.pyface.scene_model import SceneModel
from enthought.tvtk.pyface.scene_editor import SceneEditor
from enthought.tvtk.pyface import actors
from enthought.tvtk.api import tvtk

from enthought.traits.api import HasTraits, Str, Regex, List, Instance, DelegatesTo, Any, on_trait_change, Float, Range
from enthought.traits.ui.api import TreeEditor, TreeNode, View, Item, VSplit, \
  HGroup, Handler, Group, Include, ValueEditor, HSplit, ListEditor, InstanceEditor

from enthought.pyface.api import GUI

import numpy
from viewers import Viewer
from variables import Variables, Expression

class TVTKViewer(Viewer):
  name = Str('TVTK Viewer')
  scene = Instance(SceneModel, ())
  cs = Instance(tvtk.ConeSource)
  m = Instance(tvtk.PolyDataMapper)
  a = Instance(tvtk.Actor)
  e = Instance(Expression)

  view = View(
      Item(
        name = 'scene',
        height = 400,
        show_label = False,
        editor = SceneEditor()
      )
  )

  traits_view = View(
    Item(name = 'name'),
    Item(name = 'refresh_rate'),
    Item(name = 'e', style='custom'),
    Item(name = 'cs'),
    Item(name = 'm'),
    Item(name = 'a'),
    title = 'Viewer'
  )

  def start(self):
    #self.a = actors.cone_actor()
    self.cs = tvtk.ConeSource(height=3.0, radius=1.0, resolution=360)
    self.m = tvtk.PolyDataMapper()
    self.m.input = self.cs.output # or m.input = cs.get_output()
    self.a = tvtk.Actor(mapper=self.m)
    self.scene.add_actors(self.a)
    print self.a.__dict__
    self.e = self.variables.new_expression('[fm_fAirframe_x/300.0,fm_fAirframe_y/300.0,fm_fAirframe_z/300.0]')
    pass

  def stop(self):
    pass

  def show(self):
    pass

  def hide(self):
    pass

  def update(self):
    self.a.position = self.e.get_curr_value()
    GUI.invoke_later(self.scene.render)

