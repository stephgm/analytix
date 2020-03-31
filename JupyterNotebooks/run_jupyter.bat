@echo off
setlocal
set PATH=%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;c:\anaconda3-2020.02b1;c:\anaconda3-2020.02b1\Library\usr\bin;c:\anaconda3-2020.02b1\Library\bin;c:\anaconda3-2020.02b1\Scripts;%PATH%
jupyter-notebook
endlocal
