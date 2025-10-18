from uarm.wrapper import SwiftAPI
import time
from pose_generation import get_best_grasp

# #dummy
# TARGET_X = 183.8
# TARGET_Y = 1.1
# TARGET_Z = 8.5


best_grasp, score = get_best_grasp()
TARGET_X = best_grasp['x']
TARGET_Y = best_grasp['y']
TARGET_Z = best_grasp['z']
THETA = best_grasp['theta']


#init dont change
INIT_X = 150
INIT_Y = 0
INIT_Z = 150
SPEED = 5000  # mm/s (adjust as needed)

# Connect to the arm
swift = SwiftAPI()
swift.waiting_ready()
swift.set_mode(0)

# Move to the desired position
swift.set_position(x=TARGET_X, y=TARGET_Y, z=TARGET_Z, speed=SPEED)
swift.set_servo_angle(servo_id=3, angle=90-THETA)

print(f"Moving to x={TARGET_X}, y={TARGET_Y}, z={TARGET_Z}...")

# Wait for the movement to finish
time.sleep(2)

pos = swift.get_position()
print(f"Current position: {pos}")


swift.set_gripper(catch=True)
print("Gripper closed.")
time.sleep(2)

#init
swift.set_position(x=INIT_X, y=INIT_Y, z=INIT_Z, speed=SPEED)
print(f"Returning to x={INIT_X}, y={INIT_Y}, z={INIT_Z}...")

pos = swift.get_position()
print(f"Current position: {pos}")
time.sleep(10)

#move back
# Move to the desired position
swift.set_position(x=TARGET_X, y=TARGET_Y, z=TARGET_Z, speed=SPEED)
# swift.set_servo_angle(servo_id=3, angle=90)
print(f"Returning to pick-up position: xx={TARGET_X}, y={TARGET_Y}, z={TARGET_Z}")
time.sleep(2)

swift.set_gripper(catch=False)
print("Gripper opened.")
time.sleep(3)

#init
swift.set_position(x=INIT_X, y=INIT_Y, z=INIT_Z, speed=SPEED)
print(f"Returning to x={INIT_X}, y={INIT_Y}, z={INIT_Z}...")
time.sleep(2)
pos = swift.get_position()
print(f"Current position: {pos}")

swift.set_gripper(catch=True)
print("Gripper closed.")
time.sleep(2)

# Disconnect
swift.disconnect()
print("Done.")