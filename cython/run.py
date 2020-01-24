#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 20:15:46 2020

@author: hollidayh
"""

import foo
import numpy as np

array_1 = np.random.uniform(0, 1000, size=(3000, 2000)).astype(np.intc)
array_2 = np.random.uniform(0, 1000, size=(3000, 2000)).astype(np.intc)
a = 4
b = 3
c = 9

res = foo.compute(array_1.astype(np.double), array_2.astype(np.double), a, b, c)
print(res)
res = foo.numpyFunction(100)
print(res)