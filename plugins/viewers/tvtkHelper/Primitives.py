from enthought.traits.api import HasTraits, Str, Regex, Either,This, List, Instance, PrototypedFrom,DelegatesTo, Any, on_trait_change, Float, Range, Int
from enthought.traits.ui.api import TreeEditor, TreeNode, View, Item, VSplit, \
  HGroup, Handler, Group, Include, ValueEditor, HSplit, ListEditor, InstanceEditor

from enthought.tvtk.api import tvtk
from plugins.viewers.tools3D.Frame import *

import numpy
from numpy import array, ndarray, linspace, zeros
# actor inherits from Prop3D

import numpy as np


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
    for k,v in kwargs.items():
      if k == 'frame':
        self.parent=v
      elif k == 'T':
         if isinstance(v,Expression):
           self.T=v
         else:
           self.T=self.parent.variables.new_expression(v)
      elif len(self.trait_get(k))>0:
         #self.trait_set({k:v})
         self.__setattr__(k,v)
      elif len(self.actor.trait_get(k))>0:
         self.actor.__setattr__(k,v)
      elif len(self.properties.trait_get(k))>0:
         self.properties.__setattr__(k,v)
      elif len(self.source.trait_get(k))>0:
         self.source.__setattr__(k,v)
      else :
         print "unknown argument", k , v

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
    Item(name = 'source', editor=InstanceEditor(), label = 'Geometric properties'),
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
    
# The following code is mainly from 
# http://www.enthought.com/~rkern/cgi-bin/hgwebdir.cgi/colormap_explorer/file/a8aef0e90790/colormap_explorer/colormaps.py
class PolyLine(Primitive):
   source=Instance(tvtk.PolyData)
   points=Instance(numpy.ndarray)
   traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Line properties'
   )
   def __init__(self,*args,**kwargs):
    Primitive.__init__(self,**kwargs)
    self.source = tvtk.PolyData()
    self.mapper = tvtk.PolyDataMapper(input=self.source)
    self.actor = tvtk.Actor(mapper=self.mapper)
    self.handle_arguments(*args,**kwargs)
    #kwargs.get('foo', 12)  fnoble cleverity

   def _points_changed(self,old, new):
    npoints = len(self.points)
    if npoints<2 :
      return
    lines = np.zeros((npoints-1, 2), dtype=int)
    lines[:,0] = np.arange(0, npoints-1)
    lines[:,1] = np.arange(1, npoints)
    self.source.points=self.points
    self.source.lines=lines

class Circle(PolyLine):
   radius=Instance(Expression)
   resolution=Int(100)
   traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'radius', style = 'custom'),
    Item(name = 'resolution'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Line properties'
   )
   def __init__(self,*args,**kwargs):
     PolyLine.__init__(self,*args,**kwargs)
     
   def update(self):
     t=linspace(0,6.29,self.resolution)
     if self.radius.get_curr_value() !=None :
     	self.points = array([self.radius.get_curr_value()*sin(t),self.radius.get_curr_value()*cos(t),zeros(t.shape)]).T
     	super(Circle, self).update()
    
class Trace(PolyLine):
   x  = Instance(Expression)
   y  = Instance(Expression)
   z  = Instance(Expression)
   #point  = Instance(Expression)
   length = Int(0)
   
   traits_view = View(
    Item(name = 'length', label='Frame'),
    Item(name = 'x', style = 'custom'),
    Item(name = 'y', style = 'custom'),
    Item(name = 'z', style = 'custom'),
    #Item(name = 'points', style = 'custom'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Line properties'
   )
   def __init__(self,*args,**kwargs):
     PolyLine.__init__(self,*args,**kwargs)
     
   def update(self):
     x=self.x.get_array(first=-self.length)
     y=self.y.get_array(first=-self.length)
     z=self.z.get_array(first=-self.length)
     self.points = array([x,y,z]).T
     #self.points = self.point.get_array(first=-self.length) #array([x,y,z]).T
     #print self.point.get_array(first=-self.length).shape
     super(Trace, self).update()
     

class Text(Primitive):
  text=DelegatesTo('source')
  traits_view = View(
    Item(name = 'parent', label='Frame'),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    Item(name = 'text'),
    Item(name = 'properties', editor=InstanceEditor(), label = 'Render properties'),
    title = 'Text properties'
   )
  def __init__(self,*args,**kwargs):
    Primitive.__init__(self,**kwargs)
    self.source = tvtk.VectorText()
    self.mapper = tvtk.PolyDataMapper(input=self.source.get_output())
    self.actor = tvtk.Actor(mapper=self.mapper)
    self.handle_arguments(*args,**kwargs)
    #kwargs.get('foo', 12)  fnoble cleverity

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

class PrimitiveCollection(HasTraits):
  primitives=List(Primitive)
  T=Instance(Expression)
  frame=Instance(Frame)
  
  def getPrimitives(self):
    return self.primitives
    
  def __init__(self,frame,T=None):
    if T is None:
      self.frame=frame
    else :
      self.frame=Frame(frame,T)
      
  def add(self, arg):
    if isinstance(arg,list):
      map(self.add,arg)
    if isinstance(arg,Primitive):
      self.primitives.append(arg)
    if isinstance(arg,PrimitiveCollection):
      self.add(arg.getPrimitives()) 
      
      

