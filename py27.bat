@echo off
setlocal
set PATH=c:\windows\systems32;c:\anaconda2;c:\anaconda2\Library\usr\bin;c:\anaconda2\Library\bin;c:\anaconda2\Scripts;%PATH%
c:\anaconda2\python.exe -W ignore %*
endlocal
