@echo off
IF NOT EXIST venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt

IF "%~1"=="" (
    start /b pythonw tool.py
) ELSE (
    start /b pythonw tool.py "%~1"
)
exit
