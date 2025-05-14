import os
import subprocess
import sys
import time
import csv
import numpy as np
from uarm.wrapper import SwiftAPI
from pynput import keyboard
from uarm.utils.log import logger

from render_viewpoint import *
from teleop import *
import utils

# connect and initialise arm
swift = utils.init_arm()
# get current position
position = swift.get_position()
print(position)
x, y, z = position if position else print('position unknown')


# calibration
'''
get the rotations for : 
world/colmap - > robot 
'''
R_world_to_nerf = np.eye(3)
t_world_to_nerf = np.ones((3,1))
def get_w2c_matrix(x,y,z):
    world_to_cam = np.eye(4)
    return world_to_cam


# get nerf and feature field
nerf_config_path = ""
json_output_path = ""
ns_render_output = ""


# teleop arm to grasp object
def exit_training_teleop(json_output_path, nerf_config_path, ns_render_output, data_log_output):
    def on_release(key):
        if key == keyboard.Key.esc:
            print("Exiting teleop...")
            x, y, z = swift.get_position()
            world_to_cam = get_w2c_matrix(x, y, z)
            generate_camera_path_json(json_output_path, world_to_cam)
            ns_render(nerf_config_path, json_output_path, ns_render_output)
            with open(data_log_output, mode="w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["X", "Y", "Z", "Gripper", "Timestamp"])
                timestamp = datetime.now().isoformat(timespec='seconds')
                theta = 0 ## TODO Fix this
                log = [x , y, z, theta, timestamp]
                writer.writerows(log)
            return False  # only stop on ESC
    return on_release


# Start keyboard listener
with keyboard.Listener(on_press=on_press, on_release= exit_training_teleop(json_output_path, nerf_config_path, ns_render_output, data_log_output)) as listener:
    listener.join()

swift.reset()  # move back to default position
swift.disconnect()


# insert artificial viewpoint over gripper
'''
get R, t for transformation from base to gripper origin
get x, y, z, theta of gripper 
'''



# record grasp and rendered viewpoint

# give score to grasp



