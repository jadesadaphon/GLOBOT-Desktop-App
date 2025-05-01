from Lib.ai import AI
from Lib.globot import gloBot
from Lib.timeapi import TimeApi
from Lib.client import Client
from Lib.gui import GUI
from Lib.localbase import SqliteDB
from tkinter import messagebox
from adbutils import adb
import customtkinter
import threading
import cv2
import sys
import os
import time
import logging

# pyinstaller --onefile --noconsole --add-data "best9.onnx;." --add-data "Lib/gui/images/untitled.png;images" --add-data "Lib/gui/icons/icon.ico;Lib/gui/icons" --icon="Lib\gui\icons\icon.ico" main.py

# pyinstaller --onefile --add-data "best9.onnx;." --add-data "Lib/gui/images/untitled.png;images" --add-data "Lib/gui/icons/icon.ico;Lib/gui/icons" --icon="Lib\gui\icons\icon.ico" main.py

logger: logging = logging.getLogger(f"Main")

def set_command_button_login():
    global gui, client
    def client_login(email: str, password: str):
        try:
            result = client.login(email, password)
            message = client.message
        except Exception as e:
            messagebox.showerror("Login Error", f"An error occurred: {e}")
            gui.after(0, lambda: gui.button_login.configure(state="normal"))
            return
        
        def update_ui():  
            if result:
                print(result)
                adb_hook_devices(gui)
                client.id = result['id']
                credit = client.credit = result['credit']
                username = client.credit = result['name']
                gui.username_label.configure(text=username)
                gui.credit_label.configure(text=f'Your have {credit} CR.')
                gui.show_home_page()
            else:
                messagebox.showerror("Login Failed", message)
                
            gui.button_login.configure(state="normal")
        
        gui.after(0, update_ui)
    
    def handle_login():
        gui.button_login.configure(state="disabled")
        email = gui.email_login_entry.get()
        password = gui.password_login_entry.get()
        threading.Thread(target=lambda: client_login(email, password), daemon=True).start()
    
    gui.button_login.configure(command=handle_login)

def set_command_button_logout():
    global gui
    def handle_logout():
        gui.home_frame.grid_forget()
        gui.login_frame.grid(row=0, column=0, sticky="ns", pady=(20,20))
    
    gui.button_logout.configure(command=handle_logout)

def set_command_button_edit(serial,data):
    global gui
    gui.list_title_frame.grid_forget()
    gui.scrollable_list_frame.grid_forget()
    
    gui.button_close_edit.configure(command=set_command_button_close_edit)
    gui.button_save_edit.configure(command=lambda SERIAL=serial: set_command_button_save_edit(SERIAL))
    
    gui.show_edit_frame(serial,data)
    
def set_command_button_start(serial, data, widgets):
    global timeapi, model_path, botrunning, client
    botrunning.clear()
    bot = gloBot()
    bot.start(model=model_path,device_serial=serial,data=data,widgets=widgets,timeapi=timeapi,clientapi=client,cv2show=True)
    botrunning.append(bot)
    
def set_command_button_start_all():
    global gui, devices_data, timeapi, model_path, botrunning, client
    botrunning.clear()
    for device_data in devices_data:
        
        serial = device_data['Serial']
        data = device_data['Info']
        widgets = device_data['widgets']
        bot = gloBot()
        bot.start(model=model_path,device_serial=serial,data=data,widgets=widgets,timeapi=timeapi,clientapi=client,cv2show=False)
        botrunning.append(bot)

    gui.button_start_all.configure(text="STOP ALL", fg_color="red", command=set_command_button_stop_all)

def set_command_button_stop_all():
    global botrunning
    for bot in botrunning:
        bot.stop()
    gui.button_start_all.configure(text="START ALL", fg_color="#1F6AA5", command=set_command_button_start_all)

def set_command_button_close_edit():
    global gui
    gui.hide_edit_frame()

