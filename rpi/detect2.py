from edge_tpu_silva import process_detection
from picamera2 import Picamera2
import numpy as np
import cv2

# Example Usage with Required Parameters
model_path = '192_yolov8n_full_integer_quant_edgetpu.tflite'
imgsz = 192

# Initialize Picamera2
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (imgsz, imgsz)})
picam2.configure(camera_config)
picam2.start()

try:
    print("Press 'ESC' to exit.")
    while True:
        # Capture frame from Picamera2
        frame = picam2.capture_array()

        # Convert frame to the expected input format for the model
        resized_frame = cv2.resize(frame, (imgsz, imgsz))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)  # Convert to RGB if needed

        # The model expects a batch dimension (expand dims to add batch)
        input_data = np.expand_dims(rgb_frame, axis=0)

        # Run object detection
        outs = process_detection(model_path, input_data, imgsz)

        # Visualize detection results (if needed)
        for result in outs:
            # Assuming result contains bounding box and class information
            box, cls, score = result["box"], result["class"], result["score"]

            # Draw the bounding box on the original frame
            ymin, xmin, ymax, xmax = box
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            label = f"Class {cls}: {score:.2f}"
            cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Display the frame with detections
        cv2.imshow("Object Detection", frame)

        # Exit on ESC key
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    # Clean up
    picam2.stop()
    cv2.destroyAllWindows()
