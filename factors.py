
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from data import loadDailyOpen, loadDailyHigh, loadDailyLow, loadDailyClose, loadDailyVolume, loadDailyMktCap

def crrank(data, N=10, pct=False):
    return data.rolling(window=N, min_periods=1).mean().rank(axis=1, na_option="keep", ascending=False, pct=pct)

def calcSD(ret, N=20):
    return ret.rolling(window=N, min_periods=1).std()

def universe(mktrank, vol):
    univ = pd.DataFrame(index=mktrank.index, columns=mktrank.columns)
    univ.fillna(False, inplace=True)
    volume = vol.rolling(window=20, min_periods=1).mean()
    univ[(mktrank <= 100) & (volume > 1000000) & (volume.shift(100) > 0)] = True
    return univ

def calcATR(op, hi, lo, cl):
    print("Calculating ATR ...")
    hl = hi - lo
    hc = (hi - cl.shift(1)).abs()
    lc = (lo - cl.shift(1)).abs()

    tr = pd.DataFrame(index=hl.index)
    for col in hl.columns:
        print(col)
        df = pd.DataFrame({"hl":hl[col], "hc":hc[col], "lc":lc[col]})
        df_max = df.max(axis=1).to_frame(name=col)
        tr = pd.merge(tr, df_max, how="outer", left_index=True, right_index=True)

    atr = tr.ewm(com=14, min_periods=1).mean()

    return atr, atr.div(cl)

def dailyMomentum(data, N=1):
    return np.log(data) - np.log(data.shift(N))

def dump(data, name, directoroy="crypto-markets"):
    if not os.path.exists(directoroy):
        print("Creating directory {0} ...".format(directoroy))
        os.system("mkdir -p {0}".format(directoroy))

    csvfile = os.path.join(directoroy, "{0}.csv".format(name))
    print("Generating file {0} ...".format(csvfile))
    data.to_csv(csvfile)

if __name__ == "__main__":

    dailyOpen   = loadDailyOpen()
    dailyHigh   = loadDailyHigh()
    dailyLow    = loadDailyLow()
    dailyClose  = loadDailyClose()
    dailyVolume = loadDailyVolume()
    dailyMktCap = loadDailyMktCap()

    mktCapRank  = crrank(dailyMktCap)
    volumeRank  = crrank(dailyVolume)

    """
    atr, atr2 = calcATR(dailyOpen, dailyHigh, dailyLow, dailyClose)
    atrRank = crrank(atr2, 10, True)
    dump(atr, "atr")
    dump(atr2, "atr2")
    """

    dailyRet  = np.log(dailyClose) - np.log(dailyClose.shift(1))
    weeklyRet = dailyRet.resample("1W", label="right", closed="right").sum()

    sd = calcSD(dailyRet, 20)
    sdRank = crrank(sd, 10, True)

    univ = universe(mktCapRank, dailyVolume)

    mktCapMom5D = dailyMomentum(dailyMktCap, 5)
    closeMom5D  = dailyMomentum(dailyClose, 5)
