@echo off
title Auto Commit e Push - Escrituracao Carne-Leao
echo ==============================================================
echo   Iniciando observador de alteracoes (Auto Commit e Push)
echo   Qualquer arquivo salvo sera commitado e enviado ao GitHub.
echo   Para pausar ou encerrar, feche esta janela ou aperte Ctrl+C.
echo ==============================================================
echo.

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0scripts\auto_commit_watcher.py"
) else (
    python "%~dp0scripts\auto_commit_watcher.py"
)

pause
