import os
import sys
import time
import csv
from datetime import datetime

from uarm.wrapper import SwiftAPI
from pynput import keyboard
from uarm.utils.log import logger

import teleop

# connect and initialise arm
swift = SwiftAPI()
swift.waiting_ready()
swift.set_mode(0)
swift.set_gripper(False)  # open gripper


# get nerf and feature field

# calibration
'''
get the rotations for : 
world/colmap - > robot 
'''


# insert artificial viewpoint over gripper
'''
get R, t for transformation from base to gripper origin
get x, y, z, theta of gripper 
'''


# teleop arm to grasp object

# record grasp and rendered viewpoint

# give score to grasp



