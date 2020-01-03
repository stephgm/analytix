@echo off
setlocal
set PATH=c:\windows\systems32;c:\anaconda3-b4;c:\anaconda3-b4\Library\usr\bin;c:\anaconda3-b4\Library\bin;c:\anaconda3-b4\Scripts;%PATH%
c:\anaconda3-b4\python.exe -W ignore %*
endlocal
