import cv2
import time
import numpy as np
from picamera2 import Picamera2, Preview
from pycoral.utils.edgetpu import make_interpreter
from pycoral.adapters import common
from ultralytics import YOLO

# Set image size for inference
imgsz = 192

# Set up the camera
camera = Picamera2()
preview_config = camera.create_preview_configuration(main={"size": (1280, 720), "format": "RGB888"})
camera.configure(preview_config)
camera.start()

# Load EdgeTPU model
model_path = '192_yolov8n_full_integer_quant_edgetpu.tflite'
interpreter = make_interpreter(model_path)
interpreter.allocate_tensors()

# Prepare the YOLO model using UltraLytics YOLO
model = YOLO(model=model_path, task="detect", verbose=False)

while True:
    # Capture image from the camera
    np_array = camera.capture_array()
    input_path = np_array[:, :, :3]
    image = cv2.resize(np_array, (192, 192))

    # Prepare input for EdgeTPU model (must be uint8)
    input_array = np.array(image, dtype=np.uint8)

    # Run inference with EdgeTPU
    start_time = time.time()

    # Set up the input tensor
    common.set_input(interpreter, input_array)
    interpreter.invoke()

    # Get the results from the output tensor
    boxes = common.output_tensor(interpreter, 0)
    classes = common.output_tensor(interpreter, 1)
    scores = common.output_tensor(interpreter, 2)

    # Post-process the detections (box, class, score)
    outs = []
    for i in range(len(boxes)):
        if scores[i] > 0.5:  # Confidence threshold
            box = boxes[i]
            obj_cls = int(classes[i])
            conf = scores[i]
            label = model.names[obj_cls]  # Get label from YOLO model
            ol = {
                "id": obj_cls,
                "label": label,
                "conf": conf,
                "bbox": box,
            }
            outs.append(ol)

    # Display the result
    print(outs)

    # Show the processed image with detections
    if cv2.waitKey(1) == 27:  # Break the loop if 'esc' key is pressed
        break

cv2.destroyAllWindows()
