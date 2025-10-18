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

print("Runnning teleopscript")

# setup arm limits
X_MIN, X_MAX = 50, 300
Y_MIN, Y_MAX = -150, 150
Z_MIN, Z_MAX = 0, 150


# swift.get_servo_attach(servo_id=2)


# get current position
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

    # connect and initialise arm
    swift = SwiftAPI()
    swift.waiting_ready()
    swift.set_mode(0)
    swift.set_gripper(False)  # open gripper
    swift.set_servo_angle(servo_id=3, angle=90)


    info = swift.get_device_info()

    position = swift.get_position()
    print(position)
    x, y, z = position if position else print('position unknown')
    theta = 90


    with keyboard.Listener(on_press=on_press,
                           on_release=exit_teleop(data_log, output_dir,
                                                  output_name)) as listener:
        listener.join()

    # swift.reset()  # move back to default position
    swift.disconnect()



