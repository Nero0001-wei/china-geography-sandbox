"""Geometry in metres: X across, -Y forward, Z up. Objects stay editable in collections."""
from math import cos, pi, sin
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
PALETTE = {
    'pearl': ('#F1F3EF', .30, .12), 'cream': ('#F0D496', .42, .12),
    'silver': ('#C1CDD1', .31, .45), 'steel': ('#74858E', .33, .48),
    'gunmetal': ('#34444E', .46, .25), 'rubber': ('#23292E', .81, .02),
    'glass': ('#18394E', .19, .24), 'seal': ('#192C37', .44, .06),
    'coral': ('#D84434', .29, .19), 'yellow': ('#EDAD28', .31, .15),
    'teal': ('#068C92', .32, .17), 'navy': ('#164970', .32, .17),
    'green': ('#165442', .36, .18), 'blue': ('#2679AA', .32, .17),
    'red': ('#CC393C', .29, .16), 'lamp': ('#ECFAFF', .23, .14),
    'amber': ('#F9AC3F', .30, .12), 'signal': ('#AE292D', .28, .12)
}
collection = None


def color(hex_color):
    def linear(c):
        return c / 12.92 if c < .04045 else ((c + .055) / 1.055) ** 2.4
    return tuple(linear(int(hex_color[i:i + 2], 16) / 255) for i in (1, 3, 5)) + (1,)


def group(name):
    global collection
    collection = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if not collection.users:
        bpy.context.scene.collection.children.link(collection)


def mat(key):
    existing = bpy.data.materials.get(key)
    if existing:
        return existing
    material = bpy.data.materials.new(key)
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    rgb, roughness, metal = PALETTE.get(key, ('#FFFFFF', .54, .05))
    material.diffuse_color = color(rgb)
    shader.inputs['Base Color'].default_value = color(rgb)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metal
    if key.startswith('sign-'):
        tex = material.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(HERE / 'materials' / (key + '.png')), check_existing=True)
        tex.image.pack()
        uv = material.node_tree.nodes.new('ShaderNodeUVMap')
        uv.uv_map = 'Sign'
        material.node_tree.links.new(uv.outputs['UV'], tex.inputs['Vector'])
        material.node_tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
    return material


def mesh(name, verts, faces, material, smooth=False):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.materials.append(mat(material))
    if smooth:
        for poly in data.polygons:
            poly.use_smooth = True
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    return obj


def bevel(obj, width, segments):
    if width <= 0:
        return obj
    modifier = obj.modifiers.new('Rounded edges', 'BEVEL')
    modifier.width = width
    modifier.segments = segments
    modifier.harden_normals = True
    normal = obj.modifiers.new('Panel normals', 'WEIGHTED_NORMAL')
    normal.keep_sharp = True
    return obj


