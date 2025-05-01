import onnxruntime as ort

# สร้าง SessionOptions และตั้งค่า Graph Optimization
session_options = ort.SessionOptions()
session_options.log_severity_level = 1
session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

# โหลดโมเดล ONNX
session = ort.InferenceSession("best9.onnx", sess_options=session_options, providers=["CUDAExecutionProvider"])
# session = ort.InferenceSession("model.onnx", sess_options=session_options, providers=["CPUExecutionProvider"])


# ทดสอบการรันโมเดล
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# ใส่ข้อมูลตัวอย่าง
import numpy as np
input_data = np.random.rand(1, 3, 640, 640).astype(np.float32)  # แก้ขนาดตามโมเดล
result = session.run([output_name], {input_name: input_data})

print("ผลลัพธ์:", result)
