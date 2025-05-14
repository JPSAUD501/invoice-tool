@echo off
REM Check if application is already installed in this location
IF EXIST "%~dp0run.bat" (
    echo Sistema ja instalado, iniciando...
    call "%~dp0run.bat" %*
    exit /b
)

echo Verificando se o Git esta instalado...
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Git nao encontrado. Instalando via winget...
    winget install --id Git.Git -e --source winget
    if %errorlevel% neq 0 (
        echo Erro ao instalar o Git. Por favor, instale manualmente.
        pause
        exit /b 1
    )
    echo Git instalado com sucesso!
    echo Reiniciando o script para usar o Git...
    start "" "%~f0"
    exit /b 0
)

echo Git encontrado. Clonando o repositorio...
set "CURRENT_DIR=%~dp0"
cd /d "%CURRENT_DIR%"
git clone https://github.com/JPSAUD501/invoice-tool
if %errorlevel% neq 0 (
    echo Erro ao clonar o repositorio.
    pause
    exit /b 1
)

echo Repositorio clonado com sucesso!
echo Iniciando o aplicativo...

REM Launch the APP.bat from the new directory and pass any arguments
cd invoice-tool
start "" "%~dp0invoice-tool\APP.bat" %*

echo Removendo APP.bat original...
(goto) 2>nul & del "%~f0"