def set_command_button_save_edit(serial:str):
    
    global gui
    
    def set_default_border_color():
        default_border_color = customtkinter.ThemeManager.theme["CTkEntry"]["border_color"]
        gui.pin_entry.configure(border_color=default_border_color[1])
        gui.pin_delay_entry.configure(border_color=default_border_color[1])
        gui.am_start_entry.configure(border_color=default_border_color[1])
        gui.am_buy_entry.configure(border_color=default_border_color[1])
        gui.pm_start_entry.configure(border_color=default_border_color[1])
        gui.pm_buy_entry.configure(border_color=default_border_color[1])
        gui.digital_entry.configure(border_color=default_border_color[1])

    set_default_border_color()

    gui.button_save_edit.configure(state="disabled")
    def validate():
        if not len(gui.pin_entry.get()) == 6:
            gui.pin_entry.configure(border_color="red")
            return False
        if not len(gui.am_start_entry.get()) == 12:
            gui.am_start_entry.configure(border_color="red")
            return False
        if not len(gui.am_buy_entry.get()) == 12:
            gui.am_buy_entry.configure(border_color="red")
            return False
        if not len(gui.pm_start_entry.get()) == 12:
            gui.pm_start_entry.configure(border_color="red")
            return False
        if not len(gui.pm_buy_entry.get()) == 12:
            gui.pm_buy_entry.configure(border_color="red")
            return False
        if not len(gui.digital_entry.get()) == 1:
            gui.digital_entry.configure(border_color="red")
            return False
        set_default_border_color()
        return True
    
    validate = validate()
    if validate:
        update = {
            "password": gui.pin_entry.get(),
            "password_delay": gui.pin_delay_entry.get(),
            "am_start": gui.am_start_entry.get(),
            "am_buy": gui.am_buy_entry.get(),
            "pm_start": gui.pm_start_entry.get(),
            "pm_buy": gui.pm_buy_entry.get(),
            "amount": gui.digital_entry.get()
        }
        def save_task():
            db = SqliteDB(serial)
            db.update_info(update["password"],update["password_delay"],update["am_start"],update["am_buy"],update["amount"],update["pm_start"],update["pm_buy"])
            db.disconnect()
        db_job = threading.Thread(target=save_task, daemon=True)
        db_job.start()
        db_job.join()
        
        update_devices_data()
        gui.hide_edit_frame()
        gui.show_scrollable_list_frame()
            
    gui.button_save_edit.configure(state="normal")

def gui_update_list_devices_scrollable_frame(devices:list):
    
    global previous_devices, online_devices
    
    if devices != previous_devices:
        
        added = list(set(devices) - set(previous_devices))
        removed = list(set(previous_devices) - set(devices))
        
        if added:
            logger.info(f"Devices {added} connect")
        if removed:
            logger.info(f"Devices {removed} disconnect")
            
        online_devices = devices.copy()
        
        update_devices_data()
        
def update_devices_data():
    global devices_data, online_devices
    
    devices_data.clear()
    
    for device in online_devices:
        
        sqliteDB = SqliteDB(device)
        device_dict = {"Serial": device, "Info": sqliteDB.info()}
        sqliteDB.disconnect()
        
        devices_data.append(device_dict)
        
    update_ui_list_devices()
    
