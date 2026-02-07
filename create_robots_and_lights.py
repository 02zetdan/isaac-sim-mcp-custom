"""
Script to create 3x3 Franka robots, add lighting, and place additional robots
This script should be run through the Isaac Sim MCP server using execute_script
"""

import socket
import json

def send_mcp_command(command_type, params=None):
    """Send command to Isaac Sim MCP extension"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 8766))

    command = {
        "type": command_type,
        "params": params or {}
    }

    sock.sendall(json.dumps(command).encode('utf-8'))
    response_data = sock.recv(16384)
    sock.close()

    return json.loads(response_data.decode('utf-8'))

# 1. Check connection
print("Checking connection to Isaac Sim...")
result = send_mcp_command("get_scene_info")
print(f"Scene info: {result}")

# 2. Create physics scene if needed
print("\nCreating physics scene...")
result = send_mcp_command("create_physics_scene", {
    "objects": [],
    "floor": True,
    "gravity": [0, -0.981, 0],
    "scene_name": "robot_party_scene"
})
print(f"Physics scene created: {result}")

# 3. Create 3x3 grid of Franka robots
print("\n" + "="*50)
print("Creating 3x3 Franka robot grid...")
print("="*50)

start_pos = [3.0, 0.0, 0.0]
end_pos = [6.0, 3.0, 0.0]

x_spacing = (end_pos[0] - start_pos[0]) / 2
y_spacing = (end_pos[1] - start_pos[1]) / 2

for i in range(3):
    for j in range(3):
        x = start_pos[0] + i * x_spacing
        y = start_pos[1] + j * y_spacing
        z = start_pos[2]

        position = [float(x), float(y), float(z)]
        print(f"Creating Franka {i},{j} at {position}")

        result = send_mcp_command("create_robot", {
            "robot_type": "franka",
            "position": position
        })
        print(f"  Result: {result}")

# 4. Add enhanced lighting
print("\n" + "="*50)
print("Adding enhanced lighting...")
print("="*50)

lighting_code = """
from pxr import UsdLux, UsdGeom, Gf
import omni.usd

stage = omni.usd.get_context().get_stage()

# Add dome light
print("Adding dome light...")
dome_light = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
dome_light.CreateIntensityAttr(1000.0)

# Add directional light (sun)
print("Adding directional sun light...")
distant_light = UsdLux.DistantLight.Define(stage, "/World/SunLight")
distant_light.CreateIntensityAttr(3000.0)
distant_light.CreateAngleAttr(0.53)
xform = UsdGeom.Xformable(distant_light)
xform.AddRotateXYZOp().Set(Gf.Vec3f(-45, 45, 0))

# Add fill lights
fill_positions = [
    ([10, 10, 5], "FillLight_1"),
    ([-10, 10, 5], "FillLight_2"),
    ([0, -10, 5], "FillLight_3"),
]

for pos, name in fill_positions:
    print(f"Adding {name} at {pos}")
    sphere_light = UsdLux.SphereLight.Define(stage, f"/World/{name}")
    sphere_light.CreateIntensityAttr(2000.0)
    sphere_light.CreateRadiusAttr(0.5)

    xform = UsdGeom.Xformable(sphere_light)
    xform.ClearXformOpOrder()
    translate_op = xform.AddTranslateOp()
    translate_op.Set(Gf.Vec3d(pos[0], pos[1], pos[2]))

print("Lighting setup complete!")
"""

result = send_mcp_command("execute_script", {"code": lighting_code})
print(f"Lighting result: {result}")

# 5. Create G1 robot
print("\n" + "="*50)
print("Creating G1 robot at [3, 9, 0]...")
print("="*50)

result = send_mcp_command("create_robot", {
    "robot_type": "g1",
    "position": [3.0, 9.0, 0.0]
})
print(f"G1 robot created: {result}")

# 6. Create Go1 robot
print("\n" + "="*50)
print("Creating Go1 robot at [2, 1, 0]...")
print("="*50)

result = send_mcp_command("create_robot", {
    "robot_type": "go1",
    "position": [2.0, 1.0, 0.0]
})
print(f"Go1 robot created: {result}")

# 7. Move Go1 robot to [1, 1, 0]
print("\nMoving Go1 robot to [1, 1, 0]...")

move_code = """
from pxr import UsdGeom, Gf
import omni.usd

stage = omni.usd.get_context().get_stage()

# Find the Go1 robot prim (it should be the most recently created Go1)
go1_prim = None
for prim in stage.Traverse():
    if "go1" in prim.GetName().lower() or "Go1" in str(prim.GetPath()):
        go1_prim = prim
        break

if go1_prim:
    print(f"Found Go1 at: {go1_prim.GetPath()}")
    xform = UsdGeom.Xformable(go1_prim)

    # Get existing ops or create new
    ops = xform.GetOrderedXformOps()
    if ops:
        for op in ops:
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
                op.Set(Gf.Vec3d(1.0, 1.0, 0.0))
                print("Moved Go1 to [1, 1, 0]")
                break
    else:
        xform.ClearXformOpOrder()
        translate_op = xform.AddTranslateOp()
        translate_op.Set(Gf.Vec3d(1.0, 1.0, 0.0))
        print("Moved Go1 to [1, 1, 0]")
else:
    print("Could not find Go1 robot to move")
"""

result = send_mcp_command("execute_script", {"code": move_code})
print(f"Move result: {result}")

print("\n" + "="*50)
print("ALL DONE! 🎉")
print("="*50)
print("Created:")
print("  - 9 Franka robots in 3x3 grid")
print("  - Enhanced lighting (dome + sun + 3 fill lights)")
print("  - G1 robot at [3, 9, 0]")
print("  - Go1 robot at [1, 1, 0]")
