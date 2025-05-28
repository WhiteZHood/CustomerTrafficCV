import os
import cv2
import json
from tqdm import tqdm
from ultralytics import YOLO
from PIL import Image
from utils.paths import project_path

IMAGE_DIR = str(project_path("March_week_img/2025_03_25_Tue"))
OUTPUT_JSON = str(project_path("coco_annotations.json"))

CATEGORY_ID = 1  # COCO требует, чтобы категории начинались с 1, а не 0

categories = [{
    "id": CATEGORY_ID,
    "name": "person",
    "supercategory": "person"
}]

model_name = "yolov8n.pt"
model = YOLO(model_name)

images = []
annotations = []
annotation_id = 1
image_id = 1

image_files = sorted([
    f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))
])

for img_name in tqdm(image_files, desc="Обработка изображений"):
    img_path = os.path.join(IMAGE_DIR, img_name)
    img = Image.open(img_path)
    width, height = img.size

    images.append({
        "id": image_id,
        "file_name": img_name,
        "width": width,
        "height": height
    })

    results = model(img_path)[0]

    for box in results.boxes:
        cls = int(box.cls.item())
        if cls != 0:
            continue

        x1, y1, x2, y2 = box.xyxy[0].tolist()
        bbox_width = x2 - x1
        bbox_height = y2 - y1

        coco_bbox = [x1, y1, bbox_width, bbox_height]
        area = bbox_width * bbox_height

        annotations.append({
            "id": annotation_id,
            "image_id": image_id,
            "category_id": CATEGORY_ID,
            "bbox": coco_bbox,
            "area": area,
            "iscrowd": 0,
            "segmentation": []
        })
        annotation_id += 1

    image_id += 1


coco_dict = {
    "info": {
        "description": f"Predictions with {model_name} (person)",
        "version": "1.0",
        "year": 2025
    },
    "licenses": [],
    "images": images,
    "annotations": annotations,
    "categories": categories
}

with open(OUTPUT_JSON, "w") as f:
    json.dump(coco_dict, f, indent=2)

print(f"\n✅ Разметка завершена! COCO JSON сохранён в: {OUTPUT_JSON}")


