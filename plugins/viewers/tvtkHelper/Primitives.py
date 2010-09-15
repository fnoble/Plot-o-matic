from enthought.traits.api import HasTraits, Str, Regex, Either,This, List, Instance, PrototypedFrom,DelegatesTo, Any, on_trait_change, Float, Range, Int
from enthought.traits.ui.api import TreeEditor, TreeNode, View, Item, VSplit, \
  HGroup, Handler, Group, Include, ValueEditor, HSplit, ListEditor, InstanceEditor

from enthought.tvtk.api import tvtk
from plugins.viewers.tools3D.Frame import *

from numpy import array
# actor inherits from Prop3D



#note: to change color, pull slider all the way accross the range

class Primitive(HasTraits):
  parent=Instance(Frame)
  T = Instance(Expression)
  polyDataMapper = Instance(tvtk.PolyDataMapper)
  actor = Instance(tvtk.Prop)
  #actor = Instance(tvtk.Actor)
  tm = tvtk.Matrix4x4
  properties=PrototypedFrom('actor', 'property')
  
  def __init__(self,*kwargs):
    self.tm=tvtk.Matrix4x4()
    pass
    
  def update(self):
      if self.T:
        if self.T.get_curr_value() !=None :
          p = self.parent.evalT()
          if p!=None:
            self.tm.deep_copy(array(p*self.T.get_curr_value()).ravel())
            self.actor.poke_matrix(self.tm)
      else:
        p=self.parent.evalT()
        if p!=None:
          self.tm.deep_copy(array(p).ravel())
          self.actor.poke_matrix(self.tm)

class Cone(Primitive):
  source = Instance(tvtk.ConeSource)
  height= DelegatesTo('source')
  radius= DelegatesTo('source')
  resolution= DelegatesTo('source')
  traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'height'),
    Item(name = 'radius'),
    Item(name = 'resolution'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Cone properties'
  )
  def __init__(self,parent=WorldFrame(),*kwargs):
    Primitive.__init__(self,*kwargs)
    self.parent=parent
    self.source = tvtk.ConeSource()
    self.polyDataMapper = tvtk.PolyDataMapper()
    self.polyDataMapper.input=self.source.output
    self.actor = tvtk.Actor(mapper=self.polyDataMapper)
    
class Box(Primitive):
  source = Instance(tvtk.CubeSource)
  x_length=DelegatesTo('source')
  y_length=DelegatesTo('source')
  z_length=DelegatesTo('source')

  traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'x_length'),
    Item(name = 'y_length'),
    Item(name = 'z_length'),
    Item(name = 'properties',editor=InstanceEditor(), label = 'Render properties'),
    title = 'Box properties'
  )
  def __init__(self,parent=WorldFrame(),*kwargs):
    Primitive.__init__(self,*kwargs)
    self.parent=parent
    self.source = tvtk.CubeSource()
    self.polyDataMapper = tvtk.PolyDataMapper()
    self.polyDataMapper.input=self.source.output
    self.actor = tvtk.Actor(mapper=self.polyDataMapper)

class Axes(Primitive):
  source = Instance(tvtk.Axes)

  traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'properties',editor=InstanceEditor(), label = 'Render properties'),
    title = 'Axes properties'
  )
  def __init__(self,parent=WorldFrame(),scale_factor=1.0, radius=0.02,sides=12,*kwargs):
    self.parent = parent
    Primitive.__init__(self,*kwargs)
    self.source = tvtk.Axes(scale_factor=scale_factor, symmetric=1)
    self.tube = tvtk.TubeFilter(radius=radius, number_of_sides=sides,
                           vary_radius='vary_radius_off',
                           input=self.source.output)
    self.mapper = tvtk.PolyDataMapper(input=self.tube.output)
    self.actor = tvtk.Actor(mapper=self.mapper)

class Cylinder(Primitive):
  source = Instance(tvtk.CylinderSource)
  height= DelegatesTo('source')
  radius= DelegatesTo('source')
  resolution= DelegatesTo('source')
  traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'height'),
    Item(name = 'radius'),
    Item(name = 'resolution'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Cylinder properties'
  )
  def __init__(self,parent=WorldFrame(),*kwargs):
    self.parent = parent
    Primitive.__init__(self,*kwargs)
    self.source = tvtk.CylinderSource()
    self.mapper = tvtk.PolyDataMapper(input=self.source.output)
    self.actor = tvtk.Actor(mapper=self.mapper)

class Sphere(Primitive):
  source=Instance(tvtk.SphereSource)
  radius=DelegatesTo('source')
  theta_resolution=DelegatesTo('source')
  phi_resolution=DelegatesTo('source')
  traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'radius'),
    Item(name = 'theta_resolution'),
    Item(name = 'phi_resolution'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Sphere properties'
  )
  def __init__(self,parent=WorldFrame(),*kwargs):
    self.parent = parent
    Primitive.__init__(self,*kwargs)
    self.source = tvtk.SphereSource()
    self.mapper = tvtk.PolyDataMapper(input=self.source.output)
    self.actor = tvtk.Actor(mapper=self.mapper)

class Arrow(Primitive):
   source=Instance(tvtk.ArrowSource)
   tip_resolution = DelegatesTo("source")
   traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'tip_resolution'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Arrow properties'
   )
   def __init__(self,parent=WorldFrame(),*kwargs):
    self.parent = parent
    Primitive.__init__(self,*kwargs)
    self.source = tvtk.ArrowSource()
    self.mapper = tvtk.PolyDataMapper(input=self.source.output)
    self.actor = tvtk.Actor(mapper=self.mapper)

class Plane(Primitive):
   source=Instance(tvtk.PlaneSource)
   traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Plane properties'
   )
   def __init__(self,parent=WorldFrame(),*kwargs):
    self.parent = parent
    Primitive.__init__(self,*kwargs)
    self.source = tvtk.PlaneSource()
    self.mapper = tvtk.PolyDataMapper(input=self.source.output)
    self.actor = tvtk.Actor(mapper=self.mapper)

class Line(Primitive):
   source=Instance(tvtk.LineSource)
   traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Line properties'
   )
   def __init__(self,parent=WorldFrame(),*kwargs):
    self.parent = parent
    Primitive.__init__(self,*kwargs)
    self.source = tvtk.LineSource()
    self.mapper = tvtk.PolyDataMapper(input=self.source.output)
    self.actor = tvtk.Actor(mapper=self.mapper)

class Image(Primitive):
    source=Instance(tvtk.ImageReader)
    file_name=DelegatesTo('source')
    traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'file_name'),
    Item(name = 'source', editor=InstanceEditor()),
    Item(name = 'actor', editor=InstanceEditor()),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Image properties'
    )
    def __init__(self,parent=WorldFrame(),*kwargs):
        self.parent = parent
        Primitive.__init__(self,*kwargs)
	self.source=tvtk.ImageReader(file_name="woodpecker.bmp") # im.ouput
        self.source.set_data_scalar_type_to_unsigned_char()
        #self.mapper = tvtk.ImageMapper(input=self.source.output)
        #self.actor = tvtk.Actor2D(mapper=self.mapper)
        self.actor=tvtk.ImageActor(input=self.source.output)
    
    
#http://mayavi2.sourcearchive.com/documentation/3.3.0-2/actors_8py-source.html
#source = tvtk.ArrowSource(tip_resolution=resolution,
#                              shaft_resolution=resolution)

# LineSource, PlaneSource
