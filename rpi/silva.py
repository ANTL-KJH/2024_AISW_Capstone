from edge_tpu_silva import process_detection
import cv2, time
import numpy as np
from ultralytics import YOLO

# Example Usage with Required Parameters
# model_path = '240_yolov8n_full_integer_quant_edgetpu.tflite'
# input_path = 'path/to/your/input/video.mp4'
# input_path = 'obama.jpg'
imgsz = 192

from picamera2 import Picamera2, Preview

camera = Picamera2()

preview_config = camera.create_preview_configuration(main={"size": (1280, 720), "format": "RGB888"})
camera.configure(preview_config)
camera.start()
model = YOLO(model='192_yolov8n_full_integer_quant_edgetpu.tflite', task="detect", verbose=False)

while 1:
    np_array = camera.capture_array()
    input_path = np_array[:, :, :3]
    image = cv2.resize(np_array, (192, 192))

    # input_path = np.expand_dims(np_array, axis=0)

    # Run the object detection process
    start_time = time.time()
    outs = model.predict(
        source=input_path,
        conf=0.5,
        imgsz=imgsz,
        verbose=False,
        stream=False,
        show=True, )
    # outs = process_detection(model_path, input_path, imgsz, show=True)

    # frame_count = 0
    start_time = time.time()
    for out in outs:

        objs_lst = []
        for box in out.boxes:
            obj_cls, conf, bb = (
                box.cls.numpy()[0],
                box.conf.numpy()[0],
                box.xyxy.numpy()[0],
            )
            label = out.names[int(obj_cls)]
            ol = {
                "id": obj_cls,
                "label": label,
                "conf": conf,
                "bbox": bb,
            }
            objs_lst.append(ol)

            print(label)
            # print("  id:    ", obj_cls)
            # print("  score: ", conf)
            # print("  bbox:  ", bb)

        # frame_count += 1
        # elapsed_time = time.time() - start_time
        # fps = frame_count / elapsed_time

        # print (objs_lst, fps)
        print(objs_lst)
        #print("--- %s seconds ---" % (time.time() - start_time))

        # Break the loop if 'esc' key is pressed for video or camera
        if cv2.waitKey(1) == 27:
            break
    # for _, _ in outs:
    # pass