@echo off
setlocal
echo Dang huy cai dat tu dong khoi dong cho Discord English Tutor Bot...

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\DiscordEnglishTutorBot.lnk"

if exist "%SHORTCUT_PATH%" (
    del /f /q "%SHORTCUT_PATH%"
    echo.
    echo [THANH CONG] Da xoa shortcut tu dong khoi dong.
    echo Bot se khong con tu dong khoi dong cung Windows nua.
) else (
    echo.
    echo [THONG BAO] Khong tim thay shortcut autostart. Bot chua duoc cai dat tu dong khoi dong.
)
echo.
if not "%~1" == "--no-pause" pause
