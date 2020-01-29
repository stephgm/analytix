@echo off
set ccmd="c:\anaconda2\Scripts\conda.exe install -y"
set pcmd="c:\anaconda2\Scripts\pip.exe install"
set pcmd="c:\anaconda2\Scripts\pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org"
set pcmd="c:\anaconda2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org"
c:\anaconda2\Scripts\conda.exe update -n base conda
c:\anaconda2\Scripts\conda.exe update --all -y
::c:\anaconda2-5.2.0\Scripts\pip.exe install --upgrade pip
c:\anaconda2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install --upgrade pip
:: ccmd="$PREFIX/conda install"
c:\anaconda2\Scripts\conda.exe install -y R cartopy swig pyopengl pyopengl-accelerate pyqtgraph traitlets vispy hdf4 pymssql boost cudatoolkit pyculib cmake line_profiler cython cairo pyopengl pyopengl-accelerate plotly autopep8 geopandas selenium mock nodejs holoviews datashader hvplot graphviz panel param
:: glib gobject-introspection
c:\anaconda2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install msgpack argparse urwid
:: %pcmd% install construct hexdump sysv_ipc pypcapfile python-pcapng pyrasite pyrasite-gui avro spyder-memory-profiler veusz python-pptx orderedset objgraph pygraphviz PyGObject
:: %pcmd% install construct hexdump pypcapfile python-pcapng pyrasite pyrasite-gui avro spyder-memory-profiler veusz python-pptx orderedset objgraph pygraphviz PyGObject ggpy
:: what actually works
c:\anaconda2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install construct hexdump pypcapfile python-pcapng avro python-pptx
c:\anaconda2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install pyopencl pycuda
c:\anaconda2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install altair altair-widgets seaborn-altair altair-recipes yerkes gencharts
:: John Weier's addtitions
c:\anaconda2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install actdiag blockdiag nwdiag seqdiag arrow colorcet dill pathlib 
c:\anaconda2\Scripts\conda.exe clean -a -y
c:\anaconda2\python.exe c:\tools\src\feature_download.py --output \anaconda2\Lib\site-packages\cartopy\data physical
c:\anaconda2\python.exe feature_download.py --output \anaconda2\Lib\site-packages\cartopy\data physical
c:\anaconda2\python.exe feature_download.py --output \anaconda2\Lib\site-packages\cartopy\data cultural
c:\anaconda2\python.exe feature_download.py --output \anaconda2\Lib\site-packages\cartopy\data cultural-extra
c:\anaconda2\python.exe feature_download.py --output \anaconda2\Lib\site-packages\cartopy\data gshhs
cd C:\tools\natural_earth
mkdir C:\anaconda2\Lib\site-packages\cartopy\data\shapefiles\natural_earth
robocopy . C:\anaconda2\Lib\site-packages\cartopy\data\shapefiles\natural_earth /s /e
cd ..
copy  NE1_HR_LC_SR_W_DR.png C:\anaconda2\Lib\site-packages\cartopy\data\raster\natural_earth
@pause
:: done the below at work
exit
tar -xf Downloads/ViTables-3.0.0.tar
cd ViTables-3.0.0
$PREFIX/python setup.py install
cd ..
rm -rf ViTables-3.0.0
