@echo off
set ccmd="c:\anaconda2\Scripts\conda.exe install -y"
set pcmd="c:\anaconda2\Scripts\pip.exe install"
set pcmd="c:\anaconda2\Scripts\pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org"
set pcmd="c:\anaconda2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org"
c:\anaconda2\Scripts\conda.exe update -n base conda
c:\anaconda2\Scripts\conda.exe update --all -y
::c:\anaconda2-5.2.0\Scripts\pip.exe install --upgrade pip
%pcmd% install --upgrade pip
:: ccmd="$PREFIX/conda install"
%ccmd% R cartopy swig pyopengl pyopengl-accelerate pyqtgraph traitlets vispy hdf4 pymssql boost cudatoolkit pyculib cmake line_profiler cython cairo pyopengl pyopengl-accelerate plotly
:: glib gobject-introspection
%pcmd% install msgpack argparse urwid
:: %pcmd% install construct hexdump sysv_ipc pypcapfile python-pcapng pyrasite pyrasite-gui avro spyder-memory-profiler veusz python-pptx orderedset objgraph pygraphviz PyGObject
:: %pcmd% install construct hexdump pypcapfile python-pcapng pyrasite pyrasite-gui avro spyder-memory-profiler veusz python-pptx orderedset objgraph pygraphviz PyGObject ggpy
:: what actually works
c:\anaconda2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install construct hexdump pypcapfile python-pcapng avro python-pptx
%pcmd% install pyopencl pycuda
:: John Weier's addtitions
c:\anaconda2\python -m pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org install actdiag blockdiag nwdiag seqdiag arrow colorcet dill pathlib 
@pause
:: done the below at work
exit
tar -xf Downloads/ViTables-3.0.0.tar
cd ViTables-3.0.0
$PREFIX/python setup.py install
cd ..
rm -rf ViTables-3.0.0

unzip Downloads/cartopy-master.zip
cd cartopy-master
$PREFIX/python setup.py install
cd ..
rm -rf cartopy-master

tar -zxf Downloads/basemap-1.0.7.tar.gz
cd basemap-1.0.7
$PREFIX/python setup.py install
cd ..
rm -rf basemap-1.0.7

# version=$($PREFIX/python -V | awk '{print $1}'

mkdir -p $PREFIX/../lib/python2.7/site-packages/cartopy/data/shapefiles
cd $PREFIX/../lib/python2.7/site-packages/cartopy/data/shapefiles
tar -zxvf ~/natural_earth.tgz
cd -

mkdir -p $PREFIX/../lib/python2.7/site-packages/cartopy/data/raster/natural_earth
cp NE1_HR_LC_SR_W_DR.png $PREFIX/../lib/python2.7/site-packages/cartopy/data/raster/natural_earth/.
:: HERE
cd C:\tools\natural_earth
mkdir C:\anaconda2\Lib\site-packages\cartopy\data\shapefiles\natural_earth
robocopy . C:\anaconda2\Lib\site-packages\cartopy\data\shapefiles\natural_earth /s /e
cd ..
copy  NE1_HR_LC_SR_W_DR.png C:\anaconda2\Lib\site-packages\cartopy\data\raster\natural_earth
c:\anaconda2\Scripts\conda.exe clean -a
