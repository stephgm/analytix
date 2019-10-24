#!/bin/bash -e

# git pre-clone commands
# git config --global http.sslVerify false
# git post-clone commands
# git remote set-url origin git@github.com:hollidayh/analytix.git
# ssh-keygen -t rsa -b 4096 -C "hpholliday@gmail.com"
# eval $(ssh-agent -s)
# ssh-add ~/.ssh/id_rsa
# sudo yum -y install xclip
# xclip -sel clip < ~/.ssh/id_rsa.pub
# login to github -> settings -> ssh keys -> import 
# this will ask for the private key password (not git hub password)

if [ "$1" == "" ];then
echo "usage: $0 /path/to/anaconda"
exit
fi

PREFIX="$1"/bin
# yum -y install "gcc*" graphviz graphviz-devel "mesa-*" opencl-filesystem.noarch opencl-headers.noarch
export PATH="$PREFIX:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin"
export LD_LIBRARY_PATH="$PREFIX/lib:/lib64:/usr/lib64:/usr/local/lib64:/lib:/usr/lib:/usr/local/lib"
export GEOS_DIR="$1"
export PKG_CONFIG_PATH="$1/lib/pkgconfig"
export PYTHONHTTPSVERIFY=0
export TABULATE_INSTALL=lib-only
# check certificates may comment the next 2 out
if [ 1 == 1 ];then
$PREFIX/conda config --set ssl_verify false
#$PREFIX/conda update -n base conda -y
pcmd="$PREFIX/pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org"
$pcmd --upgrade pip
ccmd="$PREFIX/conda install -y"
# no R, no cuda stuff cuz it regresses python
$ccmd gcc_impl_linux-64 gcc_linux-64 gfortran_impl_linux-64 gfortran_linux-64 binutils_linux-64 binutils_impl_linux-64 gsl gxx_impl_linux-64 gxx_linux-64 make cartopy swig line_profiler vispy boost cmake autopep8 hdf4 glib pyqtgraph pyopengl pyopengl-accelerate gobject-introspection pymssql autopep8 geopandas selenium mock nodejs holoviews datashader hvplot graphviz panel param xmltodict
$pcmd msgpack argparse urwid
# pdfminer
# PyGObject, veusz DNW, spyder-memory-profiler?
$pcmd construct hexdump sysv_ipc pypcapfile python-pcapng avro python-pptx orderedset objgraph pandastable # cx-Freeze
# upgrading
#pcmd="$PREFIX/pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org -U"
$pcmd altair altair-widgets seaborn-altair altair-recipes yerkes gencharts
$pcmd actdiag blockdiag nwdiag seqdiag arrow dill pathlib
$pcmd -U ray
$pcmd modin vega_datasets pdvega
$pcmd ggplot pyggplot
$pcmd terminal_table tabulate
# for carpopy features
$PREFIX/conda update --all -y
$PREFIX/conda clean -a -y
#$PREFIX/python feature_download.py --output /storage/data/local/lib/python3.7/site-packages/cartopy/data physical
#$PREFIX/python feature_download.py --output /storage/data/local/lib/python3.7/site-packages/cartopy/data cultural
#$PREFIX/python feature_download.py --output /storage/data/local/lib/python3.7/site-packages/cartopy/data cultural-extra
#$PREFIX/python feature_download.py --output /storage/data/local/lib/python3.7/site-packages/cartopy/data gshhs
fi
# scrubbed 7zip
#tar -zxvf uza.tgz
#cd uza
#make
#cp bin/7za $PREFIX/uza
#cd -
##########################################
#exit
if [ 1 == 1 ];then
tar -zxf ~/Downloads/ViTables-3.0.0.tar.gz
cd ViTables-3.0.0
$PREFIX/python setup.py install
cd ..
rm -rf ViTables-3.0.0
fi

# cartopy handled by conda
#unzip ~/Downloads/cartopy-master.zip
#cd cartopy-master
#$PREFIX/python setup.py install
#cd ..
#rm -rf cartopy-master

# DNW
#tar -zxf ~/Downloads/basemap-1.0.7.tar.gz
#cd basemap-1.0.7
#$PREFIX/python setup.py install
#cd ..
#rm -rf basemap-1.0.7

# version=$($PREFIX/python -V | awk '{print $1}'

mkdir -p $PREFIX/../lib/python3.7/site-packages/cartopy/data/shapefiles
cd $PREFIX/../lib/python3.7/site-packages/cartopy/data/shapefiles
#tar -zxvf ~/natural_earth.tgz
cp -rv ~/natural_earth . 
cd -

mkdir -p $PREFIX/../lib/python3.7/site-packages/cartopy/data/raster/natural_earth
cp ~/Downloads/NE1_HR_LC_SR_W_DR.png $PREFIX/../lib/python3.7/site-packages/cartopy/data/raster/natural_earth/.

cd $PREFIX/..

./bin/python -m compileall . 

cd bin

ln -s x86_64-conda_cos6-linux-gnu-gcc ./gcc

cd ..

chmod -R 755 *

#cd ~/Downloads
#tar -jxvf p7zip_16.02_src_all.tar.bz2
#cd p7zip_16.02
#make
#cp bin/7za $PREFIX/.
#cd ..
#rm -rf p7zip_16.02



exit
# working
tar -zxvf eric6-18.05.tar.gz
cd eric6-18.05
ins=$(dirname $PREFIX)
$PREFIX/python install.py -b $ins 
cd ..
rm -rf eric6-18.05
