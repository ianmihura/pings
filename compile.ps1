pyinstaller --onefile main.py
Move-Item -Path .\dist\main.exe -Destination .\pings.exe
pause