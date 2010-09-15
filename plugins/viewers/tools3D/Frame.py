from variables import Expression

from enthought.traits.api import HasTraits, Str, Regex, Either,This, List, Instance, DelegatesTo, Any, on_trait_change, Float, Range
from enthought.traits.ui.api import TreeEditor, TreeNode, View, Item, VSplit, \
  HGroup, Handler, Group, Include, ValueEditor, HSplit, ListEditor, InstanceEditor


from numpy import eye



class Frame(HasTraits):
  parent=This
  T = Instance(Expression)
  name= Str("")
  
  traits_view = View(
    Item(name = 'name'),
    Item(name = 'parent' , label='Base', editor = InstanceEditor(label="Frame")),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    title = 'Frame properties'
  )

  def evalT(self):
    if self.T.get_curr_value()!=None:
      return self.parent.evalT()*self.T.get_curr_value()
    else:
      return None

  def __init__(self, parent, T,name=""):
    self.name=name
    self.parent=parent
    self.T=T

class WorldFrame(Frame):
  #Nothing to be seen here
  e=eye(4)
  def evalT(self):
    return self.e

  def __init__(self):
    self.name="WorldFrame"
    #self.parent=None
    #self.T=T

  traits_view = View(
	Item(label="The world is immutable"),
    title = 'WorldFrame'
  )

from numpy import matrix, sin, cos

class FrameHelperFunctions:


  def TRx(a):
    return  matrix([[1,0,0,0],[0,cos(a),-sin(a),0],[0,sin(a),cos(a),0],[0,0,0,1]])

  def TRy(a):
    return  matrix([[cos(a),0,sin(a),0],[0,1,0,0],[-sin(a),0,cos(a),0],[0,0,0,1]])

  def TRz(a):
    return  matrix([[cos(a),-sin(a),0,0],[sin(a),cos(a),0,0],[0,0,1,0],[0,0,0,1]])

  def tr(x,y,z):
    return  matrix([[1,0,0,x],[0,1,0,y],[0,0,1,z],[0,0,0,1]])

  def origin() :
    return tr(0,0,0)
    

from variables import update_context

update_context(FrameHelperFunctions.__dict__)



