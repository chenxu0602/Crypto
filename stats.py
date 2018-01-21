
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from data import loadDailyOpen, loadDailyHigh, loadDailyLow, loadDailyClose, loadDailyVolume, loadDailyMktCap, loadDailyField
from factors import crrank, universe, calcSD
from signals import cross_price_momentum, cross_price_momentum_adjust_by_vol


class Port:
    def __init__(self, sig, pri, w, slip):
        self.signal = sig
        self.price  = pri
        self.ret    = np.log(self.price).diff(1)
        self.weight = w
        self.position = self.signal.shift(1)
        self.nPosition = self.position.count(axis=1)
        self.nLongPosition  = self.position[self.position > 0].count(axis=1)
        self.nShortPosition = self.position[self.position < 0].count(axis=1)

        self.rawPnL = self.ret.mul(self.position)
        self.slip   = self.position.diff().abs() * slip / 1e4
        self.PnL    = self.rawPnL - self.slip

        self.wPosition = self.weight.mul(self.position)
        self.wRawPnL   = self.ret.mul(self.wPosition)
        self.wSlip     = self.wPosition.diff().abs() * slip / 1e4
        self.wPnL      = self.wRawPnL - self.wSlip

        self.annualizedRet = self.PnL.mean() * 252.
        self.annualizedStd = self.PnL.std() * 16.
        self.annaulizedSharpe = self.annualizedRet.div(self.annualizedStd)

        self.portPosition = self.wPosition.sum(axis=1)
        self.portRawPnL   = self.wRawPnL.sum(axis=1)
        self.portSlip     = self.wSlip.sum(axis=1)
        self.portPnL      = self.wPnL.sum(axis=1)

        self.annualizedPortRet = self.portPnL.mean() * 252.
        self.annualizedPortStd = self.portPnL.std() * 16.
        self.annualizedPortSharpe = self.annualizedPortRet / self.annualizedPortStd

    def __str__():
        pass




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

    mktCapMom5D  = cross_price_momentum(univ, dailyMktCap, 3)
    mktCapMom10D = cross_price_momentum(univ, dailyMktCap, 10)
    mktCapMom15D = cross_price_momentum(univ, dailyMktCap, 15)
    mktCapMom25D = cross_price_momentum(univ, dailyMktCap, 25)

    adjMktCapMom3D  = cross_price_momentum_adjust_by_vol(univ, dailyClose, atr, 3)
    adjMktCapMom10D = cross_price_momentum_adjust_by_vol(univ, dailyClose, atr, 10)
    adjMktCapMom15D = cross_price_momentum_adjust_by_vol(univ, dailyClose, atr, 15)
    adjMktCapMom25D = cross_price_momentum_adjust_by_vol(univ, dailyClose, atr, 25)

    signal = pd.DataFrame(index=adjMktCapMom3D.index, columns=adjMktCapMom3D.columns)

    signal[adjMktCapMom3D > 0.5] = -1.0
    signal[adjMktCapMom3D <= 0.5] = 1.0

    signal[(signal > -1.0) & (signal < 1.0)] = 0.0

    equalWeight = pd.DataFrame(index=signal.index, columns=signal.columns)
    count = signal.count(axis=1)
    for idx in count.index:
        c = count[idx]
        if not pd.isnull(c) and c > 0:
            equalWeight.loc[idx, :] = 1.0 / c

    atrWeight = 0.01 / atr

    stats = Port(signal, dailyClose, equalWeight, 10)