import threading
from Lib.ai import AI
from Lib.timeapi import TimeApi
import cv2
from adbutils import adb
import logging
import scrcpy
from pathlib import Path
import time
import re
from datetime import datetime
import os
import subprocess
import base64
from Lib.gui import GUI
from Lib.client import Client

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] ["GLoBot"] [%(name)s] %(levelname)s - %(message)s')

class gloBot(threading.Thread):
    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None):
        super().__init__(group, target, name, args, kwargs, daemon=True)
        self.running = threading.Event()
        self.process = threading.Event()
        self.shhell_open_paotang_initialized = threading.Event()
        self.scrcpy_initialized = threading.Event()
        self.hook_process_initialized = threading.Event()

        self.wait_pin_confirm = False
        
    def update_ui_show_button_stop(self):
        self.__widgets['button_edit'].configure(state="disabled")
        self.__widgets['button_start'].grid_forget()
        self.__widgets['button_stop'].grid(row=0, column=9, padx=(5, 5), pady=5)
        self.__widgets['button_stop'].configure(command=self.stop)

    def update_ui_show_button_start(self):
        self.__widgets['button_edit'].configure(state="normal")
        self.__widgets['button_stop'].grid_forget()
        self.__widgets['button_start'].grid(row=0, column=9, padx=(5, 5), pady=5)
        
    def start(self,model:str,device_serial:str,data:dict,widgets:GUI,timeapi:TimeApi,clientapi:Client,cv2show:bool=False):
        self.__ai = AI(model)
        self.__data = data
        self.__widgets:dict = widgets
        self.__cv2show = cv2show
        self.__time_api = timeapi
        self.__clientapi = clientapi
        self.__device = adb.device(device_serial)
        self.__logger:logging = logging.getLogger(f"{device_serial}")
        self.__start_time, self.__buy_time = self.__time_api.get_timestamp(data["am_start"],data["am_buy"],data["pm_start"],data["pm_buy"])
        return super().start()
    
    def run(self):

        self.update_ui_show_button_stop()
        
        self.running.set()
        
        self.__scrcpy_init()
        self.scrcpy_initialized.wait()

        while self.running.is_set():
            if self.__time_api.check_time(self.__start_time):
                break
            time.sleep(0.1)

        self.__disable_animation_with_su()
        
        # self.__open_paotang()
        
        while self.running.is_set():
            try:
                if not self.process.is_set():
                    detections = self.__ai.detections(self.__device_frame,0.7)
                    self.__ai.drawbox(detections, self.__device_frame)

                    if detections != []:
                        
                        self.process.set()
                        detected_classes = {detection['class'] for detection in detections}

                        if all(p in detected_classes for p in ["pin1","pin2","pin3","pin4","pin5","pin6","pin7","pin8","pin9","pin0","pindel"]):
                            delay = self.__data["password_delay"] if self.wait_pin_confirm else 0
                            self.__login(detections,self.__data["password"],delay=delay)
                            time.sleep(0.5) if self.wait_pin_confirm else time.sleep(1)
                                
                        if all(p in detected_classes for p in ["pthome"]):
                            self.__open_glo_page()
                            self.wait_pin_confirm = False
                            time.sleep(1)

                        if all(p in detected_classes for p in ["btnbuyseri"]):
                            if self.__time_api.check_time(self.__buy_time):
                                self.__touch(detections,"btnbuyseri")
                                self.wait_pin_confirm = False
                                time.sleep(0.5)

                        if all(p in detected_classes for p in ["btnbuydigital"]):
                            if self.__time_api.check_time(self.__buy_time):
                                self.__touch(detections,"btnbuydigital")
                                self.wait_pin_confirm = True
                                time.sleep(0.5)

                        if all(p in detected_classes for p in ["digitalitem1","digitalitem2","btnnext"]):
                            self.__digital_select_item(detections,int(self.__data["amount"])) 
                            self.wait_pin_confirm = False
                            time.sleep(0.1)

                        if all(p in detected_classes for p in ["btnslideconfirm"]):
                            self.__slide_confirm(detections)
                            self.wait_pin_confirm = True
                            time.sleep(0.1)

                        if all(p in detected_classes for p in ["btnslidecaptcha","captchajigsaw"]):
                            self.__slide_captcha_verify(detections)
                            self.wait_pin_confirm = False
                            time.sleep(0.1)

                        if all(p in detected_classes for p in ["receipt"]):
                            self.__save_receipt_image()
                            self.wait_pin_confirm = False
                            time.sleep(0.1)

                        if all(p in detected_classes for p in ["btnok"]):
                            self.__touch(detections,"btnok")
                            time.sleep(0.5)

                        if all(p in detected_classes for p in ["btncloseapp"]):
                            self.__touch(detections,"btncloseapp")
                            self.wait_pin_confirm = False
                            time.sleep(1)
                            self.__open_paotang()
                            
                    self.process.clear()
                    
            except Exception as e:
                self.__logger.warning(f"AI : wait scrcpy init.")
            
            time.sleep(0.1)
            
    def stop(self):
        self.running.clear()
        try:
            self.__client.stop()
        except Exception as e:
            self.__logger.warning(f"stop cv2 error : {e}")
        self.update_ui_show_button_start()
        self.__enable_animation_with_su()
        self.__logger.info(f"gloBot [{self.__device}] stop.")
        
    def __scrcpy_init(self):
        try:
            self.__client = scrcpy.Client(device=self.__device.serial)
            self.__client.max_width = 640
            self.__client.max_fps = 5
            self.__client.bitrate = 500000
            self.__client.add_listener(scrcpy.EVENT_FRAME, self.__on_frame)
            self.__client.start(Path("scrcpy-server.jar") ,threaded=True, daemon_threaded=True)
        except Exception as e:
            self.__logger.error(f"__scrcpy_init Error : {e}")

    def __on_frame(self, frame):
        if not self.running.is_set():
            try:
                cv2.destroyWindow(self.__device.serial)
            except cv2.error as e:
                self.__logger.warning(f"Error destroying window: {e}")

        if frame is not None:
            self.__device_frame = frame.copy()
            
        if self.__cv2show:
            try:
                cv2.imshow(self.__device.serial, self.__device_frame)
                cv2.waitKey(10)
            except Exception as e:
                pass
            
        if not self.scrcpy_initialized.is_set():
            self.scrcpy_initialized.set()

    def __touch_on_screen(self, name, x, y):
        try:
            self.__client.control.touch(x, y, scrcpy.ACTION_DOWN) 
            self.__client.control.touch(x, y, scrcpy.ACTION_UP)
            self.__logger.info(f"Touch {name} in x[{x}] y[{y}]")
        except Exception as e:
            pass
    
    def __touch_on_screen_test(self, name, x, y):
        try:
            self.__client.control.touch(x, y, scrcpy.ACTION_DOWN) 
            time.sleep(1)
            self.__client.control.touch(x, y, scrcpy.ACTION_UP)
            self.__logger.info(f"Touch {name} in x[{x}] y[{y}]")
        except Exception as e:
            pass

    def __login(self, detections, pin:str, delay=0):
        for digit in pin:  # วนลูปแต่ละตัวเลขใน pin
            for det in detections:  # วนลูปใน detections
                if det['class'] == f'pin{digit}':  # ตรวจสอบว่าตรงกับ pin
                    x, y, w, h = det["box"]
                    self.__touch_on_screen(f'pin{digit}', x, y)  # เรียกฟังก์ชัน touch
                    break  # หยุดลูป detections เมื่อเจอ class ที่ต้องการ
            time.sleep(delay)
        
    def __touch(self,detections,name):
        for det in detections:
            if det['class'] == name:  
                x, y, w, h = det["box"]
                self.__touch_on_screen(name, x, y)
                break 
    
    def __digital_select_item(self,detections,item:int):
        item_name = f'digitalitem{item}'
        for det in detections:
            if det['class'] == item_name:  
                x, y, w, h = det["box"]
                original_height, original_width = self.__device_frame.shape[:2]
                x = original_width / 2
                self.__touch_on_screen_test(item_name, x, y)
            time.sleep(1)
            if det['class'] == "btnnext":
                x, y, w, h = det["box"]
                self.__touch_on_screen_test("btnnext", x, y)

    def __slide_confirm(self,detections):
        steps = 8
        step_time = 0.000001 / steps
        original_height, original_width = self.__device_frame.shape[:2]
        endx = original_width - 8
        for det in detections:
            try:
                if det['class'] == "btnslideconfirm":
                    x, y, w, h = det["box"]
                    delta_x = (endx - x) / steps
                    self.__client.control.touch(x, y, scrcpy.ACTION_DOWN)
                    for step in range(1, steps + 1):
                        intermediate_x = int(x + step * delta_x)
                        self.__client.control.touch(intermediate_x, y, scrcpy.ACTION_MOVE)
                        time.sleep(step_time)
                    self.__client.control.touch(endx, y, scrcpy.ACTION_UP)
                    self.__logger.info(f"__slide_confirm...")
            except Exception as e:
                self.__logger.error(f"__slide_confirm : Exception {e}")

    def __slide_captcha_verify(self,detections):
        
        btnslidecaptcha = None
        captchajigsaw = None
        for det in detections:
            try:
                if det['class'] == "btnslidecaptcha":
                    btnslidecaptcha = det["box"]

                if det['class'] == "captchajigsaw":
                    captchajigsaw = det["box"]
                
                if btnslidecaptcha and captchajigsaw:
                    break
            except Exception as e:
                self.__logger.error(f"__slide_captcha_verify : Exception {e}")
        
        try:

            def calculate_b(x):
                return (x-(12+(0.86*x)))+x
        
            bx, by, bw, bh = btnslidecaptcha
            cx, cy, cw, ch = captchajigsaw

            start_x = bx
            end_x = cx
            y = by

            steps=5
            step_time = 0.000001 / steps
            delta_x = (end_x - start_x) / steps

            x = 0
            self.__client.control.touch(start_x, y, scrcpy.ACTION_DOWN)
            for step in range(1, steps + 1):
                intermediate_x = int(start_x + step * delta_x)
                x =  calculate_b(intermediate_x)
                self.__client.control.touch(x, y, scrcpy.ACTION_MOVE)
                time.sleep(step_time)
            self.__client.control.touch(x, y, scrcpy.ACTION_UP)
        except Exception as e:
            pass

    def __save_receipt_image(self):
        folder_name:str="slips"
        file_name:str=self.__device.serial+'-'+datetime.now().strftime('%Y-%m-%d-%H.%M.%S.%f')[:-3]+'.png'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_path:str=folder_name+'/'+file_name
        device_path = "/sdcard/screenshot.png"
        self.__device.shell(f"su -c 'screencap -p {device_path}'")
        subprocess.run(["adb", "-s", self.__device.serial, "pull", device_path, file_path])
        self.__device.shell(f"su -c 'rm {device_path}'")

        try:
            if os.path.exists(file_path):
                binary_fc = open(file_path, 'rb').read()
                base64_utf8_str = base64.b64encode(binary_fc).decode('utf-8')
                ext = file_path.split('.')[-1]
                dataurl = f'data:image/{ext};base64,{base64_utf8_str}'

                def loob_save(DATAURL):
                    while self.running.is_set():
                        result = self.__clientapi.save_history(DATAURL)
                        if result:
                            self.stop()
                            break
                        time.sleep(3)

                save = threading.Thread(target=lambda DATAURL=dataurl:loob_save(DATAURL), daemon=False)
                save.start()
                save.join()

        except Exception as e:
            self.__logger.error(f"__save_receipt_image : Exception {e}")

    def __open_glo_page(self):
        self.__device.shell("su -c 'am start -n com.ktb.customer.qr/.feature.gloflutter.ui.main.home.GloFlutterMainActivity'")

    def __open_paotang(self):
        self.__device.shell("su -c 'am start -n com.ktb.customer.qr/.feature.ekyc.ui.splashscreen.EkycSplashScreenActivity'")

    def __disable_animation_with_su(self):
        self.__device.shell("su -c 'settings put global window_animation_scale 0.01'")
        self.__device.shell("su -c 'settings put global transition_animation_scale 0.01'")
        self.__device.shell("su -c 'settings put global animator_duration_scale 0.01'")

    def __enable_animation_with_su(self):
        self.__device.shell("su -c 'settings put global window_animation_scale 1.0'")
        self.__device.shell("su -c 'settings put global transition_animation_scale 1.0'")
        self.__device.shell("su -c 'settings put global animator_duration_scale 1.0'")

    def __disable_pointer_location(self):
        self.__device.shell("su -c 'settings put system pointer_location 0'")

    def __enable_pointer_location(self):
        self.__device.shell("su -c 'settings put system pointer_location 1'")

    def __disable_magisk_notification(self):
        self.__device.shell("su -c 'settings put system pointer_location 1'")

    def __enable_magisk_notification(self):
        shell_uid = ""
        self.__device.shell(f"su -c 'magisk --sqlite UPDATE policies SET policy = 2, until = 0, logging = 0, notification = 0 WHERE uid = {shell_uid};'")


        



            
        

