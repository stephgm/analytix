@echo off
setlocal
set PATH=c:\windows\systems32;c:\anaconda3;c:\anaconda3\Library\usr\bin;c:\anaconda3\Library\bin;c:\anaconda3\Scripts;%PATH%
c:\anaconda3\Scripts\conda %*
endlocal
