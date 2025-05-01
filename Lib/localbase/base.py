import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(levelname)s - %(message)s')

class SqliteDB():
    def __init__(self, device: str) -> None:
        
        self.__logger:logging = logging.getLogger(f"SqliteDB")
        self.device = device
        db_name = device
        basesqlite_folder = "basesqlite"

        if not os.path.exists(basesqlite_folder):
            os.makedirs(basesqlite_folder)
        
        db_file = f"{basesqlite_folder}/{db_name}.db"

        self.__connect_db(db_file)

        if not os.path.isfile(db_file):
            self.__create_db()
        else:
            self.__check_and_create_info_tables()

    def __connect_db(self, db_file: str):
        """เชื่อมต่อกับฐานข้อมูล SQLite"""
        try:
            conn = sqlite3.connect(db_file, check_same_thread=False)
            cursor = conn.cursor()
            conn.row_factory = sqlite3.Row
            self.__conn = conn
            self.__cursor = cursor
        except sqlite3.Error as e:
            print(f"Database connection failed: {e} db: {db_file}")
            raise
    
    def __check_and_create_info_tables(self):
        """ตรวจสอบว่ามีตาราง 'info' หรือไม่ และสร้างขึ้นหากไม่มี"""
        self.__cursor.execute('''SELECT name FROM sqlite_master WHERE type="table" AND name="info";''')
        if not self.__cursor.fetchone():
            script = self.__create_info_table_script()
            self.__cursor.execute(script)
            self.__conn.commit()
            self.insert_info()

    def __create_info_table_script(self):
        """สคริปต์ SQL เพื่อสร้างตาราง info"""
        return ''' 
            CREATE TABLE IF NOT EXISTS info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password TEXT NOT NULL UNIQUE,
                password_delay FLOAT UNIQUE,
                am_start TEXT UNIQUE,
                am_buy TEXT UNIQUE,
                amount INT UNIQUE,
                pm_start TEXT UNIQUE,
                pm_buy TEXT UNIQUE
            )
        '''
    
    def insert_info(self,
                    password: str = "588888",
                    password_delay: float = 0.25,
                    am_start: str = "07:25:00.000",
                    am_buy: str = "07:30:00.000",
                    amount: int = 2,
                    pm_start: str = "14:55:00.000",
                    pm_buy: str = "15:00:00.000"):
        
        """เพิ่ม ข้อมูล ลงในตาราง info"""
        try:
            query = '''INSERT INTO info (password, password_delay, am_start, am_buy, amount, pm_start, pm_buy) VALUES (?, ?, ?, ?, ?, ?, ?)'''
            self.__cursor.execute(query, (password, password_delay, am_start, am_buy, amount, pm_start, pm_buy))
            self.__conn.commit()
            self.__logger.info(f"{self.device} INSERT [password:{password}] [password_delay:{password_delay}] [am_start:{am_start}] [am_buy:{am_buy}] [amount:{amount}] [pm_start:{pm_start}] [pm_buy:{pm_buy}]")
            return True
        except sqlite3.Error as e:
            print(f"Error adding info: {e}")
            return False
        
    def update_info(self,
                    password: str = "588888",
                    password_delay: float = 0.25,
                    am_start: str = "07:25:00.000",
                    am_buy: str = "07:30:00.000",
                    amount: int = 0,
                    pm_start: str = "14:55:00.000",
                    pm_buy: str = "15:00:00.000"):
        """อัปเดตข้อมูลในตาราง info"""
        try:
            id = 1
            query = '''UPDATE info 
                    SET password = ?,
                        password_delay = ?,
                        am_start = ?, 
                        am_buy = ?, 
                        amount = ?, 
                        pm_start = ?, 
                        pm_buy = ? 
                    WHERE id = ?'''
            self.__cursor.execute(query, (password, password_delay, am_start, am_buy, amount, pm_start, pm_buy, id))
            self.__conn.commit()
            self.__logger.info(f"{self.device} UPDATE [password:{password}] [password_delay:{password_delay}] [am_start:{am_start}] [am_buy:{am_buy}] [amount:{amount}] [pm_start:{pm_start}] [pm_buy:{pm_buy}]")
            return True
        except sqlite3.Error as e:
            print(f"Error updating info: {e}")
            return False


    def info(self):
        """รับ info ทั้งหมดเป็น python dictionary """
        self.__cursor.execute("SELECT * FROM info")
        rows = self.__cursor.fetchall()
        column_names = [description[0] for description in self.__cursor.description]
        result = []
        for row in rows:
            row_dict = dict(zip(column_names, row))  
            result.append(row_dict)
        return result

    def disconnect(self):
        """ปิดการเชื่อมต่อฐานข้อมูล"""
        if self.__conn:
            self.__conn.close()
    
    def __del__(self):
        """ ตรวจสอบให้แน่ใจว่าการเชื่อมต่อฐานข้อมูลถูกปิดเมื่อวัตถุถูกทำลาย """
        self.disconnect()


if __name__ == "__main__":
    sqliteDB = SqliteDB("R7AX80EYK0L")