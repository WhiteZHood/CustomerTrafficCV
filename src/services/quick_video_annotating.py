import cv2
import json
from ultralytics import YOLO
from tqdm import tqdm

VIDEO_PATH = "Shopping_centers_data/3235_брунелло_кучинелли_19_10_2024_16.00.59.mp4"
OUTPUT_JSON = "coco_annotations_video.json"

CATEGORY_ID = 1  # COCO 'person' category ID starts at 1

categories = [{
    "id": CATEGORY_ID,
    "name": "person",
    "supercategory": "person"
}]

model = YOLO("yolov8n.pt")

images = []
annotations = []
annotation_id = 1
image_id = 1


cap = cv2.VideoCapture(VIDEO_PATH)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

pbar = tqdm(total=total_frames, desc="Processing video frames")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width = frame.shape[:2]

    file_name = f"frame_{image_id:06d}.jpg"
    images.append({
        "id": image_id,
        "file_name": file_name,
        "width": width,
        "height": height
    })

    results = model(frame)[0]

    for box in results.boxes:
        cls = int(box.cls.item())
        if cls != 0:
            continue

        x1, y1, x2, y2 = box.xyxy[0].tolist()
        bbox_width = x2 - x1
        bbox_height = y2 - y1
        area = bbox_width * bbox_height

        annotations.append({
            "id": annotation_id,
            "image_id": image_id,
            "category_id": CATEGORY_ID,
            "bbox": [x1, y1, bbox_width, bbox_height],
            "area": area,
            "iscrowd": 0,
            "segmentation": []
        })
        annotation_id += 1

    image_id += 1
    pbar.update(1)

pbar.close()
cap.release()

coco_output = {
    "info": {
        "description": "Auto-labeled video frames with YOLOv8 (person)",
        "version": "1.0",
        "year": 2025
    },
    "licenses": [],
    "images": images,
    "annotations": annotations,
    "categories": categories
}

with open(OUTPUT_JSON, "w") as f:
    json.dump(coco_output, f, indent=2)

print(f"\n✅ Finished! COCO JSON saved to: {OUTPUT_JSON}")
