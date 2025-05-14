import cv2 as cv
import numpy as np

# === Load Image ===
image_name = "mug_proc/images/frame_00006.jpg"
img = cv.imread(image_name)
if img is None:
    raise FileNotFoundError(f"Could not load image: {image_name}")

grey_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# === AprilTag Detection ===
aruco_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_36h11)
parameters = cv.aruco.DetectorParameters()
detector = cv.aruco.ArucoDetector(aruco_dict, parameters)
corners, ids, _ = detector.detectMarkers(grey_img)

if ids is not None and len(corners) > 0:
    for i, corner in enumerate(corners):
        print(f"Tag ID: {ids[i][0]}")
        print("Corners (in image coordinates):")
        for j, point in enumerate(corner[0]):
            print(f"Corner {j}: {point}")
        # Optional: draw the tag
        cv.polylines(img, [np.int32(corner)], True, (0, 255, 0), 2)

    # === AprilTag pose estimation (PnP) ===
    tag_size = 100/1000  # mm
    object_points = np.array([
        [-tag_size / 2, tag_size / 2, 0],
        [tag_size / 2, tag_size / 2, 0],
        [tag_size / 2, -tag_size / 2, 0],
        [-tag_size / 2, -tag_size / 2, 0]
    ], dtype=np.float32)

    # Use the first detected tag
    image_points = corners[0][0].astype(np.float32)

    K = np.array([
        [3162.6917917099686, 0, 2002.6217660372267],
        [0, 3150.400818955349, 1564.6369336051791],
        [0, 0, 1]
    ], dtype=np.float32)

    dist_coeffs = np.array([
        0.041583647358609324,
        -0.08065327514514421,
        -0.0011864718361330247,
        -0.0013845300296879428
    ], dtype=np.float32)

    success, rvec, tvec = cv.solvePnP(object_points, image_points, K,
                                      dist_coeffs)

    if success:
        print("\nPose Estimation Successful!")
        print("Rotation Vector:\n", rvec)
        print("Translation Vector:\n", tvec)

        # Convert rvec to rotation matrix
        R, _ = cv.Rodrigues(rvec)

        # Compose 4x4 transform matrix: T_tag_to_cam
        # This transforms points from tag coordinate system to camera coordinate system
        T_tag_to_cam = np.eye(4)
        T_tag_to_cam[:3, :3] = R
        T_tag_to_cam[:3, 3] = tvec.flatten()

        print("\nTransformation Matrix (T_tag_to_cam):\n", T_tag_to_cam)
    else:
        print("solvePnP failed to estimate pose.")

    # Show image with overlay
    cv.imshow("Detected Tags", img)
    cv.waitKey(0)
    cv.destroyAllWindows()

else:
    print("No AprilTags detected.")

# Define the transform from camera to NeRF world
# This should be determined by your calibration
T_cam_to_nerf = np.array([
    [-0.5815673, -0.65332876, -0.4847071, -1.38999609],
    [0.08120135, -0.63947582, 0.76451097, 3.6932075],
    [-0.80943547, 0.40525573, 0.42494942, -3.17019743],
    [0, 0, 0, 1]
])

# Calculate tag position in NeRF world
# First, transform from tag to camera, then from camera to NeRF
T_tag_to_nerf = T_cam_to_nerf @ T_tag_to_cam

# For verification: tag is at origin in its own frame, where is this point in NeRF?
tag_origin_in_nerf = T_tag_to_nerf @ np.array([0, 0, 0, 1])
print("Tag origin in NeRF coordinates:", tag_origin_in_nerf)


# CORRECTED look_at function
def look_at(cam_pos, target, up):
    # Calculate camera axes
    forward = target - cam_pos  # Camera looks TOWARD target
    forward = forward / np.linalg.norm(forward)

    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)

    camera_up = np.cross(right, forward)
    camera_up = camera_up / np.linalg.norm(camera_up)

    # Create camera-to-world matrix
    c2w = np.eye(4)
    c2w[:3, 0] = right
    c2w[:3, 1] = camera_up
    c2w[:3, 2] = -forward  # Negative because camera Z points backward
    c2w[:3, 3] = cam_pos

    return c2w


# Define a viewpoint that's above the AprilTag in tag coordinate system
height = 0.05  # meters
cam_pos_tag = np.array([0, 0, height])  # Position above the tag
target = np.array([0, 0, 0])  # Looking at the tag origin
up = np.array([0, 1, 0])  # Y-axis is up

# Get camera-to-world transform in tag coordinate system
c2w_tag = look_at(cam_pos_tag, target, up)
print("Camera-to-world in tag coordinates:\n", c2w_tag)

# Transform to get camera-to-world in NeRF coordinates
c2w_nerf = T_tag_to_nerf @ c2w_tag
print("Camera-to-world in NeRF coordinates:\n", c2w_nerf)

# This c2w_nerf matrix can now be used for rendering or controlling the uArm