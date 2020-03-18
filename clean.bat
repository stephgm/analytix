@echo off
color 0A
del /s *.pyc
del /s *_py.txt
del /s *.npy
for /f "delims=" %%d in ('dir /s /b /ad ^| sort /r') do rd "%%d" >NUL 2>&1
@pause