def update_ui_list_devices():
    try:
        global gui, devices_data
        
        def clear_scrollable_list_frame():
            for widget in gui.scrollable_list_frame.winfo_children():
                widget.destroy()
            gui.scrollable_list_frame.update_idletasks()

        clear_scrollable_list_frame()

        # if devices_data == []:
        #     gui.button_start_all.grid_forget()
        # else:
        #     gui.button_start_all.configure(command=set_command_button_start_all)
        #     gui.button_start_all.grid(row=0, column=1, padx=(5, 25), pady=5)
        
        # Add rows in scrollable list frame
        for i, device in enumerate(devices_data):
            serial = device["Serial"] 
            data = device["Info"][0] 
            row_frame = customtkinter.CTkFrame(gui.scrollable_list_frame, height=40, corner_radius=10, fg_color="#2f2f2f")
            row_frame.pack(fill="x", expand=True, pady=(10 if i == 0 else 2, 2), padx=5)
            row_frame.grid_columnconfigure(0, weight=1)
            serial_label = customtkinter.CTkLabel(row_frame, text=serial, font=customtkinter.CTkFont(size=12))
            serial_label.grid(row=0, column=0, padx=(10, 5), sticky="w")

            pin_label = customtkinter.CTkLabel(row_frame, text=data["password"], font=customtkinter.CTkFont(size=12))
            pin_label.grid(row=0, column=1, padx=(5, 5))

            pin_label = customtkinter.CTkLabel(row_frame, text=data["password_delay"], font=customtkinter.CTkFont(size=12))
            pin_label.grid(row=0, column=2, padx=(5, 5))

            am_start_label = customtkinter.CTkLabel(row_frame, text=data["am_start"], font=customtkinter.CTkFont(size=12))
            am_start_label.grid(row=0, column=3, padx=(5, 5))
            am_buy_label = customtkinter.CTkLabel(row_frame, text=data["am_buy"], font=customtkinter.CTkFont(size=12))
            am_buy_label.grid(row=0, column=4, padx=(5, 5))
            pm_start_label = customtkinter.CTkLabel(row_frame, text=data["pm_start"], font=customtkinter.CTkFont(size=12))
            pm_start_label.grid(row=0, column=5, padx=(5, 5))
            pm_buy_label = customtkinter.CTkLabel(row_frame, text=data["pm_buy"], font=customtkinter.CTkFont(size=12))
            pm_buy_label.grid(row=0, column=6, padx=(5, 5))
            digital_label = customtkinter.CTkLabel(row_frame, text=data["amount"], font=customtkinter.CTkFont(size=12))
            digital_label.grid(row=0, column=7, padx=(5, 5))
            button_edit = customtkinter.CTkButton(row_frame, text="EDIT", width=50, font=customtkinter.CTkFont(weight="bold"))
            button_edit.configure(command=lambda SERIAL=serial, DATA=data: set_command_button_edit(SERIAL, DATA))
            button_edit.grid(row=0, column=8, padx=(5, 5), pady=5)
            button_stop = customtkinter.CTkButton(row_frame, text="STOP", fg_color="red", width=50,  font=customtkinter.CTkFont(weight="bold"))
            button_stop.grid(row=0, column=9, padx=(5, 5), pady=5)
            button_stop.grid_forget()
            button_start = customtkinter.CTkButton(row_frame, text="START", width=50, font=customtkinter.CTkFont(weight="bold"))
            widgets={"button_edit":button_edit,"button_start":button_start,"button_stop":button_stop,"button_start_all":gui.button_start_all}
            button_start.configure(command=lambda SERIAL=serial, DATA=data, WIDGETS=widgets: set_command_button_start(SERIAL, DATA, WIDGETS))
            button_start.grid(row=0, column=10, padx=(5, 5), pady=5)

            devices_data[i]['widgets'] = widgets
        
    except Exception as e:
        print(f"Error in update_ui_list_devices: {e}")
        time.sleep(1)

def set_gui_processor_name():
    ['CUDAExecutionProvider', 'CPUExecutionProvider']
    global gui, ai
    processor_name:list = ai.processor_name
    if len(processor_name) == 1:
        gui.processor_name_label.configure(text="CPU only")
    else:
        gui.processor_name_label.configure(text="CUDA and CPU")
   
def adb_hook_devices(gui:GUI):
    global running
    running.set()
    
    def live():
        def update_devices(devices):
            gui_update_list_devices_scrollable_frame(devices)

        while running.is_set():
            
            global previous_devices
            
            try:
                device_list = adb.device_list()
                devices = [device.serial for device in device_list]
                
                if devices != previous_devices:
                    update_devices(devices)
                    
                previous_devices = devices.copy()
                
            except Exception as e:
                print(f"Error in live device thread: {e}")
            time.sleep(1)
                
    threading.Thread(target=live, daemon=True).start()


if __name__ == "__main__":
    running=threading.Event()

    botrunning:list=[]
    previous_devices:list=[]
    online_devices:list=[]
    devices_data:list=[]
    
    model_path = "best9.onnx"
    if hasattr(sys, "_MEIPASS"):
        model_path = os.path.join(sys._MEIPASS, model_path)
    ai:AI=AI(model_path=model_path)
    gui:GUI=GUI()
    
    timeapi:TimeApi=TimeApi()
    timeapi.start(gui.clock_label)

    set_gui_processor_name()
    
    client:Client=Client()
    set_command_button_login()
    set_command_button_logout()
    
    gui.email_login_entry.insert(0, "jadesadaphon.chaykaew@gmail.com")
    gui.password_login_entry.insert(0, "admin@1234")

    gui.mainloop()
    
    running.clear()

    






