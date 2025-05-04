import requests
from threading import Thread, Event
from time import sleep, time
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(levelname)s - %(message)s')

class ClientApi(Thread):

    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None):
        super().__init__(group, target, "ClientApi-Thread", args, kwargs, daemon=True)
        self.__logger:logging = logging.getLogger(f"ClientApiThread")
        self.__client_api_running = Event()
        self.online:Event = Event()
        self.__server_time_offset = 0.0
        self.__server_epoch_time = 0.0
        self.__time_offset = 0.0

    def get_timeApi_offset(self):
        return self.__time_offset
    
    def stop_client_api(self):
        self.online.clear()
        self.__client_api_running.clear()
        
    def __update_offset(self):
        server_time = self.__server_time_offset + self.__server_epoch_time
        local_time = time()
        self.__time_offset = server_time - local_time
        
    def run(self):
        self.__client_api_running.set()
        self.__logger.info('Service time api is running.')
        while self.__client_api_running.is_set():
            try:
                url = 'http://www.time.navy.mi.th/'
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    script_tags = soup.find_all('script')
                    for script in script_tags:
                        if 'var clockServerStartTime' in script.string:
                            time_line = script.string.splitlines()
                            for line in time_line:
                                if 'var time=' in line:
                                    time_value = line.split('=')[1].split(';')[0].strip()
                                    parts = time_value.split('+')
                                    self.__server_time_offset = float(parts[0].strip())
                                    self.__server_epoch_time = float(parts[1].strip())
                                    self.__logger.info(f'Server update [time offset : {self.__server_time_offset}] [epoch time : {self.__server_epoch_time}]')
                                    self.__update_offset()
                                    self.online.set()
                                    break           
                else:
                    self.__logger.error('Error fetching server time')
            except Exception as e:
                self.__logger.error(f'Error in update_server_time: {e}')
            count_seconds = 60
            while self.__client_api_running.is_set():
                count_seconds -= 1
                sleep(1)
        self.__logger.info('Service time api has stopped running.')

if __name__ == "__main__":
    client_api = ClientApi()
    client_api.start()