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

from scipy.spatial.transform import Rotation as R

data_no = 50

nerf_config_path = "outputs/duck_proc/f3rm/2025-05-14_120756/config.yml"
json_output_path = "camera_output.json"
ns_render_output = "camera_image.mp4"
data_log_output = f"collected_data/out_{data_no}.csv"



# connect and initialise arm
swift = utils.init_arm()


#swift.reset()  # move back to default position



# get current position
position = swift.get_position()
print(position)
x, y, z = position if position else print('position unknown')


theta = 90

calibration = np.array([[-0.75973469, -0.61652919, -0.20662751,  0.63120975],
 [-0.59847706,  0.53877725,  0.59291172,  0.39382047],
 [-0.25422119,  0.57411743, -0.77830634,  0.6011442 ],
 [ 0,          0,          0,          1.        ]])




def on_press(key):
    position = swift.get_position()
    print("position value", position)

    rot = swift.get_servo_angle()

    print("rotation", rot)
    x, y, z = position
    gripper_state = swift.get_gripper_catch()

    global theta

    try:
        if key == keyboard.Key.up:
            z += z_step
        elif key == keyboard.Key.down:
            z -= z_step
        elif key == keyboard.Key.left:
            x -= step
        elif key == keyboard.Key.right:
            x += step
        elif key.char == 'z':
            y += step
        elif key.char == 'c':
            y -= step
        elif key.char == 'm':
            print(gripper_state)
            if gripper_state == 0:
                swift.set_gripper(True)
            elif gripper_state == 1:
                swift.set_gripper(False)
            else:
                print('error with gripper')
            gripper_state = swift.get_gripper_catch()
        elif key.char == 'p':
            theta += theta_step
        elif key.char == 'o':
            theta -= theta_step
        else:
            return

        swift.set_position(x, y, z, speed=speed)
        position = swift.get_position()
        x_real, y_real, z_real = position
        swift.set_servo_angle(servo_id=3, angle=theta)
        print(f"Moved to x={x_real:.1f}, y={y_real:.1f}, z={z_real:.1f}")
        timestamp = datetime.now().isoformat(timespec='seconds')
        data_log.append([x_real, y_real, z_real, gripper_state, timestamp])

    except AttributeError:
        pass

# calibration
'''
get the rotations for : 
world/colmap - > robot 
'''
R_world_to_nerf = np.eye(3)
t_world_to_nerf = np.ones((3,1))

def get_w2c_matrix(x,y,z, theta):
    world_to_cam = np.eye(4)
    
    rotation = R.from_euler('XYZ', [0, 0, theta], degrees=True)

    world_to_cam[:3, :3] = rotation.as_matrix()


    world_to_cam[0, 3] = x / 1000 - 0.17
    world_to_cam[1, 3] = y / 1000
    world_to_cam[2, 3] = z / 1000

    print(world_to_cam)



    world2colmap_transform = np.array([[-0.59989827, -0.72288046,  0.34287886,  2.10634284],
                                       [-0.76156189,  0.64728991,  0.03223754,  4.62163948],
                                       [-0.24524592, -0.24178423, -0.9388263,   1.21333575],
                                       [ 0.,          0.,          0.,          1.        ]])
    
    colmap_frame = world_to_cam @ world2colmap_transform

    print(colmap_frame.shape)

    world2nerf = colmap2nerf_convert(colmap_frame)

    return world2nerf


def colmap2nerf_convert(colmap_frame):
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


    applied_transform = np.array([
        [0.0, 1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]]
        )


    colmap_frame[0:3, 1:3] *= -1
    colmap_frame = applied_transform @ colmap_frame
    colmap_frame[:3, 3] *= scale

    colmap2nerf = dataparser_transform @ colmap_frame

    return colmap2nerf



# get nerf and feature field
# nerf_config_path = "outputs/duck_proc/f3rm/2025-05-14_122555/config.yml"

# teleop arm to grasp object
def exit_training_teleop(json_output_path, nerf_config_path, ns_render_output, data_log_output):
    global theta
    global calibration
    global data_no
    def on_release(key):
        if key == keyboard.Key.esc:
            print("Exiting teleop...")
            x, y, z = swift.get_position()

            rotation = theta - swift.get_servo_angle()[0]
            print("servo angles", rotation)

            world_to_cam = get_w2c_matrix(x, y, z, rotation)
            print("w2c",world_to_cam)
            generate_camera_path_json(json_output_path, world_to_cam)#calibration @ world_to_cam)
            ns_render(nerf_config_path, json_output_path, ns_render_output, data_no)



            with open(data_log_output, mode="w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["X", "Y", "Z", "Gripper", "Timestamp"])
                timestamp = datetime.now().isoformat(timespec='seconds')
                 ## TODO Fix this


                log = [x , y, z, theta, timestamp]
                print(log)
                writer.writerow(log)
            return True  # only stop on ESC
    return on_release


# Start keyboard listener
with keyboard.Listener(on_press=on_press, on_release= exit_training_teleop(json_output_path, nerf_config_path, ns_render_output, data_log_output)) as listener:
    listener.join()


# insert artificial viewpoint over gripper
'''
get R, t for transformation from base to gripper origin
get x, y, z, theta of gripper 
'''



# record grasp and rendered viewpoint

# give score to grasp



