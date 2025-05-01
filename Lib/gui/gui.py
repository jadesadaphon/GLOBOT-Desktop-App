import customtkinter
from PIL import Image
import os
import re
import sys

customtkinter.set_appearance_mode("dark")

class GUI(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.width:int=1200
        self.height:int=600

        self.title("GLOBOT V1")

        if hasattr(sys, "_MEIPASS"):
            temp_icon_path = os.path.join(sys._MEIPASS, "Lib/gui/icons/icon.ico")
        else:
            temp_icon_path = "Lib/gui/icons/icon.ico"

        if not os.path.exists(temp_icon_path):
            raise FileNotFoundError(f"Icon file not found: {temp_icon_path}")

        self.iconbitmap(temp_icon_path)

        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)

        current_path = os.path.dirname(os.path.realpath(__file__))

        if hasattr(sys, "_MEIPASS"):
            images_path = os.path.join(sys._MEIPASS, 'images', 'untitled.png')
        else:
            images_path = os.path.join(current_path, 'images', 'untitled.png')

        bg_image = customtkinter.CTkImage(Image.open(images_path), size=(self.width, self.height))

        bg_image_label = customtkinter.CTkLabel(self, image=bg_image)
        bg_image_label.grid(row=0, column=0)
        
        self.__create_login_frame()
        self.__create_home_frame()
        self.__create_edit_frame()
        
    def __create_login_frame(self):
        # create login frame
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.login_frame.grid(row=0, column=0, sticky="ns", pady=(20,20))
        login_label = customtkinter.CTkLabel(self.login_frame, text="GLOBOT Login",font=customtkinter.CTkFont(size=20, weight="bold"))
        login_label.grid(row=0, column=0, padx=30, pady=(150, 15))
        self.email_login_entry = customtkinter.CTkEntry(self.login_frame, width=200, placeholder_text="Email")
        self.email_login_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
        self.password_login_entry = customtkinter.CTkEntry(self.login_frame, width=200, show="*", placeholder_text="Password")
        self.password_login_entry.grid(row=2, column=0, padx=30, pady=(0, 15))
        self.button_login = customtkinter.CTkButton(self.login_frame, text="Login", width=200)
        self.button_login.grid(row=3, column=0, padx=30, pady=(15, 15))  
        self.processor_name_label = customtkinter.CTkLabel(self.login_frame,font=customtkinter.CTkFont(size=12, weight="bold"))
        self.processor_name_label.grid(row=4, column=0, padx=30, pady=(150, 15))
        
    def __create_home_frame(self):
        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.home_frame.grid_rowconfigure(0, weight=1)
        self.home_frame.grid_columnconfigure(0, weight=0) 
        self.home_frame.grid_columnconfigure(1, weight=1) 
        # create info frame
        info_frame = customtkinter.CTkFrame(self.home_frame, corner_radius=10)
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") 
        info_frame.grid_rowconfigure(2, weight=1)
        main_label = customtkinter.CTkLabel(info_frame, text="GLOBOT", font=customtkinter.CTkFont(size=20, weight="bold"))
        main_label.grid(row=0, column=0, pady=(15, 5))
        self.clock_label = customtkinter.CTkLabel(info_frame, text="00:00:00.000", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.clock_label.grid(row=1, column=0, pady=(5, 15))
        # create profile frame
        profile_frame = customtkinter.CTkFrame(info_frame, corner_radius=10)
        profile_frame.grid(row=2, column=0, padx=15, pady=(15, 15), sticky="nsew") 
        profile_frame.grid_columnconfigure(0, weight=1)
        self.username_label = customtkinter.CTkLabel(profile_frame, text="Username", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.username_label.grid(row=0, column=0, pady=(15,5))
        self.credit_label = customtkinter.CTkLabel(profile_frame, text="Credit", font=customtkinter.CTkFont(size=11, weight="bold"))
        self.credit_label.grid(row=1, column=0, pady=(0,15))
        
        self.button_logout = customtkinter.CTkButton(info_frame, text="LogOut", width=150)
        self.button_logout.grid(row=3, column=0, padx=30, pady=(15, 15), sticky="s")
        # create list frame
        self.list_frame = customtkinter.CTkFrame(self.home_frame, corner_radius=10)
        self.list_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.list_frame.grid_rowconfigure(1, weight=1) 
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_title_frame = customtkinter.CTkFrame(self.list_frame, height=40, corner_radius=10)
        self.list_title_frame.grid(row=0, column=0, padx=5, pady=(10, 2), sticky="nsew")
        self.list_title_frame.grid_columnconfigure(0, weight=1)
        self.button_start_all = customtkinter.CTkButton(self.list_title_frame, text="START ALL", width=110)
        self.scrollable_list_frame = customtkinter.CTkScrollableFrame(self.list_frame, corner_radius=10)
        self.scrollable_list_frame.grid(row=1, column=0, padx=5, pady=(2, 5), sticky="nsew")
        
    # ###################### Edit from ###################### #
    def __validate_pin(self,input_text):
        return input_text == "" or (input_text.isdigit() and len(input_text) <= 6)
    
    def __validate_time_format(self, input_text):
        return input_text == "" or re.fullmatch(r"\d{0,2}(:\d{0,2})?(:\d{0,2}(\.\d{0,3})?)?", input_text) is not None
    
    def __on_time_entry_widget_change(self,event,entry_widget):
        try:
            value = entry_widget.get()
            if value != "":
                if len(value) == 2:
                    if not int(value[0:2]) <= 23:
                        entry_widget.delete(0,2)
                        entry_widget.insert(0,"2")
                        entry_widget.insert(1,"3")
                    entry_widget.insert(2,":")
                if len(value) == 5:
                    if not int(value[3:5]) <= 59:
                        entry_widget.delete(3,5)
                        entry_widget.insert(3,"5")
                        entry_widget.insert(4,"9")
                    entry_widget.insert(5,":")
                if len(value) == 8:
                    if not int(value[6:8]) <= 59:
                        entry_widget.delete(6,8)
                        entry_widget.insert(6,"5")
                        entry_widget.insert(7,"9")
                    entry_widget.insert(8,".")
        except Exception as e:
            entry_widget.delete(0,customtkinter.END)
            
    def __validate_digits(self,input_text):
        return input_text == "" or (len(input_text) == 1 and input_text in "012")
    
    def __create_edit_frame(self,serial=None,data=None):

        self.edit_frame = customtkinter.CTkFrame(self.list_frame, width=600, corner_radius=10)
        
        customtkinter.CTkLabel(self.edit_frame, text="EDITING", font=customtkinter.CTkFont(size=20, weight="bold")).pack(pady=(20,10))

        def new_frame(pady=(0,0)):
            frame = customtkinter.CTkFrame(self.edit_frame, fg_color="gray17")
            frame.pack(fill="both", expand=True, padx=(20,0), pady=pady)
            frame.grid_columnconfigure(0, weight=1)
            bg_color = frame.cget("bg_color")
            print(f"Background color: {bg_color}")
            return frame
        
        def new_label(text:str):
            customtkinter.CTkLabel(frame, text=text, font=customtkinter.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0,10), sticky="w")

        def pack_grid(widget):
            widget.grid(row=0, column=1, sticky="e", padx=(0,20)) 

        frame = new_frame((5,5)) 
        new_label("SERIAL")
        self.serial_entry = customtkinter.CTkEntry(frame, width=200, placeholder_text="Serial" if serial == None else serial)
        pack_grid(self.serial_entry)
        
        frame = new_frame((5,5))
        new_label("PIN")
        self.pin_entry = customtkinter.CTkEntry(
            frame, 
            width=200, 
            placeholder_text="password" if data == None else data["password"],
            textvariable=customtkinter.StringVar(),
            validate="key",
            validatecommand=(self.edit_frame.register(self.__validate_pin), "%P"))
        pack_grid(self.pin_entry)
        self.pin_entry.grid(row=0, column=1, sticky="e", padx=(0,20)) 

        frame = new_frame((5,5))
        new_label("PIN DELAY")
        self.pin_delay_entry = customtkinter.CTkEntry(
            frame, 
            width=200, 
            placeholder_text="pin delay" if data == None else data["password_delay"],
            textvariable=customtkinter.StringVar(),
            validate="key")
        pack_grid(self.pin_delay_entry)
        self.pin_delay_entry.grid(row=0, column=1, sticky="e", padx=(0,20)) 

        frame = new_frame((5,5))
        new_label("AM START")
        self.am_start_entry = customtkinter.CTkEntry(
            frame,
            width=200,
            placeholder_text="AM-Start" if data is None else data["am_start"],
            textvariable=customtkinter.StringVar(),
            validate="key",
            validatecommand=(self.edit_frame.register(self.__validate_time_format), "%P"))
        pack_grid(self.am_start_entry)
        self.am_start_entry.bind("<KeyRelease>", lambda event: self.__on_time_entry_widget_change(event, self.am_start_entry))
        
        frame = new_frame((5,5))
        new_label("AM BUY")
        self.am_buy_entry = customtkinter.CTkEntry(
            frame, 
            width=200, 
            placeholder_text="AM-Buy" if data == None else data["am_buy"],
            textvariable=customtkinter.StringVar(),
            validate="key",
            validatecommand=(self.edit_frame.register(self.__validate_time_format), "%P"))
        pack_grid(self.am_buy_entry)
        self.am_buy_entry.bind("<KeyRelease>", lambda event: self.__on_time_entry_widget_change(event, self.am_buy_entry))
        
        frame = new_frame((5,5))
        new_label("PM START")
        self.pm_start_entry = customtkinter.CTkEntry(
            frame, 
            width=200, 
            placeholder_text="PM-Start" if data == None else data["pm_start"],
            textvariable=customtkinter.StringVar(),
            validate="key",
            validatecommand=(self.edit_frame.register(self.__validate_time_format), "%P"))
        pack_grid(self.pm_start_entry)
        self.pm_start_entry.bind("<KeyRelease>", lambda event: self.__on_time_entry_widget_change(event, self.pm_start_entry))
        
        frame = new_frame((5,5))
        new_label("PM BUY")
        self.pm_buy_entry = customtkinter.CTkEntry(
            frame, 
            width=200, 
            placeholder_text="PM-Buy" if data == None else data["pm_buy"],
            textvariable=customtkinter.StringVar(),
            validate="key",
            validatecommand=(self.edit_frame.register(self.__validate_time_format), "%P"))
        pack_grid(self.pm_buy_entry)
        self.pm_buy_entry.bind("<KeyRelease>", lambda event: self.__on_time_entry_widget_change(event, self.pm_buy_entry))
        
        frame = new_frame((5,5))
        new_label("DIGITAL")
        self.digital_entry = customtkinter.CTkEntry(
            frame,
            width=200,
            placeholder_text="Amount" if data is None else data["amount"],
            textvariable=customtkinter.StringVar(),
            validate="key",
            validatecommand=(self.edit_frame.register(self.__validate_digits), "%P"))
        pack_grid(self.digital_entry)

        frame = new_frame((5,20))
        self.button_close_edit = customtkinter.CTkButton(frame, text="CLOSE")
        self.button_close_edit.grid(row=0, column=0, sticky="e", padx=(20,2.5)) 

        self.button_save_edit = customtkinter.CTkButton(frame, text="Save")
        self.button_save_edit.grid(row=0, column=1, sticky="w", padx=(2.5,20)) 
 
    def show_edit_frame(self,serial,data):
        self.serial_entry.configure(state="normal")
        self.serial_entry.configure(placeholder_text=serial)
        self.serial_entry.configure(state="disabled") 
        
        self.pin_entry.delete(0, customtkinter.END)
        self.pin_entry.insert(0,data["password"])

        self.pin_delay_entry.delete(0, customtkinter.END)
        self.pin_delay_entry.insert(0,data["password_delay"])
        
        self.am_start_entry.delete(0, customtkinter.END)
        self.am_start_entry.insert(0,data["am_start"])
        
        self.am_buy_entry.delete(0, customtkinter.END)
        self.am_buy_entry.insert(0,data["am_buy"])
        
        self.pm_start_entry.delete(0, customtkinter.END)
        self.pm_start_entry.insert(0,data["pm_start"])
        
        self.pm_buy_entry.delete(0, customtkinter.END)
        self.pm_buy_entry.insert(0,data["pm_buy"])
        
        self.digital_entry.delete(0, customtkinter.END)
        self.digital_entry.insert(0,data["amount"])
        
        self.edit_frame.grid(row=1, column=0, padx=5, pady=(10, 10))
        self.edit_frame.focus_set()

    def show_home_page(self):
        self.login_frame.grid_forget()
        self.home_frame.grid(row=0, column=0, sticky="nsew", padx=100)
        
    def hide_edit_frame(self):
        self.edit_frame.grid_forget()
        self.show_scrollable_list_frame()
        
    def show_scrollable_list_frame(self):
        self.list_title_frame.grid(row=0, column=0, padx=5, pady=(10, 2), sticky="nsew")
        self.list_title_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_list_frame.grid(row=1, column=0, padx=5, pady=(2, 5), sticky="nsew")
        
if __name__ == "__main__":      
    app = GUI()
    app.mainloop()