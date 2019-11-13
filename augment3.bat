@echo off
setlocal
set PATH=c:\windows\systems32;c:\anaconda3;c:\anaconda3\Library\usr\bin;c:\anaconda3\Library\bin;c:\anaconda3\Scripts;c:\Program Files\7-zip
set PYTHONHTTPSVERIFY=0
set TABULATE_INSTALL=lib-only
:: for unit testing
:: c:\anaconda3\Scripts\conda.exe install -y pyculib
:: exit
c:\anaconda3\Scripts\conda.exe config --set ssl_verify false
c:\anaconda3\Scripts\conda.exe update -n base conda
c:\anaconda3\Scripts\conda.exe update --all -y
c:\anaconda3\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install --upgrade pip
c:\anaconda3\Scripts\conda.exe install -y R cartopy swig pyopengl pyopengl-accelerate pyqtgraph traitlets vispy hdf4 pymssql boost cudatoolkit cmake line_profiler cython cairo pyopengl pyopengl-accelerate plotly autopep8 geopandas selenium mock nodejs holoviews datashader hvplot graphviz panel param xmltodict
c:\anaconda3\Scripts\conda.exe install -y -c spyder-ide spyder=4.0.0rc1
:: failures : pyculib
:: glib gobject-introspection
c:\anaconda3\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install msgpack argparse urwid
:: what actually works
c:\anaconda3\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install construct hexdump pypcapfile python-pcapng avro python-pptx
c:\anaconda3\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install pyopencl pycuda
c:\anaconda3\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install altair altair-widgets seaborn-altair altair-recipes yerkes gencharts
:: John Weier's addtitions
c:\anaconda3\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install actdiag blockdiag nwdiag seqdiag arrow colorcet dill pathlib terminal-table tabulate
c:\anaconda3\Scripts\conda.exe clean -a -y
c:\anaconda3\python.exe c:\tools\src\feature_download.py --output \anaconda3\Lib\site-packages\cartopy\data physical
c:\anaconda3\python.exe c:\tools\src\feature_download.py --output \anaconda3\Lib\site-packages\cartopy\data physical
c:\anaconda3\python.exe c:\tools\src\feature_download.py --output \anaconda3\Lib\site-packages\cartopy\data cultural
c:\anaconda3\python.exe c:\tools\src\feature_download.py --output \anaconda3\Lib\site-packages\cartopy\data cultural-extra
c:\anaconda3\python.exe c:\tools\src\feature_download.py --output \anaconda3\Lib\site-packages\cartopy\data gshhs
cd C:\tools\natural_earth
mkdir C:\anaconda3\Lib\site-packages\cartopy\data\shapefiles\natural_earth
robocopy . C:\anaconda3\Lib\site-packages\cartopy\data\shapefiles\natural_earth /s /e
cd ..
copy  NE1_HR_LC_SR_W_DR.png C:\anaconda3\Lib\site-packages\cartopy\data\raster\natural_earth
cd c:\tools
7z x ViTables-3.0.0.tar 
cd ViTables-3.0.0
c:\anaconda3\python setup.py install
cd ..
rmdir /s /q ViTables-3.0.0
@pause
:: done the below at work
endlocal
exit
