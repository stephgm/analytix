import sys
import os

RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([root for root,dirs,files in os.walk(RELATIVE_LIB_PATH)
                    for xfile in files
                    if os.path.isfile(os.path.join(root,xfile)) and xfile.endswith('.py')])

from xtime import fml
import numpy
fml('fcl')

def damnitJanet(thingy):
    print thingy
    a = numpy.arange(15)
    print a