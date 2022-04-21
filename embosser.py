import cadquery as cq
import numpy as np
from types import SimpleNamespace as ns

measured = ns(
    diameter = 43,
    gap = 3.65,
    rectangle = ns(
        width = 3,
        length = 6,
        separation = 22.25,
        front_offset = 14.75
    ),
    circle = ns(
        diameter = 3.25,
        front_offset = 10,
        back_offset = 15,
        separation = 15,
        depth = 1.4
    ),
    thickness = 2.3,
    tang = 14.5
)


paper_thickness = 0.1

lip = ns(
    radius = 3,
    thickness = 2.5
)

############################

base = cq.Workplane('XY')
base = base.circle(measured.diameter/2+lip.radius)
base = base.extrude(-measured.gap/2-lip.thickness)
base = base.faces('<Z').workplane().circle(measured.diameter/2).cutBlind(-lip.thickness)

top = base.mirror('XY')
top = top.faces('>Z[1]').workplane()
for x in [i*(measured.rectangle.separation+measured.rectangle.width)/2 for i in [-1, 1]]:
    top = top.moveTo(x, measured.diameter/2 - measured.rectangle.front_offset - measured.rectangle.length/2)
    top = top.rect(measured.rectangle.width, measured.rectangle.length)
top = top.extrude(measured.thickness)
top = top.cut(
    cq.Workplane('XZ')
    .moveTo(0, measured.gap/2 + lip.thickness)
    .rect(measured.tang, 2*lip.thickness)
    .extrude(measured.diameter)
)

base = base.faces('<Z[1]').workplane()
for center in [
    (0, -measured.diameter/2 + measured.circle.front_offset),
    ( measured.circle.separation/2, -measured.circle.back_offset+measured.diameter/2),
    (-measured.circle.separation/2, -measured.circle.back_offset+measured.diameter/2)
]:
    base = base.moveTo(*center)
    base = base.circle(measured.circle.diameter/2)
base = base.extrude(measured.circle.depth)

base = base.faces('>Z').workplane()
angles = np.linspace(0, 2*np.pi, num=40, endpoint = False)
r = measured.diameter/2 - 2
xx = r * np.cos(angles)
yy = r * np.sin(angles)
for x, y, a in zip(xx, yy, angles*180/np.pi):
    base = base.moveTo(x, y)
    base = base.slot2D(4, 1.5, angle = a)
    
base = base.extrude(0.5);

letter = cq.Workplane('XY').text('A', 26, 0.5, font='Lucida Calligraphy Italic').translate([-2, 2, 0])

base = base.union(letter)
base = base.faces('>Z').edges().fillet(0.4)

top = top.cut(base)

show_object(base, name='base', options={'color':'green', 'alpha':0.1})
show_object(top, name='top', options={'color':'orange', 'alpha':0.1})

cq.exporters.export(top.rotate([0,0,0], [1,0,0], 90), 'top.stl')
cq.exporters.export(base.rotate([0,0,0], [1,0,0], 90).rotate([0,0,0],[0,1,0],90), 'base.stl')
