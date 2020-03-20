#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 16:12:01 2020

@author: hollidayh
"""

from numpy import asfarray, zeros, nan, nonzero, linalg, cross, isfinite, pi, empty
from math import sqrt, sin, cos, exp, acos, atan2, hypot, copysign, asin, degrees
from numba import njit

@njit
def Accelerate_Gravity(Time, Pos):
    """
    Computes earth's gravity for a WGS-84 zonal harmonic, up to 18x18
    Parameters
    ----------
    Time : float
        Reference Time.
    Pos : Array
        ECI position vector.

    Returns
    -------
    gvec, acceleration due to earth's gravity in eci frame

    """
    We = 99
    Re = 99
    Mu_e = 99
    xj_wgs = empty((18,18))
    c_wgs  = empty((18,18))
    s_wgs  = empty((18,18))
    ###############################
    Posnorm = linalg.norm(Pos)
    Posnrm2 = Posnorm**2
    c_theta = Pos[2] / Posnorm
    s_theta = sqrt(1.0 - c_theta**2)
    if s_theta == 0.0:
        return empty(0)
    theta = arc_cos(c_theta) # co-latitude
    phi = atan2(Pos[1],Pos[0]) - We*Time
    po,p = legendre_poly(c_theta)
    g = asfarray([1,0,0])
    arg0 = Re * (1.0 / Posnorm)
    a = arg0
    for n in range(1,18):
        nn = n + 1.0
        a = arg0 * a
        xnp1 = nn + 1.0
        g[0] = g[0] + xnp1*a*xj_wgs[0,n]*po[0,n]
        g[1] = g[1] + a*xj_wgs[0,n]*nn*(po[0,n]*c_theta - po[0,n-1])
        a_num = int(min([nn,18]))
        for m in range(a_num):
            mm = m + 1.
            xnpm = nn + mm
            arg1 = mm*phi
            b1 = cos(arg1)
            b2 = sin(arg1)
            arg2 = c_wgs[n,m]*b1 + s_wgs[n,m]*b2
            g[0] = g[0] + xnp1*a*p[n,m]*arg2
            g[1] = g[1] + a*(nn*p[n,m]*c_theta - xnpm*p[n-1,m])*arg2
            g[2] = g[2] + mm*a*p[n,m]*(c_wgs[n,m]*b2 - s_wgs[n,m]*b1)
    arg3 = Mu_e / Posnrm2
    arg4 = 1. / s_theta
    gvec = sph2rec(asfarray([-1.*arg3*g[0],arg3*g[1]*arg4,-1.*arg3*g[2]*arg4]),theta,phi)
    return ecr2eci(Time,gvec[0],gvec[1],gvec[2])

def legendre_poly(x):
    pass

def ecr2eci(itime,xi,yi,zi):
    pass

def arc_cos(arg):
    if arg <= -1.:
        return pi
    elif arg >= 1.0:
        return 0.0
    else:
        return acos(arg)

def sph2rec(istate, theta, phi):
    st = sin(theta)
    ct = cos(theta)
    sp = sin(phi)
    cp = cos(phi)
    b12 = istate[0]*st + istate[1]*ct
    return asfarray([b12*cp - istate[2]*sp,
                     b12*sp + istate[2]*cp,
                     istate[0]*ct - istate[1]*st])

