@echo off
setlocal

REM Clean Cursor profile directory (isolated from regular profile)
set "CURSOR_CLEAN_PROFILE=%TEMP%\cursor-clean-profile"
if not exist "%CURSOR_CLEAN_PROFILE%" mkdir "%CURSOR_CLEAN_PROFILE%"

REM Prefer CLI if available
where cursor >nul 2>nul
if %ERRORLEVEL%==0 (
    start "" cursor --disable-extensions --user-data-dir "%CURSOR_CLEAN_PROFILE%" %*
    exit /b 0
)

REM Fallback to default installation path
set "CURSOR_EXE=%LocalAppData%\Programs\cursor\Cursor.exe"
if exist "%CURSOR_EXE%" (
    start "" "%CURSOR_EXE%" --disable-extensions --user-data-dir "%CURSOR_CLEAN_PROFILE%" %*
    exit /b 0
)

echo Cursor executable not found.
echo Install Cursor or add "cursor" to PATH.
exit /b 1
