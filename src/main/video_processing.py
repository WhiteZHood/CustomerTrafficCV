from ultralytics import YOLO
from utils.paths import project_path


model = YOLO('yolov8m.pt')
results = model.track(source=str(project_path('Shopping_centers_data/32134_проход_брунелло_кучинелли_19_10_2024_16_00_00.mp4')), conf=0.6, classes=[0],show=True, tracker="bytetrack.yaml")
