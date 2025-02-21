@echo off
echo Installing dependencies for TikTok Views Automator...
echo -----------------------------------------------------

:: Verifica se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python and try again.
    pause
    exit /b 1
)

:: Instala as dependências do requirements.txt
pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies. Check the requirements.txt file.
        pause
        exit /b 1
    )
) else (
    echo requirements.txt file not found. Please ensure it exists in the same directory.
    pause
    exit /b 1
)

echo -----------------------------------------------------
echo Dependencies installed successfully!
pause
exit /b 0