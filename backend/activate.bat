@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Environment activated!
echo.
echo To install dependencies, run: pip install -r requirements.txt
echo To start the development server, run: uvicorn app.main:app --reload
