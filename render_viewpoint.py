import numpy as np
import json
import subprocess
import os

config_path = "outputs/duck_proc/f3rm/2025-05-14_120756/config.yml"
ckpt_path = "outputs/duck_proc/f3rm/2025-05-14_120756/nerfstudio_models/step-000004000.ckpt"

json_path = "camera_path_test.json"

output_path = "video_output.mp4"


#  Camera intrinsics and pose

# H, W = 480, 640
# focal = 50.0
# K = torch.tensor([
#     [focal, 0, W / 2],
#     [0, focal, H / 2],
#     [0, 0, 1]
# ], dtype=torch.float32)


# cam_to_world_matrices = [
#     np.array([
#         [7.86e-01, -5.08e-01, 3.53e-01, -3.002e+02],
#         [-5.29e-01, -8.48e-01, -4.36e-02, 2.12e02],
#         [3.21e-01, -1.522e-01, -9.347e-01, 2.03e02],
#         [0.0, 0.0, 0.0, 1.]
#     ]),
# ]

dataparser_transform = np.array([
        [
            0.17285069823265076,
            0.8305922150611877,
            -0.529376208782196,
            -0.034270286560058594
        ],
        [
            0.8236364126205444,
            0.17285069823265076,
            0.5401349067687988,
            -0.33935973048210144
        ],
        [
            0.5401349067687988,
            -0.529376208782196,
            -0.6542286276817322,
            0.14749151468276978
        ],
        [
            0,
            0,
            0, 
            1]
    ])

scale = 0.20857019136345292

colmap_frame12 = np.array([
                [
                    0.047408775279113115,
                    -0.9984658429242282,
                    -0.028607141418621425,
                    3.391198974189175
                ],
                [
                    0.9977378619410376,
                    0.045968837544282465,
                    0.04905124691742652,
                    1.3433303151491138
                ],
                [
                    -0.04766095756341381,
                    -0.030867887657528806,
                    0.9983865016293543,
                    2.4329084513705532
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ])

colmap_frame17 = np.array([
                [
                    -0.5258952943687721,
                    0.552363397325042,
                    -0.6467834387616307,
                    -2.273491650409511
                ],
                [
                    -0.8503384593812825,
                    -0.3245106952120952,
                    0.4142672002343773,
                    3.692098656239071
                ],
                [
                    0.01893789475758768,
                    0.7678460040844781,
                    0.6403544878843672,
                    -1.663726125576306
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ])

applied_transform = np.array([
    [0.0, 1.0, 0.0, 0.0],
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, -1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0]]
    )


# colmap_frame12[0:3, 1:3] *= -1
colmap_frame17 = applied_transform @ colmap_frame17
colmap_frame17[:3, 3] *= scale

test = dataparser_transform @ colmap_frame17
scale_matrix = np.array([[scale, 0, 0, 0],
                         [0, scale, 0, 0],
                         [0, 0, scale, 0],
                         [0, 0, 0, 1]])
# test_scaled =  test @ scale_matrix

print(test)
# test[:3, 3] *= scale

print(test.shape)
# print(test_scaled)
# test[:3, 3] *= scale

# test[0:3, 1:3] *= -1

print(test)

cam_to_world_matrices = [test]

# Construct the JSON structure


def generate_camera_path_json(json_output_path, cam_to_world_matrix):
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
    camera_path_data["camera_path"].append({
            "camera_to_world": (cam_to_world_matrix).flatten().tolist(),  # Flatten to 16-element list
            "fov": 50,
            "aspect": 1.0
    })

    with open(json_output_path, "w") as f:
        json.dump(camera_path_data, f, indent=2)

    print("Saved camera_path.json")


def ns_render(config_path, json_path, output_path, number):
    '''
    ns-render camera-path --load-config outputs/duck_proc/f3rm/2025-05-14_120765/config.yml 
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
    ffmpeg_command = ["ffmpeg", "-i", output_path, f"collected_data/out{number}_%d.png"]

    print("Running ns-render...")
    subprocess.run(ns_command)
    print("Running ffmpeg")
    subprocess.run(ffmpeg_command)

if __name__ == "__main__":
    ns_render(config_path, json_path, output_path)
