cd C:\Users\39544686g\Desktop\pings\
pyinstaller --onefile main.py
COPY /B /Y dist\main.exe /B %SystemRoot%\System32\pings.exe
pause