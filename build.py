"""Reproducible original bpy production for Hurry Up and Wait.

Blender 5.2.1. All motion is choreographed, not a physical simulation.
Run: Blender -b --factory-startup --python build.py -- --quality preview --stills
"""
import argparse, bpy, math, json, hashlib, datetime
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument("--quality", choices=["preview","final"], default="preview")
p.add_argument("--stills", action="store_true")
p.add_argument("--animation", action="store_true")
p.add_argument("--start", type=int, default=1)
p.add_argument("--end", type=int, default=504)
args = p.parse_args(__import__("sys").argv[__import__("sys").argv.index("--")+1:] if "--" in __import__("sys").argv else [])
OUT = ROOT / ("preview" if args.quality == "preview" else "final")
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablock in list(bpy.data.materials): bpy.data.materials.remove(datablock)

def mat(name, color, metallic=0.0, rough=.35, emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1)
    m.use_nodes=True; bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Metallic"].default_value=metallic; bs.inputs["Roughness"].default_value=rough
    if emission:
        bs.inputs["Emission Color"].default_value=(*color,1)
        bs.inputs["Emission Strength"].default_value=emission
    return m

CREAM=mat("Porcelain | warm ivory",(.72,.64,.51),rough=.33)
WHITE=mat("Markings | chalk",(.92,.94,.87),rough=.4)
RED=mat("Racer | vermilion",(.92,.055,.026),metallic=.28,rough=.24)
CYAN=mat("Courier | lagoon",(.015,.57,.64),metallic=.22,rough=.25)
DARK=mat("Graphite",(.017,.037,.052),metallic=.28,rough=.32)
BLACK=mat("Rubber",(.009,.014,.020),rough=.6)
STEEL=mat("Brushed aluminium",(.29,.38,.40),metallic=.8,rough=.23)
YELLOW=mat("Safety | golden",(.96,.5,.035),metallic=.1,rough=.3)
WATER=mat("Stylized water",(.018,.18,.25),metallic=.3,rough=.28)
GLOW_RED=mat("Stop signal",(.9,.022,.008),emission=2.4)
GLOW_GREEN=mat("Go signal",(.045,.9,.44),emission=2.4)
TYPE=mat("Overlay | ivory",(.96,.92,.8),emission=1)
SUBTYPE=mat("Overlay | mist",(.39,.63,.64),emission=1)

def finish(obj,name,material,parent=None):
    obj.name=name
    if material:obj.data.materials.append(material)
    if parent: obj.parent=parent
    return obj
