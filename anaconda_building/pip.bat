@echo off
setlocal
set PATH=c:\windows\systems32;c:\anaconda3-2020.02b2;c:\anaconda3-2020.02b2\Library\usr\bin;c:\anaconda3-2020.02b2\Library\bin;c:\anaconda3-2020.02b2\Scripts;%PATH%
set PYTHONHTTPSVERIFY=0
c:\anaconda3-2020.02b2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org %*
endlocal
