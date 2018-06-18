# -*- coding: utf-8 -*-
"""
Created on Wed May  28 2018

@author: Qingshan
"""
from __future__ import division
import os
import bloomberg
import numpy as np
import pandas as pd
import datetime as dt
import math
import definitions
import datetime as dt

blp = bloomberg.BLPInterface()

#curr_dir = os.getcwd()
#data_dir = os.path.join(curr_dir, 'Data')
data_dir = os.path.join(os.getcwd(), 'daily')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    
start = dt.datetime(2014, 12, 1)
end = dt.datetime.today()  # Date why RBT2 stops reporting second active contract
    
#symbols
copper = blp.historicalRequest(['LMCADS03 Comdty'], ['PX_LAST'], start, end, periodicitySelection = 'DAILY')
spot = blp.historicalRequest(['CU3 Comdty'], ['PX_LAST'], start, end, periodicitySelection = 'DAILY')

df = pd.concat([copper, spot], axis=1)
df = df.fillna(method='ffill')

#calculate returns, vols and the ration of vols
df['LME stdv'] = pd.Series()
df['CU3 stdv'] = pd.Series()
df['LME aver'] = pd.Series()
df['CU3 aver'] = pd.Series()
df['LC ratio'] = pd.Series()

L_vois = []
S_vois = []

#initialize lists for storing the data
for i in range(len(df) - 30):
    L_vois.append(np.std(df.iloc[i + 1: i + 31, 0], ddof=1))
    S_vois.append(np.std(df.iloc[i + 1: i + 31, 1], ddof=1))

df.iloc[30:, 2] = L_vois
df.iloc[30:, 3] = S_vois

L_vois = []
S_vois = []

for i in range(len(df) - 30):
    L_vois.append(np.mean(df.iloc[i + 1: i + 31, 0]))
    S_vois.append(np.mean(df.iloc[i + 1: i + 31, 1]))
    
df.iloc[30:, 4] = L_vois
df.iloc[30:, 5] = S_vois

df.iloc[30:, 6] = (df.iloc[30:, 4] * df.iloc[30:, 2]) / (df.iloc[30:, 5] * df.iloc[30:, 3])

df.to_csv(os.path.join(data_dir, 'LMESHFP_copper.csv'))



upper = sorted(df['LC ratio'])[-92]
lower = sorted(df['LC ratio'])[91]

#GET future price for SHFE CU3
data_CU3 = blp.referenceRequest(['CUN8 COMB Comdty', 'CUQ8 COMB Comdty', 'CUU8 COMB Comdty',
                              'CUV8 COMB Comdty', 'CUX8 COMB Comdty', 'CUZ8 COMB Comdty',
                              'CUF9 COMB Comdty', 'CUG9 COMB Comdty', 'CUH9 COMB Comdty',
                              'CUJ9 COMB Comdty', 'CUK9 COMB Comdty'],'PX_LAST')

#time to maturity
T = []
for i in range(11):
    T.append(((i + 1) * 365 / 12 + 18 - dt.datetime.today().day) / 365)
    
#calculate the upper bounds and the lower bounds of implied volatility table for CU3

delta = {0: 0.9, 2: 0.75, 4: 0.5, 6: 0.25, 8: 0.1}

#for upper bound
df = pd.read_excel('data.xlsx')
df = df[0:13]

for i in range(13):
    if i == 0:
        continue
    if i == 1:
        for j in range(10):
            df.iloc[i][j] = 'NA'
        continue
    for j in [4]:
        r = definitions.rate(T[i - 2])
        K = df.iloc[i][j]
        vol = df.iloc[i][j + 1] / 100
        S = definitions.imp_S(r, K, vol, T[i - 2], delta[j])
        f1 = S * definitions.breakeven(r, S, K, vol, T[i - 2])
        
        S = data_CU3['PX_LAST'][i - 2]
        upper = 5 * vol
        lower = 0.5 * vol 
        while True:
            ini_vol = (upper + lower) / 2
            K = definitions.imp_K(r, S, ini_vol, T[i - 2], delta[j])
            f2 = S * definitions.breakeven(r, S, K, ini_vol, T[i - 2])
            print(f1 / f2)
            if f1 / f2 - 0.02569 > 0.001:
                lower = ini_vol
            elif f1 / f2 - 0.02569 < -0.001:
                upper = ini_vol
            else:
                break
        df.iloc[i][j] = K
        df.iloc[i][j + 1] = ini_vol * 100

# =============================================================================
# df[['10 Delta Put', 'Unnamed: 1', '25 Delta Put', 'Unnamed: 3', '50 Delta',
#     'Unnamed: 5', '25 Delta Call', 'Unnamed: 7', '10 Delta Call', 'Unnamed: 9']].to_csv('upperbound.csv')
# 
# #for lower bound
# df = pd.read_excel('data.xlsx')
# df = df[0:13]
# 
# for i in range(13):
#     if i != 0:
#         continue
#     if i == 1:
#         for j in range(10):
#             df.iloc[i][j] = 'NA'
#         continue
#     for j in [0, 2, 4, 6, 8]:
#         r = definitions.rate(T[i - 2])
#         K = df.iloc[i][j]
#         vol = df.iloc[i][j + 1] / 100
#         S = definitions.imp_S(r, K, vol, T[i - 2], delta[j])
#         f1 = definitions.breakeven(r, S, K, vol, T[i - 2])
#         
#         S = data_CU3['PX_LAST'][i - 2]
#         upper = 4 * vol
#         lower = 0
#         while True:
#             ini_vol = (upper + lower) / 2
#             K = definitions.imp_K(r, S, ini_vol, T[i - 2], delta[j])
#             f2 = definitions.breakeven(r, S, K, ini_vol, T[i - 2])
#             if f1 / f2 - 0.01347 > 0.0001:
#                 upper = ini_vol
#             elif f1 / f2 - 0.01347 < -0.0001:
#                 lower = ini_vol
#             else:
#                 break
#         df.iloc[i][j] = K
#         df.iloc[i][j + 1] = ini_vol
# 
# 
# df[['10 Delta Put', 'Unnamed: 1', '25 Delta Put', 'Unnamed: 3', '50 Delta',
#     'Unnamed: 5', '25 Delta Call', 'Unnamed: 7', '10 Delta Call', 'Unnamed: 9']].to_csv('lowerbound.csv')
# 
# 
# =============================================================================















