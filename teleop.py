import os
import sys
import time
import csv
from datetime import datetime

from uarm.wrapper import SwiftAPI
from pynput import keyboard
from uarm.utils.log import logger

'''
servo_id for servo 3
'''


# setup arm limits
X_MIN, X_MAX = 50, 300
Y_MIN, Y_MAX = -150, 150
Z_MIN, Z_MAX = 0, 150


# connect and initialise arm
swift = SwiftAPI()
swift.waiting_ready()
swift.set_mode(0)
swift.set_gripper(False)  # open gripper
swift.set_servo_angle(servo_id=3, angle=90)

# swift.get_servo_attach(servo_id=2)

info = swift.get_device_info()

# get current position
position = swift.get_position()
print(position)
x, y, z = position if position else print('position unknown')
theta = 90
# theta = 0

# movement settings
step = 5  # mm perss key press
z_step = 5  # mm up/down
speed = 5000  # speed of motion
theta_step = 2

# logging setup
output_dir = ''
output_name = 'test.csv'
data_log = []


# keyboard controls

def on_press(key):
    position = swift.get_position()
    x, y, z = position
    theta = 90
    gripper_state = swift.get_gripper_catch()
    print('theta', theta)


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


def exit_teleop(log, dir, fname):
    def on_release(key):
        if key == keyboard.Key.esc:
            print("Exiting teleop...")

            with open(fname, mode="w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["X", "Y", "Z", "Gripper", "Timestamp"])
                writer.writerows(log)
            return False  # only stop on ESC
    return on_release


if __name__ == "__main__":
    with keyboard.Listener(on_press=on_press,
                           on_release=exit_teleop(data_log, output_dir,
                                                  output_name)) as listener:
        listener.join()

    # swift.reset()  # move back to default position
    swift.disconnect()



