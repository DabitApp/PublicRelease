@echo off
setlocal enabledelayedexpansion

:: Prompt for the path to the target
set /p "TARGET_PATH=Enter the path to the target (e.g., [C:\ProgramData\Anaconda3\]): "
set "CONDA_PATH=%TARGET_PATH%\condabin\conda.bat"
set "PYTHON_PATH=%TARGET_PATH%\python.exe"
set "SHORTCUT_NAME=Python Anaconda Prompt"

:: Create the shortcut using PowerShell (single line)
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%cd%\Build.lnk'); $Shortcut.TargetPath = '%windir%\System32\cmd.exe'; $Shortcut.Arguments = '/K %CONDA_PATH% run %PYTHON_PATH% scripts\build.py' ; $Shortcut.WorkingDirectory = '%cd%'; $Shortcut.Description = 'Python Anaconda Prompt'; $Shortcut.Save()"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%cd%\Install.lnk'); $Shortcut.TargetPath = '%windir%\System32\cmd.exe'; $Shortcut.Arguments = '/K %CONDA_PATH% run %PYTHON_PATH% -m pip install -r scripts\requrements.txt'; $Shortcut.WorkingDirectory = '%cd%'; $Shortcut.Description = 'Python Anaconda Prompt'; $Shortcut.Save()"

if %errorlevel% equ 0 (
    echo Shortcut created successfully in the current directory: %cd%\Build.lnk
    echo Shortcut created successfully in the current directory: %cd%\Install.lnk
) else (
    echo Failed to create shortcut. Please check your input and try again.
)

pause