@echo off
setlocal
set PATH=c:\windows\systems32;c:\anaconda3-b4;c:\anaconda3-b4\Library\usr\bin;c:\anaconda3-b4\Library\bin;c:\anaconda3-b4\Scripts;%PATH%
set PYTHONHTTPSVERIFY=0
c:\anaconda3-b4\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org %*
endlocal
