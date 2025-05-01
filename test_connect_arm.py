# #!/usr/bin/env python3
# # Software License Agreement (BSD License)
# #
# # Copyright (c) 2018, UFactory, Inc.
# # All rights reserved.
# #
# # Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import os
import sys
import time
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI
from uarm.utils.log import logger

"""
api test: connect and disconnect
"""

# swift = SwiftAPI('COM9')
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'},
                 callback_thread_pool_size=0, do_not_open=True)

while True:
    try:
        swift.connect()
        swift.disconnect()
        print('thread count:', len(threading.enumerate()), time.time())
    except Exception as e:
        pass


import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"{port.device} - {port.description}")

# from uarm.wrapper import SwiftAPI

# swift = SwiftAPI()
# print(swift.port)  # Should print something like /dev/tty.usbmodem14101
# print(swift.get_device_info())  # Returns a dict with firmware, version, etc.