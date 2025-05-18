import cv2
import numpy as np
from scipy.spatial import KDTree

def detect_colors(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Color ranges (adjust as needed)
    yellow_low = np.array([20, 100, 100])
    yellow_high = np.array([30, 255, 255])
    yellow_mask = cv2.inRange(hsv, yellow_low, yellow_high)
    
    red_low1 = np.array([0, 100, 100])
    red_high1 = np.array([10, 255, 255])
    red_low2 = np.array([160, 100, 100])
    red_high2 = np.array([180, 255, 255])
    red_mask = cv2.inRange(hsv, red_low1, red_high1) + cv2.inRange(hsv, red_low2, red_high2)
    
    purple_low = np.array([130, 50, 50])
    purple_high = np.array([160, 255, 255])
    purple_mask = cv2.inRange(hsv, purple_low, purple_high)
    
    return yellow_mask, red_mask, purple_mask

def get_centroid(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    M = cv2.moments(max(contours, key=cv2.contourArea))
    return (int(M['m10']/M['m00']), int(M['m01']/M['m00'])) if M['m00'] != 0 else None

def process_yellow_line(mask):
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return cv2.ximgproc.thinning(mask)

def detect_structures(region, structure_threshold=1000):
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return np.sum(edges) > structure_threshold

def analyze(image_path):
    image = cv2.imread(image_path)
    yellow, red, purple = detect_colors(image)
    
    # Get important points
    purple_point = get_centroid(purple)
    interest_point = get_centroid(red)
    
    # Process yellow line
    yellow_line = process_yellow_line(yellow)
    line_points = np.column_stack(np.where(yellow_line > 0))[:,[1,0]]
    
    # Determine street direction at POI
    tree = KDTree(line_points)
    _, index = tree.query(interest_point)
    nearby_points = line_points[max(0,index-5):index+5]
    vx, vy, _, _ = cv2.fitLine(nearby_points, cv2.DIST_L2, 0, 0.01, 0.01)
    direction = np.array([vx[0], vy[0]])
    
    # Calculate perpendicular directions
    right_vec = np.array([direction[1], -direction[0]])
    left_vec = np.array([-direction[1], direction[0]])
    
    # Define regions of interest
    size = 50
    roi_size = (100, 100)
    
    # Right region
    right_p1 = tuple((interest_point + right_vec * size).astype(int))
    right_roi = image[right_p1[1]-roi_size[1]//2:right_p1[1]+roi_size[1]//2,
                     right_p1[0]-roi_size[0]//2:right_p1[0]+roi_size[0]//2]
    
    # Left region
    left_p1 = tuple((interest_point + left_vec * size).astype(int))
    left_roi = image[left_p1[1]-roi_size[1]//2:left_p1[1]+roi_size[1]//2,
                   left_p1[0]-roi_size[0]//2:left_p1[0]+roi_size[0]//2]
    
    # Detect structures
    right_structures = detect_structures(right_roi) if right_roi.size > 0 else False
    left_structures = detect_structures(left_roi) if left_roi.size > 0 else False
    
    print(f"Structures on the right: {'Yes' if right_structures else 'No'}")
    print(f"Structures on the left: {'Yes' if left_structures else 'No'}")

    return right_structures,left_structures

if __name__ == "__main__":
    analyze("satellite_tile.png")