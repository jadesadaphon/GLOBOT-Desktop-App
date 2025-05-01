import cv2
import numpy as np
import onnxruntime as ort
import ast
import time

class AI():
    def __init__(self,model_path):
        EP_list = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        session_options = ort.SessionOptions()
        session_options.log_severity_level = 1
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.__session = ort.InferenceSession(model_path, session_options, providers=EP_list)
        
        self.processor_name = self.__session.get_providers()

        self.__model_input_name = self.__session.get_inputs()[0].name
        self.__model_output__name = self.__session.get_outputs()[0].name
        
        metadata = self.__session.get_modelmeta().custom_metadata_map
        names_dict = ast.literal_eval(metadata['names'])
        self.__model_class_names = [names_dict[key] for key in sorted(names_dict.keys())]
        
        self.__model_imgsz = ast.literal_eval(metadata['imgsz'])

    def detections(self,image,confidence):
        # รับขนาดของภาพต้นฉบับ
        original_height, original_width = image.shape[:2]

        # ปรับขนาดภาพให้ตรงกับขนาดของโมเดล
        resized_image = cv2.resize(image, (self.__model_imgsz[0],self.__model_imgsz[1]))
        input_image = resized_image.astype(np.float32) / 255.0
        input_image = np.transpose(input_image, (2, 0, 1))
        input_image = np.expand_dims(input_image, axis=0)
        
        # ประมวลผลการตรวจจับ
        outputs = self.__session.run([self.__model_output__name], {self.__model_input_name: input_image})[0]

        detections = self.__post_process(outputs, self.__model_class_names, confidence)
        
        # แปลงตำแหน่ง bounding box กลับเป็นขนาดต้นฉบับ
        detections = self.__rescale_boxes(detections, original_width, original_height)

        return detections
    
    def __rescale_boxes(self, detections, original_width, original_height):
        resized_width, resized_height = self.__model_imgsz
        scale_x = original_width / resized_width
        scale_y = original_height / resized_height

        for det in detections:
            x, y, w, h = det["box"]
            # ปรับสเกลของ x, y, w, h และจุดศูนย์กลาง
            det["box"] = [
                x * scale_x,
                y * scale_y,
                w * scale_x,
                h * scale_y
            ]
        return detections

    def drawbox(self,detections,image):
        for det in detections:
            x, y, w, h = det["box"]
            start_point = (int(x - w / 2), int(y - h / 2))
            end_point = (int(x + w / 2), int(y + h / 2))
            color = (255, 0, 255)
            thickness = 1
            image = cv2.rectangle(image, start_point, end_point, color, thickness)
            label = f"{det['class']} ({det['confidence']:.2f})"
            image = cv2.putText(image, label, start_point, cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, thickness)
        return image
        
    def __post_process(self, output, class_names, confidence_threshold):
        results = {}
        c = 0
        for detection in output[0].transpose((1, 0)):
            print(detection)
            c += 1
            scores = detection[4:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > confidence_threshold:
                x, y, w, h = detection[:4]
                class_name = class_names[class_id]
                # ถ้า class นี้ยังไม่มี หรือ confidence สูงกว่าเดิม ให้เก็บค่าใหม่
                if class_name not in results or results[class_name]["confidence"] < confidence:
                    results[class_name] = {
                        "confidence": confidence,
                        "box": [x, y, w, h]
                    }
        print(c)
        time.sleep(20)
        # แปลง dictionary เป็น list เพื่อคืนค่า
        final_results = [{"class": k, **v} for k, v in results.items()]
        return final_results