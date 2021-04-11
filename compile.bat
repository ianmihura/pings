pyinstaller --onefile main.py
COPY /B /Y dist\main.exe /B %SystemRoot%\System32\pings.exe
pause