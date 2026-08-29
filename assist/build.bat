@echo off
echo ============================================
echo  D-Flipflop Frequenzteiler - Build
echo ============================================
echo.

echo Erstelle .exe...
echo.

py -m PyInstaller --onefile --windowed ^
    --name "DFF-Frequenzteiler" ^
    main.py

echo.
if exist "dist\DFF-Frequenzteiler.exe" (
    echo ============================================
    echo  Build erfolgreich!
    echo  Die .exe liegt unter: dist\DFF-Frequenzteiler.exe
    echo ============================================
) else (
    echo Build fehlgeschlagen. Siehe Fehlermeldungen oben.
)

pause
