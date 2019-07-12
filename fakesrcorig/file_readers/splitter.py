import os
import sys

RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([root for root,dirs,files in os.walk(RELATIVE_LIB_PATH)
                    for xfile in files
                    if os.path.isfile(os.path.join(root,xfile)) and xfile.endswith('.py')])

import numpy
from copy import deepcopy

import coord

a = numpy.arange(5)
print a
b = a
print b
a = numpy.arange(6)
print b
b = deepcopy(a)
print b

coord.damnitJanet('fudge dragon')
