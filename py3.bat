@echo off
setlocal
set PATH=c:\windows\systems32;c:\anaconda3-2019.10b3;c:\anaconda3-2019.10b3\Library\usr\bin;c:\anaconda3-2019.10b3\Library\bin;c:\anaconda3-2019.10b3\Scripts;%PATH%
c:\anaconda3-2019.10b3\python.exe -W ignore %*
endlocal
