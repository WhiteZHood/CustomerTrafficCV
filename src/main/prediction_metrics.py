import json
import os
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
from ultralytics import YOLO
from utils.paths import project_path


coco_gt = COCO(str(project_path("tests/test_labels/instances_default.json")))  


model = YOLO("models/yolov8n.pt")


predictions = []
image_id_map = {img["file_name"]: img["id"] for img in coco_gt.dataset["images"]}


for img_info in coco_gt.dataset["images"]:
    img_path = str(project_path("data/images/March_week_img_one_folder"))
    
    results = model.predict(img_path, classes=[0], conf=0.25)  # class 0 = person
    
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            w = x2 - x1
            h = y2 - y1
            
            predictions.append({
                "image_id": image_id_map[img_info["file_name"]],
                "category_id": 1,  # Matches your 'person' category
                "bbox": [x1, y1, w, h],
                "score": float(box.conf),
                "area": w * h,
                "iscrowd": 0
            })

with open(str(project_path("predictions.json")), "w") as f:
    json.dump(predictions, f)

coco_dt = coco_gt.loadRes(str(project_path("predictions.json")))
coco_eval = COCOeval(coco_gt, coco_dt, "bbox")
coco_eval.evaluate()
coco_eval.accumulate()
coco_eval.summarize()
