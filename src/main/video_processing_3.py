import cv2
from ultralytics import YOLO
from utils.paths import project_path


model_version = "yolov8m.pt"
model = YOLO(model_version)

video_path = str(project_path("Shopping_centers_data/32134_проход_брунелло_кучинелли_19_10_2024_16_00_00.mp4"))
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model.track(frame, persist=True, classes=[0])
        
        annotated_frame = results[0].plot()
        cv2.imshow(f"{model_version[:-3]} Tracking", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()