def cube(name,loc,scale,material,bevel=.08,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=finish(bpy.context.object,name,material,parent);ob.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=ob.modifiers.new("Soft machined edges","BEVEL"); b.width=bevel;b.segments=3
        ob.modifiers.new("Weighted surface normals","WEIGHTED_NORMAL")
    return ob
def sphere(name,loc,scale,material,parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=loc)
    ob=finish(bpy.context.object,name,material,parent);ob.scale=scale
    for poly in ob.data.polygons:poly.use_smooth=True
    return ob
def cylinder(name,loc,radius,depth,material,axis="Z",parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc)
    ob=finish(bpy.context.object,name,material,parent)
    if axis=="Y":ob.rotation_euler[0]=math.pi/2
    if axis=="X":ob.rotation_euler[1]=math.pi/2
    b=ob.modifiers.new("Rim","BEVEL");b.width=.025;b.segments=2
    ob.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return ob
def empty(name,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=loc;o.parent=parent;return o
def key(o,frame,**props):
    for k,v in props.items():setattr(o,k,v);o.keyframe_insert(data_path=k,frame=frame)
def smooth(t):return max(0,min(1,t))**2*(3-2*max(0,min(1,t)))
def mix(a,b,t):return a+(b-a)*t
def arrow(name,x,y):
    verts=[(x-.18,y-.14,.337),(x+.18,y,.337),(x-.18,y+.14,.337),(x-.09,y,.337)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],[(0,1,2,3)]);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(WHITE)
def text(name,body,loc,size,material,parent=None):
    c=bpy.data.curves.new(name,"FONT");c.body=body;c.size=size;c.extrude=.001;c.align_x="LEFT"
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.location=loc;o.parent=parent;c.materials.append(material);return o
def visible_window(o,start,end):
    visibility=[(1,True),(max(1,start-1),True),(start,False),(end,False)]
    if end<504:visibility.extend([(end+1,True),(504,True)])
    for f,v in visibility:
        o.hide_render=v;o.keyframe_insert(data_path="hide_render",frame=f)
    # Restore state through frame_set before rendering.
def set_linear_animation():
    for a in bpy.data.actions:
        for layer in a.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for point in fc.keyframe_points:
                            if fc.data_path not in ("hide_render","hide_viewport"): point.interpolation="LINEAR"

# A floating industrial miniature, with a separate ferry across a stylized water channel.
cube("Diorama / chamfered plinth",(0.55,0,-.37),(16.9,7,.65),DARK,.25)
cube("Water channel",(3.35,0,.02),(8.05,5.7,.28),WATER,.08)
cube("Origin dock",(-3.13,0,.16),(7.6,4.7,.32),CREAM,.13)
cube("Arrival dock",(7.85,0,.16),(1.7,4.7,.32),CREAM,.13)
for y in [-1.05,1.05]:
    cube("Recessed lane",(-3.17,y,.323),(6.95,1.5,.02),DARK,.05)
    for x in [-5.7,-4.7,-3.7,-2.7,-1.7,-.7]: arrow("Direction chevron",x,y)
for x in [-6.6,-5.8,-5,-4.2,-3.4,-2.6,-1.8,-1.0,-.2]:
    cube("Dock rim bolt",(x,-2.13,.343),(.055,.055,.025),STEEL,.01)
for y in [-2.45,2.45]:
    for x in [.65,6.72]:
        cylinder("Mooring post",(x,y,.48),.105,.66,STEEL)
        cylinder("Mooring cap",(x,y,.83),.17,.10,YELLOW)
# Lines under the ferry clarify that it is a shared transport platform.
for y in [-1.8,1.8]:
    cube("Ferry guide cable",(3.65,y,.22),(6.2,.033,.035),STEEL,.01)
for row in range(6):
    for col in range(4):
        cube("Water glint",(1.4+col*1.4, -2.0+row*.79,.167),(.38,.018,.008),CYAN,.008)

ferry=empty("FERRY / shared departure", (1.85,0,0))
cube("Ferry deck",(0,0,.20),(2.52,3.96,.26),WHITE,.14,ferry)
cube("Ferry flotation",(0,0,-.02),(2.24,3.6,.23),DARK,.10,ferry)
for y in [-1.88,1.88]:
    cube("Deck edging",(0,y,.37),(2.42,.1,.13),YELLOW,.025,ferry)
for y in [-1.05,1.05]:
    cube("Boarding pad",(0,y,.338),(1.84,1.45,.02),DARK,.05,ferry)
for y in [-1.55,0,1.55]:
    cube("Deck rib",(0,y,.338),(2.34,.018,.012),STEEL,.007,ferry)
# Small rear stabilizer fins and a restrained bow indicator.
for y in [-1.62,1.62]:
    cylinder("Ferry bumper",(1.16,y,.31),.11,.10,BLACK,"X",ferry)

hinge=empty("Barrier / actual animated hinge",(.50,-2.15,.78))
cube("Barrier arm",(0,2.15,0),(.15,4.35,.15),YELLOW,.045,hinge)
for y in [.3,.8,1.3,1.8,2.3,2.8,3.3,3.8,4.2]:
    cube("Barrier stripe",(-.084,y,0),(.021,.20,.152),DARK,.005,hinge)
cylinder("Barrier pedestal",(.5,-2.15,.66),.2,.8,DARK)
cylinder("Hinge cap",(.5,-2.15,.81),.20,.22,STEEL,"X")
# Red/green signals exchange, and not a fake physical sensor.
cube("Signal housing",(.52,2.24,1.00),(.32,.40,1.13),DARK,.09)
stop=sphere("STOP lamp",(.335,2.24,1.2),(.055,.13,.13),GLOW_RED)
go=sphere("GO lamp",(.335,2.24,.83),(.055,.13,.13),GLOW_GREEN)

def vehicle(name,bodymat,y,racer=False):
    root=empty(name,(-5.7,y,0))
    sphere(name+" / body",(0,0,.83),(.69,.45,.31),bodymat,root)
    cube(name+" / undercarriage",(0,0,.57),(1.0,.68,.15),DARK,.07,root)
    wheels=[]
    for x in [-.40,.40]:
        for sy in [-.47,.47]:
            wheel=cylinder(name+" / rubber wheel",(x,sy,.54),.21,.17,BLACK,"Y",root);wheels.append(wheel)
            cylinder(name+" / hub",(x,sy*1.20,.54),.105,.022,STEEL,"Y",root)
            # Visible asymmetric marking makes impatient spinning legible.
            stripe=cube(name+" / wheel tick",(0,0,0),(.10,.028,.015),YELLOW if racer else WHITE,.006,wheel)
            stripe.location=(.15,0,.094 if sy<0 else -.094)
    # Eyes at the front (+X). The front is visible from the camera.
    eyes=[]
    for sy in [-.18,.18]:
        sphere(name+" / eye",( .586,sy,.94),(.14,.105,.12),WHITE,root)
        pupil=sphere(name+" / pupil",(.70,sy,.95),(.033,.068,.073),DARK,root);eyes.append(pupil)
    # A tiny curved smile is a simple original curve.
    c=bpy.data.curves.new(name+" smile","CURVE");c.dimensions="3D";c.bevel_depth=.015;c.bevel_resolution=3
    sp=c.splines.new("POLY");sp.points.add(12)
    for i,pt in enumerate(sp.points):
        a=i/12*math.pi;pt.co=(.647, .13*math.cos(a), .76-.035*math.sin(a),1)
    ob=bpy.data.objects.new(name+" / smile",c);bpy.context.collection.objects.link(ob);ob.parent=root;c.materials.append(DARK)
    antenna=empty(name+" / antenna pivot",(0,0,1.0),root)
    cylinder(name+" / antenna stem",(0,0,.20),.024,.38,STEEL,parent=antenna)
    sphere(name+" / antenna light",(0,0,.41),(.095,.095,.095),YELLOW if racer else WHITE,antenna)
    if racer:
        cube(name+" / spoiler",(-.48,0,1.08),(.21,1.12,.10),RED,.04,root)
        for sy in [-.29,.29]:cube(name+" / spoiler strut",(-.43,sy,.93),(.06,.06,.31),STEEL,.015,root)
        for sy in [-.20,.20]:
            cylinder(name+" / turbo exhaust",(-.68,sy,.73),.13,.28,STEEL,"X",root)
            cylinder(name+" / dark nozzle",(-.833,sy,.73),.086,.014,BLACK,"X",root)
    else:
        cube(name+" / parcel",(-.14,0,1.11),(.49,.49,.25),CREAM,.05,root)
        cube(name+" / parcel band",(-.14,0,1.247),(.08,.5,.018),WHITE,.006,root)
    return root,wheels,eyes,antenna

red,rw,re,ra=vehicle("RED / impatient racer",RED,1.05,True)
cyan,cw,ce,ca=vehicle("CYAN / steady courier",CYAN,-1.05,False)

# Choreographed paths. Red arrives at frame 108; cyan at 268. Both board the same ferry.
FPS=24; END=504
for f in range(1,END+1,2):
    if f<52:rx=-5.65
    elif f<108:rx=mix(-5.65,-.28,smooth((f-52)/56))
    elif f<292:rx=-.28
    elif f<326:rx=mix(-.28,1.83,smooth((f-292)/34))
    else:rx=1.83+4.15*smooth((f-326)/108)
    if f<58:cx=-5.65
    elif f<270:cx=mix(-5.65,-.28,smooth((f-58)/212))
    elif f<292:cx=-.28
    elif f<326:cx=mix(-.28,1.83,smooth((f-292)/34))
    else:cx=1.83+4.15*smooth((f-326)/108)
    waiting=108<=f<=268
    fidget=(.035*math.sin(f*1.0)+.018*math.sin(f*.31)) if waiting else 0
    lean=-.055*math.sin(math.pi*max(0,min(1,(f-52)/56))) if f<108 else (.027*math.sin(f*.44) if waiting else 0)
    key(red,f,location=(rx,1.05,fidget),rotation_euler=(0,lean,0))
    key(cyan,f,location=(cx,-1.05,.008*math.sin(f*.1) if 58<f<270 else 0))
    carried_distance=4.15*smooth((f-326)/108)
    spin=(rx-carried_distance+5.65)/.21 + (max(0,min(f,270)-108)*.46)
    for w in rw:key(w,f,rotation_euler=(math.pi/2,spin,0))
    for w in cw:key(w,f,rotation_euler=(math.pi/2,(cx-carried_distance+5.65)/.21,0))
    key(ra,f,rotation_euler=(0,.19*math.sin(f*.55) if waiting else .03*math.sin(f*.08),0))
    key(ca,f,rotation_euler=(0,.03*math.sin(f*.08),0))
    key(ferry,f,location=(1.85+4.15*smooth((f-326)/108),0,0))
    key(hinge,f,rotation_euler=(1.40*smooth((f-275)/25),0,0))
    # Blinks: tiny squash, with no false simulation claims.
    for eyes in (re,ce):
        blink= .16 if any(abs(f-b)<3 for b in [34,147,249,365,457]) else 1
        for o in eyes:key(o,f,scale=(.033,.068,.073*blink))
for obj in [stop]:
    visible_window(obj,1,274)
visible_window(go,275,504)

# Camera and intentional framing.
scene=bpy.context.scene
bpy.ops.object.camera_add(location=(9,-14,12))
camera=bpy.context.object;camera.name="Camera / miniature stage";scene.camera=camera
camera.data.type="ORTHO";camera.data.ortho_scale=19.5;camera.data.lens=48
def camera_pose(f,loc,target,scale):
    camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.keyframe_insert(data_path="location",frame=f);camera.keyframe_insert(data_path="rotation_euler",frame=f)
    camera.data.ortho_scale=scale;camera.data.keyframe_insert(data_path="ortho_scale",frame=f)
camera_pose(1,(8,-13,12),(.55,0,.05),19.5)
camera_pose(105,(8,-13,12),(.55,0,.05),19.5)
camera_pose(155,(6,-10,8),(-.6,0,.25),13.5)
camera_pose(245,(6,-10,8),(-.6,0,.25),13.5)
camera_pose(330,(9,-13,11),(.75,0,.25),19.5)
camera_pose(434,(9,-14,12),(.75,0,.1),19.5)
camera_pose(504,(9,-14,12),(.75,0,.1),19.5)

# Editorial typography is actual Blender geometry parented to the camera.
title=text("Opening title","HURRY UP",(-8.20,4.25,-9),.48,TYPE,camera)
title2=text("Opening subtitle","AND WAIT.",(-8.20,3.68,-9),.48,TYPE,camera)
visible_window(title,1,60);visible_window(title2,1,60)
counter_label=text("Departure label","NEXT DEPARTURE",(-8.15,4.28,-9),.22,SUBTYPE,camera)
visible_window(counter_label,72,274)
for n in range(9,0,-1):
    begin=max(72,275-n*24)
    ob=text("Countdown "+str(n),f"00:{n:02d}",(-8.15,3.65,-9),.51,TYPE,camera)
    visible_window(ob,begin,min(274,275-(n-1)*24-1))
boarding=text("Boarding title","RIGHT ON TIME.",(-8.15,4.10,-9),.45,TYPE,camera);visible_window(boarding,276,324)
endtitle=text("Payoff","SAME DEPARTURE.",(-8.15,4.15,-9),.49,TYPE,camera);visible_window(endtitle,438,504)
endnote=text("Endnote","A LITTLE FILM ABOUT SPEED.",(-8.15,4.80,-9),.20,SUBTYPE,camera);visible_window(endnote,448,504)
overlay=empty("Editorial typography / framing",parent=camera)
for obj in list(bpy.data.objects):
    if obj.type=="FONT" and obj.parent==camera:obj.parent=overlay
for frame,scale in [(1,19.5),(105,19.5),(155,13.5),(245,13.5),(330,19.5),(434,19.5),(504,19.5)]:
    key(overlay,frame,scale=(scale/18.9,scale/18.9,1))

# Studio floor, warm key and cool rim.
cube("Studio backdrop",(0,0,-1.0),(200,200,.15),mat("Backdrop",(.024,.049,.060),rough=.8),.0)
world=bpy.data.worlds.new("Studio ambience");scene.world=world;world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.12,.18,.21,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.5
def area(name,loc,power,size,color,target):
    bpy.ops.object.light_add(type="AREA",location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape="DISK";o.data.size=size;o.data.color=color
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
area("Key / giant softbox",(-3,-4,11),1900,8,(1,.80,.59),(0,0,0))
area("Rim / daylight",(4,6,8),1600,7,(.46,.81,1),(1,0,0))
area("Front fill",(7,-8,5),750,5,(.75,.89,1),(1,0,0))

scene.render.engine="BLENDER_EEVEE"
scene.eevee.taa_render_samples=16 if args.quality=="preview" else 32
scene.render.resolution_x=960 if args.quality=="preview" else 1920
scene.render.resolution_y=540 if args.quality=="preview" else 1080
scene.render.resolution_percentage=100
scene.render.fps=FPS;scene.frame_start=args.start;scene.frame_end=args.end
scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGB"
scene.render.film_transparent=False
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.view_settings.exposure=.3
scene.render.use_file_extension=True
set_linear_animation()
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"hurry-up-and-wait.blend"))
manifest={
 "title":"Hurry Up and Wait","created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "blender_version":bpy.app.version_string,"blender_build_hash":bpy.app.build_hash.decode(),
 "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 "fps":FPS,"frames":[1,END],"rendered_frame_range":[args.start,args.end],"duration_seconds":END/FPS,
 "resolution":[scene.render.resolution_x,scene.render.resolution_y],
 "quality":args.quality,"all_geometry":"Original, generated by this script","AI_assistance":"Codex authored and revised bpy script",
 "physical_simulation":False,"motion":"Choreographed procedural paths and keyframes","external_assets":[],
 "render_service":"Local Blender EEVEE","objects":len(bpy.data.objects)}
(OUT/"build-manifest.json").write_text(json.dumps(manifest,indent=2))
if args.stills:
    for f in [1,90,190,270,305,380,474]:
        scene.frame_set(f);scene.render.filepath=str(OUT/f"still-{f:04}.png");bpy.ops.render.render(write_still=True)
if args.animation:
    frames=OUT/"frames";frames.mkdir(exist_ok=True)
    scene.render.filepath=str(frames/"frame-")
    bpy.ops.render.render(animation=True)
