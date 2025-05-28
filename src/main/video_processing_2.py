import cv2
from ultralytics import solutions, YOLO
from datetime import datetime
from utils.paths import project_path


class SelectPointsWindow:
    def __init__(self):
        self.region_points = []
        self.current_point = None
        self.drawing = False
    
    def select_region(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.region_points.append((x, y))
            self.current_point = (x, y)
            self.drawing = True

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.current_point = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
        
    def show_window(self, cap_path):
        cap = cv2.VideoCapture(cap_path)
        assert cap.isOpened(), "Error reading video file"

        success, first_frame = cap.read()
        if not success:
            raise ValueError("Failed to read the first frame")

        clone = first_frame.copy()
        cv2.namedWindow("Select Region (Press 'y' to confirm)")
        cv2.setMouseCallback("Select Region (Press 'y' to confirm)", self.select_region)

        while True:
            temp_frame = clone.copy()
            
            for i, point in enumerate(self.region_points):
                cv2.circle(temp_frame, point, 5, (0, 0, 255), -1)
                if i > 0:
                    cv2.line(temp_frame, self.region_points[i-1], point, (0, 255, 0), 2)
            
            if self.drawing and self.current_point and len(self.region_points) > 0:
                cv2.line(temp_frame, self.region_points[-1], self.current_point, (0, 255, 0), 2)
            
            cv2.imshow("Select Region (Press 'y' to confirm)", temp_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('y'):
                break
            elif key == ord('n'):
                self.region_points = []

        cv2.destroyAllWindows()

        if not self.region_points:
            raise ValueError("No region points selected")


cap_path = str(project_path("Shopping_centers_data/32134_проход_брунелло_кучинелли_19_10_2024_16_00_00.mp4"))

window = SelectPointsWindow()
window.show_window(cap_path)

cap = cv2.VideoCapture(cap_path)

w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
video_writer = cv2.VideoWriter("object_counting_output.mp4", cv2.VideoWriter_fourcc(*"MJPG"), fps, (w, h))

in_out_counter = solutions.ObjectCounter(
    show=True,
    region=window.region_points,
    model="yolo11n.pt",
    classes=[0],
)
total_counter = "yolo11n.pt"


total_people = None
in_region = None
out_region = None

# Process video
start_time = datetime.now()
while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video processing complete.")
        break
    # Get ALL detections (not just those in region)
    #full_detections = total_counter.track(im0, persist=True, classes=[0])
    
    # Get region-specific counts via ObjectCounter
    results = in_out_counter(im0)

    # write the processed frame
    video_writer.write(results.plot_im)
    
    # Extract counts
    #total_people = len(full_detections[0].boxes)  # Total detected people
    in_region = in_out_counter.in_count  # People inside region
    out_region = in_out_counter.out_count # People outside region
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
video_writer.release()
cv2.destroyAllWindows()

end_time = datetime.now()
with open(str(project_path("outputs/people_counts")), "w") as f:
    f.write(f"{in_region}\n{out_region}\n{str(start_time)}\n{str(end_time)}")
