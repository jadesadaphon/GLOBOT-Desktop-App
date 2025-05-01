@echo off
:: ตั้งชื่อ Virtual Environment
set VENV_NAME=.venv

:: ตรวจสอบว่ามี Python ติดตั้งอยู่หรือไม่
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

:: สร้าง Virtual Environment
echo Creating Virtual Environment...
python -m venv %VENV_NAME%

:: ตรวจสอบว่า Virtual Environment ถูกสร้างสำเร็จ
if not exist "%VENV_NAME%\Scripts\activate" (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b
)

:: เปิดใช้งาน Virtual Environment
echo Activating Virtual Environment...
call "%VENV_NAME%\Scripts\activate"

:: อัปเกรด pip, setuptools, และ wheel
echo Upgrading pip, setuptools, and wheel...
pip install --upgrade pip setuptools wheel

:: ติดตั้ง dependencies จาก requirements.txt
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found. Skipping dependency installation.
)

:: แสดงรายการไลบรารีที่ติดตั้ง
pip list

:: ออกจาก Virtual Environment
deactivate
echo Virtual Environment setup complete.

pause
