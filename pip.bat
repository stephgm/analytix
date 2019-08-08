@echo off
setlocal
set PATH=c:\windows\systems32;c:\anaconda3;c:\anaconda3\Library\usr\bin;c:\anaconda3\Library\bin;c:\anaconda3\Scripts;%PATH%
set PYTHONHTTPSVERIFY=0
c:\anaconda3\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org %*
endlocal
