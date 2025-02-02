# Set UTF-8 locale
import locale
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
locale.getpreferredencoding = lambda: "UTF-8"

# Mount Drive
from google.colab import drive
drive.mount('/content/drive')

# Install dependencies
!pip install ultralytics

# Setup paths
DRIVE_PATH = "/content/drive/MyDrive/yolo_dataset"
COLAB_PATH = "/content/dataset"

# Create dataset structure
import yaml

dataset_config = {
    'path': COLAB_PATH,
    'train': 'images',
    'val': 'images',
    'names': {
        0: 'battery',
        1: 'gift_card',
        2: 'garbage',
        3: 'can'
    }
}

# Create directories and copy data
!mkdir -p {COLAB_PATH}/images {COLAB_PATH}/labels
!cp -r "{DRIVE_PATH}/images/"* "{COLAB_PATH}/images/" || true
!cp -r "{DRIVE_PATH}/labels/"* "{COLAB_PATH}/labels/" || true

# Save YAML config
with open(f'{COLAB_PATH}/dataset.yaml', 'w', encoding='utf-8') as f:
    yaml.safe_dump(dataset_config, f, allow_unicode=True)

# Train model
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.train(
    data=f'{COLAB_PATH}/dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='yolo_custom'
)

# Save to Drive safely
!cp -r runs/detect/yolo_custom/* "{DRIVE_PATH}/results/" || true