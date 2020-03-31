@echo off

setlocal
set PATH=%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;c:\anaconda3-2020.02b2;c:\anaconda3-2020.02b2\Library\usr\bin;c:\anaconda3-2020.02b2\Library\bin;c:\anaconda3-2020.02b2\Scripts;c:\Program Files\7-zip
set PYTHONHTTPSVERIFY=0
set TABULATE_INSTALL=lib-only

c:\anaconda3-2020.02b2\Scripts\conda.exe update --all -y
c:\anaconda3-2020.02b2\Scripts\conda.exe clean -a -y

c:\anaconda3-2020.02b2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install --upgrade msgpack argparse urwid construct hexdump pypcapfile python-pcapng avro python-pptx orderedset objgraph pandastable altair altair-widgets seaborn-altair altair-recipes yerkes gencharts actdiag blockdiag nwdiag seqdiag arrow dill pathlib terminal-table tabulate pyinstaller removestar flynt ipytree pdfminer3k django
@pause
endlocal
