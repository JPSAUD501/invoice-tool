@echo off
git pull

echo Verificando se o Python esta instalado...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python nao encontrado. Instalando via winget...
    winget install --id Python.Python.3.11 -e --source winget
    if %errorlevel% neq 0 (
        echo Erro ao instalar o Python. Por favor, instale manualmente.
        pause
        exit /b 1
    )
    echo Python instalado com sucesso!
    echo Reiniciando o script para usar o Python...
    start "" "%~f0" %*
    exit /b 0
)

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
