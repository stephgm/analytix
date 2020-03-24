#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 16:12:01 2020

@author: hollidayh
"""

from numpy import asfarray, zeros, nan, nonzero, linalg, cross, isfinite, pi, empty, sign, concatenate
from math import sqrt, sin, cos, exp, acos, atan2, hypot, copysign, asin, degrees
from numba import njit

ATM_MAX_ALT = 1476400. / 3.28084
We = 99
Re = 99
Mu_e = 99
dt_max = 99
xj_wgs = empty((18,18))
c_wgs  = empty((18,18))
s_wgs  = empty((18,18))
# exponential desity coefficient cubic fit to 86 km then linear to 1000 km
EDC_C = asfarray([8.455411e-5, 0.52097, 0.7705354, 1.836811, -1.238564,
                 -2.1094, -.8904344, 2.456946, -8.339631, -16.462598])
EDC_L = asfarray([-2.930811e-5, -4.807431e-5, -5.439295e-5, -7.386702e-5,
                  -7.386702e-5, -3.077898e-5, -3.050896e-5, -3.879384e-5,
                  -5.151679e-5, -2.40934e-5, -7.58769e-6])

# all state vectors : [Time, Px, Py, Pz, Vx, Vy, Vz]
# Pos = state[1:4], Vel = state[4:7]

def prop_runge_kutta(iVector, TStep, Beta):
    """

    """
    xdel = float(sign(TStep)*min(dt_max,abs(TStep)))
    eci_state = ecr2eci(iVector)
    f1,f2,f3,f4 = (empty(6).T,) * 4
    tnow = asfarray([eci_state[0]])
    while abs(xdel) > 0:
        del2  = xdel / 2.
        delo6 = xdel / 6.
        f1[0] = eci_state[4]
        f1[1] = eci_state[5]
        f1[2] = eci_state[6]
        ago = Acc_Gravity_Drag(eci_state, Beta)
        if not ago.size:
            return ()
        # this is an ECI state vector
        f1[3] = ago[0]
        f1[4] = ago[1]
        f1[5] = ago[2]
        u = concatenate((tnow + del2,eci_state[1:7] + del2 * f1))
        f2[0] = u[4]
        f2[1] = u[5]
        f2[2] = u[6]
        ago = Acc_Gravity_Drag(u,Beta)
        if not ago.size:
            return ()
        f2[3] = ago[0]
        f2[4] = ago[1]
        f2[5] = ago[2]
        u = concatenate((tnow + del2,eci_state[1:7] + del2 * f2))
        f3[0] = u[4]
        f3[1] = u[5]
        f3[2] = u[6]
        ago = Acc_Gravity_Drag(u,Beta)
        if not ago.size:
            return ()
        f3[3] = ago[0]
        f3[4] = ago[1]
        f3[5] = ago[2]
        u = concatenate((tnow + xdel,eci_state[1:7] + xdel * f3))
        # fourth step
        f4[0] = u[4]
        f4[1] = u[5]
        f4[2] = u[6]
        ago = Acc_Gravity_Drag(u,Beta)
        if not ago.size:
            return ()
        f4[3] = ago[0]
        f4[4] = ago[1]
        f4[5] = ago[2]
        # New State vector
        eci_state = eci_state + delo6 * (f1 + 2.0 * (f2+f3) + f4)
        tnow[0] += xdel
        TStep -= xdel
        xdel = sign(TStep)*min(dt_max,abs(TStep))
    Acc = Acc_Gravity_Drag(eci_state, Beta)
    return eci2ecr(concatenate((eci_state,Acc)))

def ecr2eci(ecr):
    return ecr

def eci2ecr(eci):
    pass

def ecr2lla(ecr):
    pass

@njit
def Accelerate_Gravity(iState):
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
    Posnorm = linalg.norm(iState[1:4])
    Posnrm2 = Posnorm**2
    c_theta = iState[3] / Posnorm
    s_theta = sqrt(1.0 - c_theta**2)
    if s_theta == 0.0:
        return empty(0)
    theta = arc_cos(c_theta) # co-latitude
    phi = atan2(iState[2],iState[1]) - We*iState[0]
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
    return ecr2eci(iState[0],gvec[0],gvec[1],gvec[2])

def Acc_Gravity_Drag(iState, Beta):
    Acc = Accelerate_Gravity(iState)
    if not Acc.size:
        return Acc
    alt_m = ecr2lla(iState[1],iState[2],iState[3])[2]
    if alt_m <= 0. or not isfinite(alt_m):
        return empty(0)
    if Beta > 0.0 and alt_m <= ATM_MAX_ALT:
        tmatrix = asfarray([0,0,We])
        Rel_Vel = iState[4:7] - cross(tmatrix,iState[1:4])
        Vmag = linalg.norm(Rel_Vel)
        c2 = -1.0 * (Vmag * get_1976_atmospheric_density(alt_m)) / (2.0 * Beta)
        Acc = Acc + c2 * Rel_Vel
    return Acc

def get_1976_atmospheric_density(alt_m):

    local_altitude = alt_m * 3.28084
    idx = 0
    for i in range(10):
        if alt[i] < local_altitude:
            idx = i
    #                                                        IDK          density slug/ft^3 to km/m^3
    return exp((EDC_C[idx] + EDC_L[idx] * local_altitude) + -6.0420511) / 0.00193882

@njit
def legendre_poly(x):
    x2 = x*x
    a2 = 1. - x2
    a = sqrt(a2)
    po = zeros((1,18))
    po[0,0] = x
    po[0,1] = (3.0*x2 - 1.0) / 2.0
    for i in range(1,17):
        ii = i + 1.
        po[0,i+1] = ((2.0 * ii + 1.0) * x * po[0,i] - ii * po[0,i-1]) / (ii + 1.0)
    p = zeros((18,18))
    c = zeros((19,1))
    for m in range(18):
        dm = m + 1.0
        c[...] = 0.
        last_idx = m + 2
        c[m,0] = 1.0
        fact = 1.0
        for i in range(m+1):
            c[m,0] = c[m,0] * fact * a
            fact += 2.
        c[m+1,0] = x * (2.0 * dm + 1.0) * c[m,0]
        for i in range(m+2,18):
            di = i + 1.0
            c[last_idx,0] = ((2.0 * di - 1.0) * x * c[i-1,] - (di+dm-1.0) * c[i-2,0]) / (di-dm)
            last_idx += 1
        for k in range(18):
            p[k,m] = c[k,0]
    return po,p

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

