@echo off
setlocal
echo Dang cai dat Discord English Tutor Bot tu dong khoi dong cung Windows...

set "SCRIPT_DIR=%~dp0"
set "VBS_PATH=%SCRIPT_DIR%run_hidden.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\DiscordEnglishTutorBot.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"%VBS_PATH%\"'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Description = 'Discord English Tutor Bot Autostart'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo.
    echo [THANH CONG] Da cai dat thanh cong!
    echo Shortcut da duoc tao tai: "%SHORTCUT_PATH%"
    echo Bot se tu dong khoi dong va chay ngam moi khi ban mo may / dang nhap Windows.
) else (
    echo.
    echo [LOI] Khong the tao shortcut tu dong khoi dong.
)
echo.
if not "%~1" == "--no-pause" pause
