#!/bin/bash

if [ "$1" == "" ];then
echo "usage: $0 /path/to/anaconda"
exit
fi

export PATH="$PREFIX:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin"
export LD_LIBRARY_PATH="$PREFIX/lib:/lib64:/usr/lib64:/usr/local/lib64:/lib:/usr/lib:/usr/local/lib"
export GEOS_DIR="$1"
export PKG_CONFIG_PATH="$1/lib/pkgconfig"
export PYTHONHTTPSVERIFY=0
export TABULATE_INSTALL=lib-only

PREFIX="$1"/bin

$PREFIX/conda update --all -y
$PREFIX/conda clean -a -y

pcmd="$PREFIX/pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade"

$pcmd msgpack argparse urwid construct hexdump sysv_ipc pypcapfile python-pcapng avro python-pptx orderedset objgraph pandastable altair altair-widgets seaborn-altair altair-recipes yerkes gencharts actdiag blockdiag nwdiag seqdiag arrow dill pathlib terminal-table tabulate pyinstaller
