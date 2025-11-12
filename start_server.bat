@echo off
echo Starting FastAPI server...
echo.
echo Make sure you're in the project directory and have activated your virtual environment (if using one)
echo.
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
pause

