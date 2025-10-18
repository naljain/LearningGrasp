# import c,v2
import cv2
import numpy as np

# Load Image
image_name = "/home/matthew/data/nerfstudio/duck_proc/images/frame_00015.jpg"
img = cv2.imread(image_name)
if img is None:
    raise FileNotFoundError(f"Could not load image: {image_name}")

# Convert to grayscale
grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Contrast Enhancement
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
enhanced_img = clahe.apply(grey_img)

# Initialize AprilTag detector
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# Detect AprilTags
corners, ids, _ = detector.detectMarkers(enhanced_img)
print('corners are', corners)

if ids is not None and len(corners) > 0:
    print(f"Detected AprilTags: {ids.flatten()}")
    # cv2.aruco.drawDetectedMarkers(img, corners, ids)
    # cv2.imshow('Detected AprilTags', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
else:
    print("No AprilTags detected. Please click 4 corners of the tag (top-left, top-right, bottom-right, bottom-left).")

    manual_corners = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            manual_corners.append((x, y))
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow('Manual Corner Selection', img)

            if len(manual_corners) == 4:
                print("\nManual corners (in order):")
                for i, pt in enumerate(manual_corners):
                    print(f"Corner {i+1}: {pt}")
                cv2.destroyAllWindows()


    cv2.imshow('Manual Corner Selection', img)
    cv2.setMouseCallback('Manual Corner Selection', click_event)

    # Wait until 4 corners are clicked
    while True:
        if len(manual_corners) == 4:
            break
        if cv2.waitKey(20) & 0xFF == 27:  # Esc to exit early
            print("User exited before completing corner selection.")
            exit()

    cv2.destroyAllWindows()


# === AprilTag pose estimation (PnP) ===
tag_size = 100 / 1000  # meters
object_points = np.array([
    [-tag_size / 2, tag_size / 2, 0],
    [tag_size / 2, tag_size / 2, 0],
    [tag_size / 2, -tag_size / 2, 0],
    [-tag_size / 2, -tag_size / 2, 0]
], dtype=np.float32)

# Use detected or manually clicked image points
if ids is not None and len(corners) > 0:
    image_points = corners[0][0].astype(np.float32)
elif len(manual_corners) == 4:
    image_points = np.array(manual_corners, dtype=np.float32)
else:
    raise ValueError("Insufficient corner information for pose estimation.")

# Intrinsics and distortion from COLMAP


w = 4032
h = 3024
fl_x = 3149.8205568434605
fl_y = 3144.9052845897986
cx =1988.5112210225268
cy = 1510.91478762875
k1 = 0.06181398164562204
k2 = -0.09879480093473737
p1 = -0.0002816293708418898
p2 = 0.00048731735652577334

K = np.array([
    [fl_x, 0, cx ],
    [0, fl_y, cy],
    [0, 0, 1]])

dist_coeffs = np.array([
    k1,
    k2,
    p1,
    p2
], dtype=np.float32)

# Pose estimation
success, rvec, tvec = cv2.solvePnP(object_points, image_points, K, dist_coeffs)

if not success:
    raise RuntimeError("solvePnP failed to estimate pose.")

# Convert rvec to 3x3 rotation matrix
R, _ = cv2.Rodrigues(rvec)

# 4x4 Transform from tag to camera
tag2camera = np.eye(4)
tag2camera[:3, :3] = R
tag2camera[:3, 3] = tvec.flatten()
print("\n transformation (output of pnp) -> tag_to_cam:\n", tag2camera)


colmap_frame = np.array([
                [
                    -0.5687018073497259,
                    -0.8220021370839751,
                    0.029845283488904077,
                    2.059857597959175
                ],
                [
                    0.7514399503779359,
                    -0.5044417340969084,
                    0.42529582395940463,
                    4.50265180004786
                ],
                [
                    -0.3345388696297641,
                    0.2642934420879218,
                    0.9045621709844813,
                    0.7833599092859005
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            ])


# to try if it doesnt work: inverse of colmap frame here 
world2colmap = np.linalg.inv(colmap_frame) @ tag2camera



print('world to colmap transform', world2colmap)





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


# colmap_frame12[0:3, 1:3] *= -1
colmap_frame = applied_transform @ world2colmap
colmap_frame[:3, 3] *= scale

world2nerf = dataparser_transform @ colmap_frame


'''
april tag is world origin --> w (0, 0, 0)

pnp 
    gives april tag pose in colmap coords
    pnp retruns translation and R
    convert R to rodrigues 
    stack to give homogenous transform matrix

world 2 colmap 
    from json 

get april tag location in colmap frame
'''
