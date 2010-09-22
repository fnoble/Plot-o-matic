from variables import Variables, Expression

from plugins.viewers.tools3D.Frame import *
from plugins.viewers.tvtkHelper.Primitives import *

from vtk.util import colors

from numpy.random import rand

class Arnold1(PrimitiveCollection):
  def __init__(self,frame,T=None,**kwargs):
    PrimitiveCollection.__init__(self,frame,T)
    self.primitives=[
       Box(self.frame,T='tr(-0.8,0,0)',x_length=3.2,y_length=0.20,z_length=0.01,color=colors.blue,**kwargs),
       Box(self.frame,x_length=0.40,y_length=4,z_length=0.04,color=colors.blue,**kwargs),
       Box(self.frame,T='tr(-2.4,0,0)',x_length=0.40,y_length=1,z_length=0.04,color=colors.blue,**kwargs),
       #del kwargs['color']
       Box(self.frame,T='tr(-2.4,0,-0.20)',x_length=0.40,y_length=0.04,z_length=0.40,color=colors.red,**kwargs),
    ]

class Logo(PrimitiveCollection):
  def __init__(self,frame,T=None,**kwargs):
    PrimitiveCollection.__init__(self,frame,T)
    self.primitives=[
       Text(self.frame,text='Joby')
    ]

class TVTKconfig(PrimitiveCollection):
  def __init__(self,variables):
    self.variables=variables
    w=WorldFrame(variables)

    #self.add(Text(w,text='Plot-o-matic goes TVTK!'))
    ned=Frame(w,'TRx(pi)',name="North East Down");
    diskframe=Frame(ned,'tr(AP_DISK_r_n2d_n_x,AP_DISK_r_n2d_n_y,AP_DISK_r_n2d_n_z)*quat(AP_DISK_q_n2d_q0,AP_DISK_q_n2d_q1,AP_DISK_q_n2d_q2,AP_DISK_q_n2d_q3)',name="diskframe")
    orientation=Frame(ned,'tr(-50,-50,0)*quat(AP_EST2USER_0_q_n2b_q0,AP_EST2USER_0_q_n2b_q1,AP_EST2USER_0_q_n2b_q2,AP_EST2USER_0_q_n2b_q3)')
    airframe=Frame(ned,'tr(AP_EST2USER_0_r_n2b_n_x,AP_EST2USER_0_r_n2b_n_y,AP_EST2USER_0_r_n2b_n_z)*quat(AP_EST2USER_0_q_n2b_q0,AP_EST2USER_0_q_n2b_q1,AP_EST2USER_0_q_n2b_q2,AP_EST2USER_0_q_n2b_q3)')
    #airframe_gps=Frame(ned,'tr(HENRY_GNSS_North,HENRY_GNSS_East,HENRY_GNSS_Down)*quat(AP_EST2USER_0_q_n2b_q0,AP_EST2USER_0_q_n2b_q1,AP_EST2USER_0_q_n2b_q2,AP_EST2USER_0_q_n2b_q3)')

    ax=Frame(ned,'sc(50)')
    self.add(Arrow(ax,color=colors.red))
    self.add(Text(ax,T='tr(1,0,0)*sc(0.1)',text='N / X'))
    self.add(Arrow(ax,T='TRz(pi/2)',color=colors.green))
    self.add(Text(ax,T='tr(0,1,0)*sc(0.1)',text='E / Y'))
    self.add(Arrow(ax,T='TRy(-pi/2)',color=colors.blue))
    self.add(Text(ax,T='tr(0,0,1)*sc(0.1)',text='D / Z'))

    self.add(Plane(ned,T='sc(800)',representation='wireframe',color=colors.grey,x_resolution=80,y_resolution=80))

    
    self.add(Arnold1(orientation,T='sc(12)'))#,color=colors.blue))
    #self.add(Text(orientation,text='Reference only'))

    self.add(Arnold1(airframe,T='sc(5)'))#,color=colors.red))
    #self.add(Arnold1(airframe_gps,T='sc(5)'))#,color=colors.red))
    self.add(Circle(diskframe,radius=variables.new_expression('AP_DISK_radius')))
    self.add(Trace(
      ned,
      x = variables.new_expression('AP_EST2USER_0_r_n2b_n_x'),
      y = variables.new_expression('AP_EST2USER_0_r_n2b_n_y'),
      z = variables.new_expression('AP_EST2USER_0_r_n2b_n_z'),
      color=colors.green,
      length=2000
    ))
    self.add(Trace(
      ned,
      x = variables.new_expression('AP_EST2USER_0_r_n2b_n_x'),
      y = variables.new_expression('AP_EST2USER_0_r_n2b_n_y'),
      z = variables.new_expression('0'),
      color=colors.green,
      length=2000
    ))

    self.add(Trace(
      ned,
      x = variables.new_expression('HENRY_GNSS_North'),
      y = variables.new_expression('HENRY_GNSS_East'),
      z = variables.new_expression('HENRY_GNSS_Down'),
      color=colors.purple,
      length=2000
    ))
    self.add(Trace(
      ned,
      x = variables.new_expression('HENRY_GNSS_North'),
      y = variables.new_expression('HENRY_GNSS_East'),
      z = variables.new_expression('0'),
      color=colors.maroon,
      length=2000
    ))


    self.add(Trace(
      ned,
      x = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_0_x'),
      y = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_0_y'),
      z = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_0_z'),
      color=colors.pink,
      length=600
    ))
    self.add(Trace(
      ned,
      x = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_1_x'),
      y = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_1_y'),
      z = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_1_z'),
      color=colors.pink,
      length=600
    ))
    self.add(Trace(
      ned,
      x = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_2_x'),
      y = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_2_y'),
      z = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_2_z'),
      color=colors.pink,
      length=600
    ))
    self.add(Trace(
      ned,
      x = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_3_x'),
      y = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_3_y'),
      z = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_3_z'),
      color=colors.pink,
      length=600
    ))
    self.add(Trace(
      ned,
      x = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_4_x'),
      y = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_4_y'),
      z = variables.new_expression('AP_ACADO_TRAJ_r_n2t_n_4_z'),
      color=colors.pink,
      length=600
    ))


    #self.add(Logo(ned))
    
