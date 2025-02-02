import cv2
import serial
import numpy as np
from ultralytics import YOLO

# Load serial
ser = serial.Serial('/dev/cu.usbserial-0001', 9600, timeout=1)

# Load YOLO model
model = YOLO('model/best_1.pt')

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

zoom_factor = 1.0
shift_x, shift_y = 0, 0

# Define output display size
display_width, display_height = 1920, 1080  # adjust as needed

# Variables for drawing ROI
drawing = False
roi_start_x, roi_start_y, roi_end_x, roi_end_y = -1, -1, -1, -1

def draw_rectangle(event, x, y, flags, param):
    global drawing, roi_start_x, roi_start_y, roi_end_x, roi_end_y
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        roi_start_x, roi_start_y = x, y
        roi_end_x, roi_end_y = x, y  # initialize end point to current point

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            roi_end_x, roi_end_y = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        roi_end_x, roi_end_y = x, y

cv2.namedWindow("YOLO Webcam")
cv2.setMouseCallback("YOLO Webcam", draw_rectangle)

# Flag to track whether we've already sent the serial command for a blue object
blue_command_sent = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image.")
        break

    # Copy the full frame to work on
    full_frame = frame.copy()

    # Boolean flag to check if at least one blue object is found in this frame
    blue_detected = False

    # If an ROI has been drawn, display the ROI rectangle on the full frame.
    if roi_start_x != -1 and roi_start_y != -1 and roi_end_x != -1 and roi_end_y != -1:
        # Draw the ROI rectangle (in blue)
        cv2.rectangle(full_frame, (roi_start_x, roi_start_y), (roi_end_x, roi_end_y), (255, 0, 0), 2)

        # Ensure the ROI is valid
        if roi_end_x > roi_start_x and roi_end_y > roi_start_y:
            # Crop the ROI from the frame for detection
            roi = frame[roi_start_y:roi_end_y, roi_start_x:roi_end_x]
            results = model(roi)

            # Process each detection result
            for result in results:
                boxes = result.boxes.xyxy.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy()
                for box, cls in zip(boxes, classes):
                    x1, y1, x2, y2 = box
                    # Adjust the coordinates relative to the full frame by adding the ROI offset.
                    x1_full = int(x1) + roi_start_x
                    y1_full = int(y1) + roi_start_y
                    x2_full = int(x2) + roi_start_x
                    y2_full = int(y2) + roi_start_y

                    # Set color and label based on class
                    if cls == 0:
                        color = (0, 0, 255)  # Red
                        label = "Battery"
                    elif cls == 1:
                        color = (0, 255, 0)  # Green
                        label = "Plastic"
                    elif cls == 2:
                        color = (0, 0, 255)  # Red
                        label = "Garbage"
                    elif cls == 3:
                        color = (0, 255, 0)  # Green
                        label = "Metal"
                    else:
                        # Default color and label if needed
                        color = (255, 255, 255)
                        label = "Unknown"

                    # Check if the object is in the blue zone (adjust condition as needed)
                    if x1_full <= roi_start_x:
                        # Mark that a blue object was detected in this frame
                        blue_detected = True
                        # Optionally, change color for display to blue
                        color = (255, 0, 0)  # Blue

                    # Draw a filled bounding box on the full frame
                    cv2.rectangle(full_frame, (x1_full, y1_full), (x2_full, y2_full), color, thickness=-1)

                    # Determine text size and location
                    font_scale = 0.8
                    font_thickness = 2
                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
                    text_width, text_height = text_size
                    text_x = int(x1_full + (x2_full - x1_full - text_width) / 2)
                    text_y = int(y1_full + (y2_full - y1_full + text_height) / 2)
                    cv2.putText(full_frame, label, (text_x, text_y),
                                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)

    # Outside of the detection loop: handle the serial command
    if blue_detected and not blue_command_sent:
        ser.write(b'1')  # Send the command once
        blue_command_sent = True
    elif not blue_detected:
        # Reset the flag so that a new blue detection in a future frame can trigger the command again
        blue_command_sent = False

    # Resize full_frame to fit the display window while preserving aspect ratio.
    frame_height, frame_width = full_frame.shape[:2]
    aspect_ratio_frame = frame_width / frame_height
    aspect_ratio_display = display_width / display_height

    if aspect_ratio_frame > aspect_ratio_display:
        new_width = display_width
        new_height = int(display_width / aspect_ratio_frame)
    else:
        new_height = display_height
        new_width = int(display_height * aspect_ratio_frame)

    resized_frame = cv2.resize(full_frame, (new_width, new_height))
    background = np.full((display_height, display_width, 3), (128, 128, 128), dtype=np.uint8)
    x_offset = (display_width - new_width) // 2 + shift_x
    y_offset = (display_height - new_height) // 2 + shift_y
    x_offset = np.clip(x_offset, 0, display_width - new_width)
    y_offset = np.clip(y_offset, 0, display_height - new_height)
    background[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized_frame

    cv2.imshow('YOLO Webcam', background)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('w'):
        shift_y -= 10
    elif key == ord('s'):
        shift_y += 10
    elif key == ord('a'):
        shift_x -= 10
    elif key == ord('d'):
        shift_x += 10
    elif key in [ord('='), ord('+')]:
        zoom_factor = min(zoom_factor + 0.1, 5.0)
    elif key == ord('-'):
        zoom_factor = max(1.0, zoom_factor - 0.1)

cap.release()
cv2.destroyAllWindows()
ser.close()
