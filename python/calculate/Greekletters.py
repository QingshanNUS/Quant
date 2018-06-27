# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 16:29:19 2018

@author: QYang
"""
from scipy.stats import norm
from math import log, sqrt, exp
import numpy as np
import bloomberg
#this file only can be applied for futures options but not stocks options

blp = bloomberg.BLPInterface()
# get data for spot LIBOR rates in 1 day, 1 week, 1, 2, 3, 6, 12 month periods
rates = blp.referenceRequest(['US00O/N Index', 'US0001W Index', 'US0001M Index',
                              'US0002M Index', 'US0003M Index', 'US0006M Index',
                              'US0012M Index'], 'PX_LAST')

def rate(T_overyear):
    T = T_overyear * 365
    if T < 7:
        return (rates['PX_LAST'][0] + ((T - 1) * (rates['PX_LAST'][1] - rates['PX_LAST'][0]) / 6)) / 100
    elif T < 30:
        return (rates['PX_LAST'][1] + ((T - 7) * (rates['PX_LAST'][2] - rates['PX_LAST'][1]) / 23)) / 100
    elif T < 61:
        return (rates['PX_LAST'][2] + ((T - 30) * (rates['PX_LAST'][3] - rates['PX_LAST'][2]) / 31)) / 100
    elif T < 91:
        return (rates['PX_LAST'][3] + ((T - 61) * (rates['PX_LAST'][4] - rates['PX_LAST'][3]) / 30)) / 100
    elif T < 183:
        return (rates['PX_LAST'][4] + ((T - 91) * (rates['PX_LAST'][5] - rates['PX_LAST'][4]) / 92)) / 100
    else:
        return (rates['PX_LAST'][5] + ((T - 183) * (rates['PX_LAST'][6] - rates['PX_LAST'][5]) / 182)) / 100
    
#d1 and d2 refer to the 'd1' and 'd2' in Black futures option model
def d1(S, K, vol, T):
    d_up = log(S / K) + np.square(vol) * T / 2
    d_down = vol * sqrt(T)
    return d_up / d_down

def d2(S, K, vol, T):
    d_up = log(S / K) - np.square(vol) * T / 2
    d_down = vol * sqrt(T)
    return d_up / d_down

def delta(r, S, K, vol, T):
    return exp(-1 * r * T) * norm.cdf(d1(S, K, vol, T))

def gamma(r, S, K, vol, T):
    g_up = exp(-1 * r * T) * norm.pdf(d1(S, K, vol, T))
    g_down = S * vol * sqrt(T) 
    return g_up / g_down

#whethercall is used for determining the expression of theta
def theta(r, S, K, vol, T, whethercall=True):
    t1_up = -1 * S * vol * delta(r, S, K, vol, T)
    t1_down = 2 * sqrt(T)
    t1 = t1_up / t1_down
    
    if whethercall:
        t2 = S * r * exp(-1 * r *T) * norm.cdf(d1(S, K, vol, T))
        t3 = -1 * r * K * exp(-1 * r *T) * norm.cdf(d2(S, K, vol, T))
    else:
        t2 = -1 * S * r * exp(-1 * r *T) * norm.cdf(-1 * d1(S, K, vol, T))
        t3 = r * K * exp(-1 * r *T) * norm.cdf(-1 * d2(S, K, vol, T))
    
    return t1 + t2 + t3

def breakeven(r, S, K, vol, T, whethercall=True):
    up = 200 * theta(r, S, K, vol, T, whethercall)
    down = gamma(r, S, K, vol, T) * np.square(S)
    return sqrt(-1 * up / down)

#Bisection method is used to estimate the strike price with given delta and volatility
def imp_K(r, S, vol, T, local_delta):
    upper = 2 * S
    lower = 0
    while True:
        ini_K = (upper + lower) / 2
        imp_delta = delta(r, S, ini_K, vol, T)
        if imp_delta - local_delta > 0.0001:
            lower = ini_K
        elif local_delta - imp_delta > 0.0001:
            upper = ini_K
        else:
            break
    return ini_K

#Bisection method is used to estimate the future price with given delta and volatility
def imp_S(r, K, vol, T, local_delta):
    upper = 3 * K
    lower = 0
    while True:
        ini_S = (upper + lower) / 2
        imp_delta = delta(r, ini_S, K, vol, T)
        if imp_delta - local_delta > 0.0001:
            upper = ini_S
        elif local_delta - imp_delta > 0.0001:
            lower = ini_S
        else: 
            print(ini_S)
            break
    return ini_S
