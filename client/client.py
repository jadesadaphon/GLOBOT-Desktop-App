import threading
import requests
import logging
import base64
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(levelname)s - %(message)s')

class Client:
    def __init__(self):

        load_dotenv()

        self.__logger = logging.getLogger("Client")
        self.__api_key:str = os.getenv("SERVER_API_KEY")
        self.id_token:str = ""
        self.message = ""
        
        self.id:str=None

        self.host = f'http://{os.getenv("SERVER_HOST")}:{os.getenv("SERVER_PORT")}'

    def login(self, email: str, password: str) -> dict:
        payload = {"email": email, "password": password, "returnSecureToken": True}
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.__api_key}"
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.message  = "Login successful"
                self.__logger.info(self.message)
                return self.__verify_token(data['idToken'])
            else:
                error:dict = response.json()
                self.message  = f"Login failed: {error}"
                self.__logger.error(self.message)
                return
        except requests.exceptions.RequestException as e:
            self.message  = f"login Request failed: {e}"
            self.__logger.error(self.message)
            return
    
    def __verify_token(self,token:str) -> dict:
        try:
            url = f"{self.host}/verify"
            payload = {"idToken": token}
            response = requests.post(url, json=payload)
            if response:
                result:dict = response.json()
                if result['verify']:
                    self.id_token = token
                    self.message  = result['message']
                    self.__logger.info(self.message)
                    return result
                else:
                    self.message = result['message']
                    return
            else:
                self.message = response.json()
                return
        except requests.exceptions.RequestException as e:
            self.message =  f"Verify Token Request failed: {e}"
            self.__logger.error(self.message)
            return
        
    def save_history(self,img_base64:str) -> dict:
        try:
            url = f"{self.host}/history"
            payload = {"idToken": self.id_token, "img_base64": img_base64}
            response = requests.post(url, json=payload)
            if response:
                result:dict = response.json()
                return result['success']
            else:
                result:dict = response.json()
                return result['success']
        except requests.exceptions.RequestException as e:
            self.__logger.error(self.message)
            return
