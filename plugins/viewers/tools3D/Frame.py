from variables import Expression, Variables

from enthought.traits.api import HasTraits, Str, Regex, Either,This, List, Instance, DelegatesTo, Any, on_trait_change, Float, Range
from enthought.traits.ui.api import TreeEditor, TreeNode, View, Item, VSplit, \
  HGroup, Handler, Group, Include, ValueEditor, HSplit, ListEditor, InstanceEditor


from numpy import eye



class Frame(HasTraits):
  parent=This
  T = Instance(Expression)
  name= Str("")
  variables = DelegatesTo('parent')
  
  traits_view = View(
    Item(name = 'name'),
    Item(name = 'parent' , label='Base', editor = InstanceEditor(label="Frame")),
    Item(name = 'T', label = 'Matrix4x4', style = 'custom'),
    title = 'Frame properties'
  )

  def evalT(self):
    if self.T.get_curr_value()!=None and self.parent.evalT()!=None:
      return self.parent.evalT()*self.T.get_curr_value()
    else:
      return None

  def __init__(self, parent, T,name=""):
    self.name=name
    self.parent=parent
    if isinstance(T,Expression):
      self.T=T
    else :
      self.T=self.variables.new_expression(T)

class WorldFrame(Frame):
  #Nothing to be seen here
  e=eye(4)
  variables = Instance(Variables)
  def evalT(self):
    return self.e

  def __init__(self,variables):
    self.variables=variables
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
    
  def sc(s) :
    return matrix([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1.0/s]])

  def quat(a,b,c,d):
    return matrix([[	a*a+b*b-c*c-d*d,	2*b*c-2*a*d,	2*b*d+2*a*c,	0],
		[	2*b*c+2*a*d,		a*a-b*b+c*c-d*d,2*c*d-2*a*b,	0],
		[	2*b*d-2*a*c,		2*c*d+2*a*b,	a*a-b*b-c*c+d*d,0],
		[	0,			0,		0,		1]])
    
from variables import update_context

update_context(FrameHelperFunctions.__dict__)



