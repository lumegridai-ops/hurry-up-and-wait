"""Independent geometric and kinematic checks against the saved Blender scene."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
s=bpy.context.scene
r=bpy.data.objects["RED / impatient racer"];c=bpy.data.objects["CYAN / steady courier"]
ferry=bpy.data.objects["FERRY / shared departure"]
bar=bpy.data.objects["Barrier arm"]
cars=[r,c]
results={}
def mesh_bounds(obj):
    return [obj.matrix_world @ Vector(v) for v in obj.bound_box]
# Measure gate clearance over the actual crossing frames in the actual saved scene.
# The rod spans a plane x=.50. Only check when a car's full front/body/rear envelope intersects it.
gate_checks=[]
for frame in range(292,327):
    s.frame_set(frame)
    bar_pts=mesh_bounds(bar)
    for car in cars:
        cx,cy,cz=car.location
        if cx-.84<=.50<=cx+.75:
            # Rod rises along y and z from its hinge. Check its height over each car's y envelope.
            hinge=bpy.data.objects["Barrier / actual animated hinge"]
            angle=hinge.rotation_euler.x
            for y in [cy-.62,cy,cy+.62]:
                along=(y-hinge.location.y)/max(math.cos(angle),1e-8)
                if 0<=along<=4.4:
                    z=hinge.location.z+along*math.sin(angle)-.11
                    # Full car incl. antenna is below 1.55 + its animated root height.
                    gate_checks.append({"frame":frame,"car":car.name,"clearance":float(z-(cz+1.55))})
results["gate_envelope_checks"]=len(gate_checks)
results["gate_min_clearance_scene_units"]=min(x["clearance"] for x in gate_checks) if gate_checks else None
assert gate_checks and min(x["clearance"] for x in gate_checks)>.10
# Rolling: angular travel about +Y should match forward translation / radius during boarding.
# Deliberate stationary tire-spinning before boarding is excluded.
rolling=[]
for car in cars:
    wheel=next(o for o in bpy.data.objects if o.parent==car and "rubber wheel" in o.name)
    for a,b in [(60,80),(293,311),(310,325)]:
        if car==r and a==60: pass
        s.frame_set(a);x0=car.location.x;t0=wheel.rotation_euler.y
        s.frame_set(b);dx=car.location.x-x0;dt=wheel.rotation_euler.y-t0
        error=abs(dx-.21*dt)
        rolling.append({"car":car.name,"frames":[a,b],"distance":float(dx),"wheel_arc":float(.21*dt),"error":float(error)})
        assert error<.001
results["rolling"]=rolling
# Once on the ferry, car positions must stay fixed relative to the deck.
carry=[]
for car in cars:
    offsets=[]
    for frame in range(330,505):
        s.frame_set(frame)
        offsets.append(tuple(car.location-ferry.location))
    drift=max(Vector(o).length for o in [Vector(v)-Vector(offsets[0]) for v in offsets])
    carry.append({"car":car.name,"maximum_relative_drift":float(drift)})
    assert drift<.001
results["ferry_carry"]=carry
for car in cars:
    wheel=next(o for o in bpy.data.objects if o.parent==car and "rubber wheel" in o.name)
    s.frame_set(330); angle=wheel.rotation_euler.y
    s.frame_set(434); assert abs(wheel.rotation_euler.y-angle)<.001
results["wheels_stationary_on_moving_ferry"]=True
# Tire axle remains parallel with Y instead of yawing as the tire spins.
axis=[]
for frame in [75,150,299,319,400]:
    s.frame_set(frame)
    for car in cars:
        for wheel in [o for o in bpy.data.objects if o.parent==car and "rubber wheel" in o.name]:
            axle=(wheel.matrix_world.to_3x3() @ Vector((0,0,1))).normalized()
            alignment=abs(axle.dot(Vector((0,1,0))))
            axis.append(alignment);assert alignment>.999
results["minimum_tire_axle_alignment"]=min(axis)
s.frame_set(504)
for name in ["Payoff","Endnote","GO lamp"]:
    assert not bpy.data.objects[name].hide_render,name+" disappears on final frame"
results["final_frame_title_and_signal_persist"]=True
results["status"]="passed"
results["scope"]="Gate envelope, wheel travel during approach/boarding, tire axes and rigid transport with ferry. Not a physical simulation or general collision certification."
(ROOT/"scene-qa.json").write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
