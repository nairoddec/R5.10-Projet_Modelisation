@echo off
REM Script de lancement universel pour Windows
python src/main.py %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Une erreur est survenue lors de l'execution.
    pause
)
