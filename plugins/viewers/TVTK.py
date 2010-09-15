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
from plugins.viewers.tools3D.Frame import *
from plugins.viewers.tvtkHelper.Primitives import *

class TVTKViewer(Viewer):
  name = Str('TVTK Viewer')
  primitives = List(Primitive)
  scene = Instance(SceneModel, ())
  
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
    Item(name = 'primitives', editor=ListEditor(),style='custom'),
    title = 'Viewer'
  )

  def start(self):
    #self.a = actors.cone_actor()
    w=WorldFrame()
    f1=Frame(w,self.variables.new_expression('TRy(time/10.0)*tr(1,0,0)'),name="F1")
    f2=Frame(f1,self.variables.new_expression('TRz(time/10.0)*tr(1,0,0)'),name="F2")
    f3=Frame(f2,self.variables.new_expression('TRx(time/10.0)*tr(1,0,0)'),name="F3")
    f4=Frame(f3,self.variables.new_expression('TRy(time/10.0)*tr(1,0,0)'),name="F4")
    f5=Frame(f4,self.variables.new_expression('TRx(time/10.0)*tr(1,0,0)'),name="F5")
    f6=Frame(f5,self.variables.new_expression('TRx(time/10.0)*tr(1,0,0)'),name="F6")
    f7=Frame(f6,self.variables.new_expression('TRz(time/10.0)*tr(1,0,0)'),name="F7")
    f8=Frame(f7,self.variables.new_expression('TRy(time/10.0)*tr(1,0,0)'),name="F8")
    self.primitives=[Axes(w),Box(f1),Cone(f2),Arrow(f3),Sphere(f4),Cylinder(f5),Image(f6),Line(f7),Plane(f8)]
    for prim in self.primitives:
    	self.scene.add_actors(prim.actor)
    pass

  def stop(self):
    pass

  def show(self):
    pass

  def hide(self):
    pass

  def update(self):
    print 123546
    for prim in self.primitives:
      prim.update()
    GUI.invoke_later(self.scene.render)

