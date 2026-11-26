@echo off
rem Instalacja moda Wrzesien1939. Argumenty przekazuje do zainstaluj_mod.ps1, np. -NoActivate.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0zainstaluj_mod.ps1" %*
pause
