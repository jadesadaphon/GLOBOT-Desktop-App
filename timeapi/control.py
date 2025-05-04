from threading import Thread, Event
from .clientapi import ClientApi
from time import sleep, time 
from datetime import datetime 
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(levelname)s - %(message)s')

class Control(Thread):

    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None):
        super().__init__(group, target, "TimeControl-Thread", args, kwargs, daemon=True)
        self.__logger:logging = logging.getLogger(f"TimeControl")
        self.online = Event()
        self.__clock_running = Event()
        self.__server_timestamp = float(0.0)
        self.start_timestamp = None
        self.buy_timestamp = None
        
    def start(self,clockUi=None):
        self.clock_ui = clockUi
        return super().start()

    def run(self):
        self.__client_api = ClientApi()
        self.__client_api.start()
        self.__client_api.online.wait()
        self.__update_clock()
        
    def stop_time_api(self):
        self.online.clear()
        self.__clock_running.clear()
        self.__client_api.stop_client_api()
        self.__client_api.join()

    def __update_clock(self):
        self.__logger.info('Service clock is running.')
        self.__clock_running.set()
        while self.__client_api.online.is_set():
            try:
                local_time = time()
                self.__server_timestamp = local_time + (self.__client_api.get_timeApi_offset() or 0)
                clock_date_object = datetime.fromtimestamp(self.__server_timestamp)
                clock = clock_date_object.strftime('%H:%M:%S.') + clock_date_object.strftime('%f')[:3]
                
                if self.clock_ui != None:
                    try:
                        self.clock_ui.configure(text=clock)
                    except:
                        pass
                
                if not self.online.is_set():
                    self.online.set()
                    
                sleep(0.01)
                # self.__logger.info(f'Time : {clock}')
            except Exception as e:
                self.__logger.error(f"Error in update_clock: {e}")
                sleep(0.01)
        self.__logger.info('Service clock has stopped running.')
     
    def __time_to_timestamp(self,am_start,am_buy,pm_start,pm_buy):
        current_timestamp = datetime.now().timestamp()
        date_object = datetime.fromtimestamp(current_timestamp)
        string_year_month_day = date_object.strftime('%Y-%m-%d')
        if self.__check_time() == 0:
            string_target_date_program = f"{string_year_month_day} {am_start}"
            string_target_date_lotto = f"{string_year_month_day} {am_buy}"
        else:
            string_target_date_program = f"{string_year_month_day} {pm_start}"
            string_target_date_lotto = f"{string_year_month_day} {pm_buy}"
        target_date_object_program = datetime.strptime(string_target_date_program, '%Y-%m-%d %H:%M:%S.%f')
        target_date_object_lotto = datetime.strptime(string_target_date_lotto, '%Y-%m-%d %H:%M:%S.%f')
        target_date_unix_timestamp_program = target_date_object_program.timestamp()
        target_date_unix_timestamp_lotto = target_date_object_lotto.timestamp()
        return target_date_unix_timestamp_program,target_date_unix_timestamp_lotto

    def __check_time(self):
        server_date_object = datetime.fromtimestamp(self.__server_timestamp)
        server_year_month_day = server_date_object.strftime('%Y-%m-%d')
        server_target_date = f"{server_year_month_day} 12:00:00"
        server_target_date_object = datetime.strptime(server_target_date, '%Y-%m-%d %H:%M:%S')
        if self.__server_timestamp >= server_target_date_object.timestamp():
            return 1
        else:
            return 0
        
    def get_timestamp(self, am_start: str = "07:25:00.000", am_buy: str = "07:30:00.000", pm_start: str = "14:55:00.000", pm_buy: str = "15:00:00.000"):
        def format_time(time_str):
            try:
                h, m, rest = time_str.split(':')
                s, ms = rest.split('.')
                return f"{int(h):02}:{int(m):02}:{int(s):02}.{int(ms):03}"
            except ValueError as e:
                raise ValueError(f"Invalid time format: {time_str}. Expected format 'H.M.S.MS'. Error: {e}")
        try:
            if self.start_timestamp == None or self.buy_timestamp == None:
                self.start_timestamp, self.buy_timestamp = self.__time_to_timestamp(format_time(am_start),format_time(am_buy),format_time(pm_start),format_time(pm_buy))
            return self.start_timestamp, self.buy_timestamp
        except Exception as e:
            self.__logger.error(f"get_timestamp : {e}")
            return None, None
        
    def check_time(self,mTime):
        if mTime <= self.__server_timestamp:
            return True
        return False
        
 
if __name__ == "__main__":
    time_manage = Control()
    time_manage.start()