def box(name, center, dims, material, radius=0, segments=1):
    x, y, z = center
    a, b, c = [v / 2 for v in dims]
    pts = [(x+u*a, y+v*b, z+w*c) for u, v, w in
           [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces = [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return bevel(mesh(name, pts, faces, material), radius, segments)


def panel(name, vertices, material, uv=False):
    obj = mesh(name, vertices, [tuple(range(len(vertices)))], material)
    if uv:
        mapping = obj.data.uv_layers.new(name='Sign')
        for i, coords in enumerate([(0,0), (1,0), (1,1), (0,1)]):
            mapping.data[i].uv = coords
    return obj


def ring_loft(name, rings, material, smooth=True):
    size = len(rings[0])
    faces = [tuple(range(size))]
    for i in range(len(rings)-1):
        for j in range(size):
            k = (j + 1) % size
            faces.append((i*size+k,i*size+j,(i+1)*size+j,(i+1)*size+k))
    faces.append(tuple(reversed(range((len(rings)-1)*size, len(rings)*size))))
    obj = mesh(name, [point for ring in rings for point in ring], faces, material, smooth)
    obj.data.polygons[0].use_smooth = obj.data.polygons[-1].use_smooth = False
    return obj


def vehicle_body(name, slices, material, smooth=True):
    # Each slice sets width at sill, shoulder and roof, with independently shaped corner radii.
    rings = []
    for y, bottom, low_width, shoulder, width, roof, top_width in slices:
        h = roof-bottom
        rings.append([(x,y,z) for x,z in (
            (-low_width,bottom),(low_width,bottom),(width, bottom+.10*h),(width,shoulder),
            ((width+top_width)*.5,roof-.06*h),(top_width,roof),(-top_width,roof),
            (-(width+top_width)*.5,roof-.06*h),(-width,shoulder),(-width,bottom+.10*h))])
    return ring_loft(name,rings,material,smooth)


def cylinder(name, a, b, radius, material, sides=12, end_radius=None):
    a, b = Vector(a), Vector(b)
    axis = (b-a).normalized()
    across = axis.cross(Vector((0,0,1)) if abs(axis.z)<.9 else Vector((0,1,0))).normalized()
    up = across.cross(axis)
    rings = []
    for p, r in [(a,radius), (b,radius if end_radius is None else end_radius)]:
        rings.append([p + r * (across*cos(i*2*pi/sides)+up*sin(i*2*pi/sides)) for i in range(sides)])
    return ring_loft(name,rings,material)


def fuselage(name, slices, material, sides=24):
    rings=[]
    for y, height, rx, rz in slices:
        rings.append([(rx*cos(t*2*pi/sides),y,height+rz*sin(t*2*pi/sides)) for t in range(sides)])
    return ring_loft(name,rings,material)


def axle_wheels(y, z, x, radius, width, fancy=False):
    for s in [-1,1]:
        cylinder('Tyre',(s*(x-width),y,z),(s*x,y,z),radius,'rubber',20)
        cylinder('Wheel rim',(s*x,y,z),(s*(x+.018),y,z),radius*.63,'steel',16)
        if fancy:
            cylinder('Alloy centre',(s*(x+.018),y,z),(s*(x+.024),y,z),radius*.46,'gunmetal',14)
            for i in range(5):
                a = i*2*pi/5
                p1 = (s*(x+.033), y+radius*.12*cos(a), z+radius*.12*sin(a))
                p2 = (s*(x+.033), y+radius*.49*cos(a+.17), z+radius*.49*sin(a+.17))
                cylinder('Alloy spoke',p1,p2,radius*.052,'silver',5)
            cylinder('Hub',(s*(x+.026),y,z),(s*(x+.040),y,z),radius*.15,'silver',12)


def beam(name,a,b,radius,material):
    return cylinder(name,a,b,radius,material,6)


def side_panel(name, sign, x, yz, material):
    corners=[(sign*x,y,z) for y,z in yz]
    return panel(name,corners if sign==1 else list(reversed(corners)),material)


def side_stripe(name, sign, slices, material):
    # station, width, lower and upper edge heights
    verts = [(sign*w,y,h) for y,w,lo,hi in slices for h in (lo,hi)]
    faces = [(i,i+2,i+3,i+1) if sign==1 else (i+1,i+3,i+2,i) for i in range(0,len(verts)-2,2)]
    return mesh(name,verts,faces,material)


def front_decal(body, name, rows, material, columns=5, steps=3, uv=False, lift=.012):
    """Project each decal vertex onto the real loft. Rows give height and lateral limits."""
    bpy.context.view_layer.update()
    vertices=[]
    st=[]
    faces=[]
    samples=[]
    for i,(a,b) in enumerate(zip(rows,rows[1:])):
        for j in range(steps):
            f=j/steps
            samples.append(tuple(v+(w-v)*f for v,w in zip(a,b)))
    samples.append(rows[-1])
    for j,(z,left,right) in enumerate(samples):
        for i in range(columns+1):
            x=left+(right-left)*i/columns
            hit,pt,norm,_=body.ray_cast((x,-100,z),(0,1,0))
            if not hit:
                raise ValueError(f'{name} misses shell at x={x:.3f}, z={z:.3f}')
            vertices.append((x,pt.y-lift,z))
            st.append((i/columns,j/(len(samples)-1)))
        if j:
            for i in range(columns):
                start=(j-1)*(columns+1)+i
                faces.append((start,start+1,start+columns+2,start+columns+1))
    obj=mesh(name,vertices,faces,material,True)
    if uv:
        layer=obj.data.uv_layers.new(name='Sign')
        for loop in obj.data.loops:
            layer.data[loop.index].uv=st[loop.vertex_index]
    return obj


def opposite_rows(rows):
    return [(z,-x2,-x1) for z,x1,x2 in rows]


def flank_decal(body,name,s,rows,material,lift=.012,steps=3,cols=1):
    """Drape narrow side trim over a compound-curved sidewall."""
    pts=[]
    for i,(a,b) in enumerate(zip(rows,rows[1:])):
        for j in range(steps+(i==len(rows)-2)):
            t=j/steps
            z,left,right=[v+(w-v)*t for v,w in zip(a,b)]
            for k in range(cols+1):
                y=left+(right-left)*k/cols
                hit,point,_,_=body.ray_cast((s*100,y,z),(-s,0,0))
                if not hit:
                    raise ValueError(f'{name} misses sidewall at y={y:.3f}, z={z:.3f}')
                pts.append((point.x+s*lift,y,z))
    stride=cols+1
    faces=[(n,n+1,n+stride+1,n+stride) for start in range(0,len(pts)-stride,stride) for n in range(start,start+cols)]
    return mesh(name,pts,faces,material,True)
