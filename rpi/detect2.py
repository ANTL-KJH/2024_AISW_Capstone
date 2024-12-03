from edge_tpu_silva import process_detection

# Example Usage with Required Parameters
model_path = '192_yolov8n_full_integer_quant_edgetpu.tflite'
input_path = 'videoplayback.mp4'
imgsz = 192

# Run the object detection process
outs = process_detection(model_path, input_path, imgsz)

for _, _ in outs:
  pass