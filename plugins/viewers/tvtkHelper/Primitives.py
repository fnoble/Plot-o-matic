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
  
  
  #This should also add delegated trait objects.
  def handle_arguments(self,*args,**kwargs): 
    HasTraits.__init__(self)		#magic by fnoble
    for a in args:
      if isinstance(a,Frame):
        self.parent=a
    print self.all_trait_names()
    for k,v in kwargs.items():
      if k == 'frame':
        self.parent=v
      elif k == 'T':
         self.T=T
      elif len(self.trait_get(k))>0:
         print "self:", k,v
         #self.trait_set({k:v})
         self.__setattr__(k,v)
      elif len(self.actor.trait_get(k))>0:
         print "actor:", k,v
         self.actor.__setattr__(k,v)
      elif len(self.properties.trait_get(k))>0:
         print "properties:", k,v
         self.properties.__setattr__(k,v)
      else :
         print "unknown argument", k , v
         #print self.properties.__dict__
         #print self.actor.__dict__

    if not(self.parent):
      self.parent = WorldFrame()
         
  def __init__(self,**kwargs):
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
  def __init__(self,*args,**kwargs):
    Primitive.__init__(self,**kwargs)
    self.source = tvtk.ConeSource()
    self.polyDataMapper = tvtk.PolyDataMapper()
    self.polyDataMapper.input=self.source.output
    self.actor = tvtk.Actor(mapper=self.polyDataMapper)
    self.handle_arguments(*args,**kwargs)
    
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
  def __init__(self,*args,**kwargs):
    Primitive.__init__(self,**kwargs)
    self.source = tvtk.CubeSource()
    self.polyDataMapper = tvtk.PolyDataMapper()
    self.polyDataMapper.input=self.source.output
    
    self.actor = tvtk.Actor(mapper=self.polyDataMapper)
    self.handle_arguments(*args,**kwargs)
    
    
class Axes(Primitive):
  source = Instance(tvtk.Axes)
  tube = Instance(tvtk.TubeFilter)
  
  scale_factor=DelegatesTo('tube')
  radius=DelegatesTo('tube')
  sides=PrototypedFrom('tube','number_of_sides')
  
  traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'properties',editor=InstanceEditor(), label = 'Render properties'),
    title = 'Axes properties'
  )
  def __init__(self,*args,**kwargs):
    Primitive.__init__(self,*kwargs)
    self.source = tvtk.Axes(symmetric=1)
    self.tube = tvtk.TubeFilter(vary_radius='vary_radius_off',input=self.source.output)
    self.mapper = tvtk.PolyDataMapper(input=self.tube.output)
    self.actor = tvtk.Actor(mapper=self.mapper)
    self.handle_arguments(*args,**kwargs)
    

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
  def __init__(self,*args,**kwargs):
    Primitive.__init__(self,*kwargs)
    self.source = tvtk.CylinderSource()
    self.mapper = tvtk.PolyDataMapper(input=self.source.output)
    self.actor = tvtk.Actor(mapper=self.mapper)
    self.handle_arguments(*args,**kwargs)

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
  def __init__(self,*args,**kwargs):
    Primitive.__init__(self,**kwargs)
    self.source = tvtk.SphereSource()
    self.mapper = tvtk.PolyDataMapper(input=self.source.output)
    self.actor = tvtk.Actor(mapper=self.mapper)
    self.handle_arguments(*args,**kwargs)

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
   def __init__(self,*args,**kwargs):
    Primitive.__init__(self,**kwargs)
    self.source = tvtk.ArrowSource()
    self.mapper = tvtk.PolyDataMapper(input=self.source.output)
    self.actor = tvtk.Actor(mapper=self.mapper)
    self.handle_arguments(*args,**kwargs)

class Plane(Primitive):
   source=Instance(tvtk.PlaneSource)
   traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Plane properties'
   )
   def __init__(self,*args,**kwargs):
    Primitive.__init__(self,**kwargs)
    self.source = tvtk.PlaneSource()
    self.mapper = tvtk.PolyDataMapper(input=self.source.output)
    self.actor = tvtk.Actor(mapper=self.mapper)
    self.handle_arguments(*args,**kwargs)
    
class Line(Primitive):
   source=Instance(tvtk.LineSource)
   traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Line properties'
   )
   def __init__(self,*args,**kwargs):
    Primitive.__init__(self,**kwargs)
    self.source = tvtk.LineSource()
    self.mapper = tvtk.PolyDataMapper(input=self.source.output)
    self.actor = tvtk.Actor(mapper=self.mapper)
    self.handle_arguments(*args,**kwargs)

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
    def __init__(self,*args,**kwargs):
        Primitive.__init__(self,*kwargs)
        self.source=tvtk.ImageReader(file_name="woodpecker.bmp") # im.ouput
        self.source.set_data_scalar_type_to_unsigned_char()
        #self.mapper = tvtk.ImageMapper(input=self.source.output)
        #self.actor = tvtk.Actor2D(mapper=self.mapper)
        self.actor=tvtk.ImageActor(input=self.source.output)
        self.handle_arguments(*args,**kwargs)
    
#http://mayavi2.sourcearchive.com/documentation/3.3.0-2/actors_8py-source.html
#source = tvtk.ArrowSource(tip_resolution=resolution,
#                              shaft_resolution=resolution)

# LineSource, PlaneSource
