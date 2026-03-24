@echo off
title YOVO Setup
color 0A
echo.
echo  =============================================
echo    YOVO - Your Old, Valued Once More
echo    Automatic Setup Script
echo  =============================================
echo.

echo [1/6] Setting up virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo      Created new virtual environment.
) else (
    echo      Virtual environment already exists.
)

echo.
echo [2/6] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [3/6] Installing packages...
pip install -r requirements.txt --quiet

echo.
echo [4/6] Deleting old database (fresh start)...
if exist "db.sqlite3" (
    del db.sqlite3
    echo      Old database deleted.
) else (
    echo      No old database found.
)

echo.
echo [5/6] Creating database tables...
python manage.py migrate --run-syncdb

echo.
echo [6/6] Creating admin account...
echo.
echo  Please create your admin login below:
echo  (This is what you use to access /admin)
echo.
python manage.py createsuperuser

echo.
echo  =============================================
echo    SETUP COMPLETE! Starting server...
echo.
echo    Website:  http://127.0.0.1:8000
echo    Admin:    http://127.0.0.1:8000/admin
echo  =============================================
echo.
python manage.py runserver
pause
