import numpy as np
import json
import subprocess
import os

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

def generate_camera_path_json(output_name, cam_to_world):
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

    with open(output_name, "w") as f:
        json.dump(camera_path_data, f, indent=2)

    print("Saved camera_path.json")


def ns_render(config_path, json_path, output_path):
    '''
    ns-render camera-path --load-config outputs/mug_proc/f3rm/2025-05-11_152252/config.yml
    --camera-path-filename ~/Downloads/camera_path\(3\).json
    --output-path renders/mug_proc/2025-05-11_152252.mp4
    --rendered-output-names feature

    ffmpeg -i renders/mug_proc/2025-05-11_152252.mp4 out%d.png

    '''
    ns_command = [
        "ns-render", "camera-path",
        "--load-config", config_path,
        "--camera-path-filename", json_path,
        "--output-path", output_path,
        "--rendered-output-names", "feature"
    ]
    ffmpeg_command = ["ffmeg", "-i", output_path, "out%d.png"]

    print("Running ns-render...")
    subprocess.run(ns_command)
    print("Running ffmpeg")
    subprocess.run(ffmpeg_command)
