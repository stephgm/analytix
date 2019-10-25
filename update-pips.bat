@echo off

setlocal
set PATH=c:\windows\systems32;c:\anaconda3;c:\anaconda3\Library\usr\bin;c:\anaconda3\Library\bin;c:\anaconda3\Scripts;c:\Program Files\7-zip
set PYTHONHTTPSVERIFY=0
set TABULATE_INSTALL=lib-only

c:\anaconda3\Scripts\conda.exe update --all -y
c:\anaconda3\Scripts\conda.exe clean -a -y

c:\anaconda3\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install --upgrade msgpack argparse urwid construct hexdump sysv_ipc pypcapfile python-pcapng avro python-pptx orderedset objgraph pandastable altair altair-widgets seaborn-altair altair-recipes yerkes gencharts actdiag blockdiag nwdiag seqdiag arrow dill pathlib terminal-table tabulate

endlocal
