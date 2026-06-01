@echo off
echo Setting up Anwaar Galaxy Glow...

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
pip install -r requirements.txt

REM Run migrations
python manage.py makemigrations
python manage.py migrate

REM Create superuser
echo Creating superuser...
python manage.py createsuperuser

REM Seed data
python manage.py seed_data

echo Setup complete!
echo.
echo To run the server:
echo venv\Scripts\activate
echo python manage.py runserver
pause