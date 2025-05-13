import numpy as np
import json


config_path = "config.yml"
ckpt_path = "step-000002000.ckpt"


#  Camera intrinsics and pose

# H, W = 480, 640
# focal = 50.0
# K = torch.tensor([
#     [focal, 0, W / 2],
#     [0, focal, H / 2],
#     [0, 0, 1]
# ], dtype=torch.float32)


cam_to_world_matrices = [
    np.array([
        [0, 0, 0, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0.0, 0.0, 0.0, 1.0]
    ]),
]

# Construct the JSON structure
camera_path_data = {
    "camera_type": "perspective",
    "render_height": 300,
    "render_width": 300,
    "camera_path": [],
    "fps": 24,
    "seconds": 0.1,
    "smoothness_value": 0.5,
    "is_cycle": False,
    "crop": None
}

for mat in cam_to_world_matrices:
    camera_path_data["camera_path"].append({
        "camera_to_world": mat.flatten().tolist(),  # Flatten to 16-element list
        "fov": 50,
        "aspect": 1.0
    })

with open("camera_path_test.json", "w") as f:
    json.dump(camera_path_data, f, indent=2)

print("Saved camera_path.json")



