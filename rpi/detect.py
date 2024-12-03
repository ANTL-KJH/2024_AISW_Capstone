from edge_tpu_silva import process_detection

# Run the object detection process
outs = process_detection(model_path='path/to/your/model.tflite', input_path='0', imgsz=192)

for _, _ in outs:
  pass