
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from data import loadDailyOpen, loadDailyHigh, loadDailyLow, loadDailyClose, loadDailyVolume, loadDailyMktCap, loadDailyField
from factors import crrank, universe, calcSD

def cross_price_momentum(univ, close, N):
    mom = np.log(close).diff(N)
    mom[~univ] = np.nan
    momRank = crrank(mom, 1, pct=True)
    return momRank

def cross_price_momentum_adjust_by_vol(univ, close, vol, N):
    mom = np.log(close).diff(N).div(vol)
    mom[~univ] = np.nan
    momRank = crrank(mom, 1, pct=True)
    return momRank


if __name__ == "__main__":

    dailyOpen   = loadDailyOpen()
    dailyHigh   = loadDailyHigh()
    dailyLow    = loadDailyLow()
    dailyClose  = loadDailyClose()
    dailyVolume = loadDailyVolume()
    dailyMktCap = loadDailyMktCap()

    atr = loadDailyField("crypto-markets", "atr2")

    mktCapRank  = crrank(dailyMktCap)
    volumeRank  = crrank(dailyVolume)


    univ = universe(mktCapRank, dailyVolume)

    priceMom5D   = cross_price_momentum(univ, dailyClose, 5)
    priceMom10D  = cross_price_momentum(univ, dailyClose, 10)
    priceMom15D  = cross_price_momentum(univ, dailyClose, 15)
    priceMom25D  = cross_price_momentum(univ, dailyClose, 25)

    mktCapMom5D  = cross_price_momentum(univ, dailyMktCap, 5)
    mktCapMom10D = cross_price_momentum(univ, dailyMktCap, 10)
    mktCapMom15D = cross_price_momentum(univ, dailyMktCap, 15)
    mktCapMom25D = cross_price_momentum(univ, dailyMktCap, 25)

    adjMktCapMom5D  = cross_price_momentum_adjust_by_vol(univ, dailyMktCap, atr, 5)
    adjMktCapMom10D = cross_price_momentum_adjust_by_vol(univ, dailyMktCap, atr, 10)
    adjMktCapMom15D = cross_price_momentum_adjust_by_vol(univ, dailyMktCap, atr, 15)
    adjMktCapMom25D = cross_price_momentum_adjust_by_vol(univ, dailyMktCap, atr, 25)