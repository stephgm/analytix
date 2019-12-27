@echo off
setlocal
set PATH=%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;c:\anaconda3-b4;c:\anaconda3-b4\Library\usr\bin;c:\anaconda3-b4\Library\bin;c:\anaconda3-b4\Scripts;c:\Program Files\7-zip
REM c:\anaconda3-b4\Scripts\pyinstaller.exe --clean --paths c:\tools\src\modules --add-data "c:\tools\src\adarConfigurator\adarConfigurator.ui;c:\tools\src\adarConfigurator" adarConfigurator.py
c:\anaconda3-b4\Scripts\pyinstaller.exe --clean --paths c:\tools\src\modules --add-data "adarConfigurator.ui;." adarConfigurator.py
endlocal
@pause
