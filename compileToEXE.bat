@ECHO ON
::COMMENTS
pyinstaller --onefile ./LogCleaner.py
copy .\dist\LogCleaner.exe ".\LogCleaner.exe"
@RD /S /Q "./build"
@RD /S /Q "./dist"
@RD /S /Q "./__pycache__"
