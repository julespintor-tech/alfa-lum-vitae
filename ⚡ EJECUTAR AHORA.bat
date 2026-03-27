@echo off
echo.
echo  ============================================
echo    ALFA LUM-vitae -- Ejecutando run manual
echo  ============================================
echo.
cd /d "%~dp0"
python lum_vitae_runner.py
echo.
echo  Listo. Abre lum_vitae_dashboard.html para ver los resultados.
echo.
pause
