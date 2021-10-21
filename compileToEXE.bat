@ECHO ON
::COMMENTS
pyinstaller --onefile ./threadedMain.py
copy .\dist\threadedMain.exe ".\theLoginator.exe"
@RD /S /Q "./build"
@RD /S /Q "./dist"
@RD /S /Q "./__pycache__"
