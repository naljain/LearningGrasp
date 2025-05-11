import os
import sys
import time
import csv
from datetime import datetime

from uarm.wrapper import SwiftAPI
from pynput import keyboard
from uarm.utils.log import logger

def init_arm():
    swift = SwiftAPI()
    swift.waiting_ready()
    swift.set_mode(0)
    swift.set_gripper(False)  # open gripper
    return swift

def gripper_open():
    pass

def gripper_close():
    pass

