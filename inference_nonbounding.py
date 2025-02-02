import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLO model
model = YOLO('model/best_1.pt')

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

zoom_factor = 1.0
shift_x, shift_y = 0, 0

# Define output display size
display_width, display_height = 1920, 1080  # Change this based on your fullscreen resolution

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image.")
        break

    # Run YOLO inference
    results = model(frame)

    # Draw filled bounding boxes with bigger text inside the box
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()
        for box, cls in zip(boxes, classes):
            x1, y1, x2, y2 = box
            if cls in [1, 3]:  
                color = (0, 255, 0)
                label = "Gift Card/Can"
            elif cls in [0, 2]:  
                color = (0, 0, 255)
                label = "Battery/Garbage"
            else:
                color = (255, 255, 255)
                label = "Other"

            # Draw the filled bounding box
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness=-1)

            # Calculate text size to fit inside the box
            font_scale = 0.8  # You can adjust the value for larger or smaller text
            font_thickness = 2
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
            text_width, text_height = text_size

            # Calculate the position of the text to center it within the box
            text_x = int(x1 + (x2 - x1 - text_width) / 2)
            text_y = int(y1 + (y2 - y1 + text_height) / 2)

            # Place the text inside the box with white color for visibility
            cv2.putText(frame, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)

    # Zoom by cropping the center
    frame_height, frame_width = frame.shape[:2]
    zoomed_width = int(frame_width / zoom_factor)
    zoomed_height = int(frame_height / zoom_factor)
    center_x, center_y = frame_width // 2, frame_height // 2
    x1 = max(0, center_x - zoomed_width // 2)
    y1 = max(0, center_y - zoomed_height // 2)
    x2 = min(frame_width, center_x + zoomed_width // 2)
    y2 = min(frame_height, center_y + zoomed_height // 2)
    zoomed_frame = frame[y1:y2, x1:x2]

    # Get new dimensions after zoom for resizing
    zoomed_frame_height, zoomed_frame_width = zoomed_frame.shape[:2]
    aspect_ratio_frame = zoomed_frame_width / zoomed_frame_height

    # Compute scaling factor to fit the frame inside the display
    aspect_ratio_display = display_width / display_height

    if aspect_ratio_frame > aspect_ratio_display:
        # Fit width to display, adjust height to maintain aspect ratio
        new_width = display_width
        new_height = int(display_width / aspect_ratio_frame)
    else:
        # Fit height to display, adjust width to maintain aspect ratio
        new_height = display_height
        new_width = int(display_height * aspect_ratio_frame)

    # Resize frame to fit display while keeping aspect ratio
    resized_frame = cv2.resize(zoomed_frame, (new_width, new_height))

    # Create grey background
    background = np.full((display_height, display_width, 3), (128, 128, 128), dtype=np.uint8)

    # Compute centering offsets
    x_offset = (display_width - new_width) // 2 + shift_x
    y_offset = (display_height - new_height) // 2 + shift_y

    # Ensure frame stays within bounds
    x_offset = np.clip(x_offset, 0, display_width - new_width)
    y_offset = np.clip(y_offset, 0, display_height - new_height)

    # Overlay the resized frame onto the background
    background[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_frame

    # Show the result
    cv2.imshow('YOLO Webcam', background)

    # Handle key presses for translation
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('w'):
        shift_y -= 10  # Move up
    elif key == ord('s'):
        shift_y += 10  # Move down
    elif key == ord('a'):
        shift_x -= 10  # Move left
    elif key == ord('d'):
        shift_x += 10  # Move right
    elif key == ord('=') or key == ord('+'):
        zoom_factor = min(zoom_factor + 0.1, 5.0)
    elif key == ord('-'):
        zoom_factor = max(1.0, zoom_factor - 0.1)

# Release and close
cap.release()
cv2.destroyAllWindows()
