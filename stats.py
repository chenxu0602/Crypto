
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from data import loadDailyOpen, loadDailyHigh, loadDailyLow, loadDailyClose, loadDailyVolume, loadDailyMktCap, loadDailyField
from factors import crrank, universe, calcSD
from signals import cross_price_momentum, cross_price_momentum_adjust_by_vol


class Port:
    def __init__(self, name, sig, pri, w, slip):
        self.name   = name
        self.signal = sig
        self.price  = pri
        self.ret    = np.log(self.price).diff(1)
        self.weight = w
        self.position = self.signal.fillna(0).shift(1)
        self.tvr = self.position.diff().abs().mean()
        self.nPosition = self.position.count(axis=1)
        self.nLongPosition  = self.position[self.position > 0].count(axis=1)
        self.nShortPosition = self.position[self.position < 0].count(axis=1)

        self.rawPnL = self.ret.mul(self.position.shift(1))
        self.slip   = self.position.diff().abs() * slip / 1e4
        self.PnL    = self.rawPnL - self.slip

        self.wPosition = self.weight.mul(self.position)
        self.wRawPnL   = self.ret.mul(self.wPosition)
        self.wSlip     = self.wPosition.diff().abs() * slip / 1e4
        self.wPnL      = self.wRawPnL - self.wSlip

        self.annualizedRet = self.PnL.mean() * 252.
        self.annualizedStd = self.PnL.std() * 16.
        self.annualizedSharpe = self.annualizedRet.div(self.annualizedStd)

        self.portPosition = self.wPosition.sum(axis=1)
        self.portRawPnL   = self.wRawPnL.sum(axis=1)
        self.portSlip     = self.wSlip.sum(axis=1)
        self.portPnL      = self.wPnL.sum(axis=1)
        self.portTVR      = self.wPosition.diff().abs().sum(axis=1).mean()

        self.portLongPosition  = self.wPosition[self.wPosition > 0].sum(axis=1)
        self.portShortPosition = self.wPosition[self.wPosition < 0].sum(axis=1)

        self.annualizedPortRet  = self.portPnL.mean() * 252.
        self.annualizedPortSlip = self.portSlip.mean() * 252.
        self.annualizedPortStd  = self.portPnL.std() * 16.
        self.annualizedPortSharpe = self.annualizedPortRet / self.annualizedPortStd

    def __str__(self):
        s = "\n############################################## Strategy: {0} #####################################".format(self.name)
        s += "\nAnnualized Portfolio Return:         {0:.2f}%".format(self.annualizedPortRet * 100)
        s += "\nAnnualized Portfolio Slip:           {0:.2f}%".format(self.annualizedPortSlip * 100)
        s += "\nAnnualized Portfolio Std:            {0:.2f}%".format(self.annualizedPortStd * 100)
        s += "\nAnnualized Portfolio Sharpe ratio:   {0:.2f}".format(self.annualizedPortSharpe)
        s += "\nAverage number of long  positions:   {0}".format(int(self.nLongPosition.mean()))
        s += "\nAverage number of short positions:   {0}".format(int(self.nShortPosition.mean()))
        s += "\nAverage long  position:              {0:.2f}%".format(self.portLongPosition.mean() * 100)
        s += "\nAverage short position:              {0:.2f}%".format(self.portShortPosition.mean() * 100)
        s += "\nPortfolio Daily Turnover:            {0:.2f}%".format(self.portTVR * 100)

        return s

class IntraPort(Port):
    def __init__(self, name, sig, pri, w, slip):
        super().__init__(name, sig, pri, w, slip)

        self.dailyRawPnL = self.rawPnL.resample("1D", label="right", closed="right").sum()
        self.dailySlip   = self.slip.resample("1D", label="right", closed="right").sum()
        self.dailyPnL    = self.PnL.resample("1D", label="right", closed="right").sum()
        self.dailyTVR    = self.position.diff().abs().resample("1D", label="right", closed="right").sum()

        self.dailyWRawPnL = self.wRawPnL.resample("1D", label="right", closed="right").sum()
        self.dailyWSlip   = self.wSlip.resample("1D", label="right", closed="right").sum()
        self.dailyWPnL    = self.wPnL.resample("1D", label="right", closed="right").sum()

        self.annualizedRet = self.dailyPnL.mean() * 252.
        self.annualizedStd = self.dailyPnL.std() * 16.
        self.annualizedSharpe = self.annualizedRet.div(self.annualizedStd)

        self.portRawPnL = self.portRawPnL.resample("1D", label="right", closed="right").sum()
        self.portSlip   = self.portSlip.resample("1D", label="right", closed="right").sum()
        self.portPnL    = self.portPnL.resample("1D", label="right", closed="right").sum()
        self.portTVR    = self.wPosition.diff().abs().resample("1D", label="right", closed="right").sum().sum(axis=1).mean()

        self.annualizedPortRet  = self.portPnL.mean() * 252.
        self.annualizedPortSlip = self.portSlip.mean() * 252.
        self.annualizedPortStd  = self.portPnL.std() * 16.
        self.annualizedPortSharpe = self.annualizedPortRet / self.annualizedPortStd

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

    priceMom3D   = cross_price_momentum(univ, dailyClose, 3)
    priceMom10D  = cross_price_momentum(univ, dailyClose, 10)
    priceMom15D  = cross_price_momentum(univ, dailyClose, 15)
    priceMom50D  = cross_price_momentum(univ, dailyClose, 50)

    mktCapMom5D  = cross_price_momentum(univ, dailyMktCap, 3)
    mktCapMom10D = cross_price_momentum(univ, dailyMktCap, 10)
    mktCapMom15D = cross_price_momentum(univ, dailyMktCap, 15)
    mktCapMom50D = cross_price_momentum(univ, dailyMktCap, 50)

    adjMktCapMom3D  = cross_price_momentum_adjust_by_vol(univ, dailyClose, atr, 3)
    adjMktCapMom10D = cross_price_momentum_adjust_by_vol(univ, dailyClose, atr, 10)
    adjMktCapMom15D = cross_price_momentum_adjust_by_vol(univ, dailyClose, atr, 15)
    adjMktCapMom90D = cross_price_momentum_adjust_by_vol(univ, dailyClose, atr, 90)

    equalWeight = pd.DataFrame(index=univ.index, columns=univ.columns)
    count = univ[univ].count(axis=1)
    for idx in count.index:
        c = count[idx]
        if not pd.isnull(c) and c > 0:
            equalWeight.loc[idx, :] = 1.0 / c

    atrWeight = 0.01 / atr

    signal = pd.DataFrame(index=adjMktCapMom3D.index, columns=adjMktCapMom3D.columns)
    signal[adjMktCapMom3D > 0.5]  = -1.0
    signal[adjMktCapMom3D <= 0.5] = 1.0
    signal[(signal > -1.0) & (signal < 1.0)] = 0.0

    stats = Port("3-Day Reversion", signal, dailyClose, equalWeight, 10)

    from data import load_minute_ETHEUR
    from data import load_minute_ETHUSD
    from data import load_minute_BTCEUR
    from data import load_minute_BTCUSD
    from data import load_minute_LTCBTC
    from data import load_minute_LTCUSD
    from data import load_minute_LTCEUR
    from data import load_minute_XRPUSD
    from data import minuteOHLC

    btceur = load_minute_BTCEUR()
    btcusd = load_minute_BTCUSD()
    etheur = load_minute_ETHEUR()
    ethusd = load_minute_ETHEUR()
    ltcbtc = load_minute_LTCBTC()
    ltceur = load_minute_LTCEUR()
    ltcusd = load_minute_LTCUSD()
    xrpusd = load_minute_XRPUSD()

    cryptoDict = {
        "BTCEUR" : btceur,
        "BTCUSD" : btcusd,
        "ETHEUR" : etheur,
        "ETHUSD" : ethusd,
        "LTCBTC" : ltcbtc,
        "LTCEUR" : ltceur,
        "LTCUSD" : ltcusd,
        "XRPUSD" : xrpusd
    }

    mdata  = minuteOHLC(cryptoDict)

    def BTC_USD_EUR_ARB(data):
        intraSignal = pd.DataFrame(index=mdata["Close"].index,
            columns=["BTCEUR", "BTCUSD"])
        ratio = mdata["Close"]["BTCEUR"].div(mdata["Close"]["BTCUSD"])
        mv = ratio.ewm(span=120, min_periods=1, adjust=False).mean()
        sd = ratio.ewm(span=120, min_periods=1, adjust=False).std()

        longCondition  = ratio > mv + 2 * sd
        shortCondition = ratio < mv - 2 * sd

        intraSignal.loc[longCondition, "BTCEUR"] = -1.0
        intraSignal.loc[longCondition, "BTCUSD"] = 1.0
        intraSignal.loc[shortCondition, "BTCEUR"] = 1.0
        intraSignal.loc[shortCondition, "BTCUSD"] = -1.0

        intraSignal.fillna(method="ffill", inplace=True)

        return intraSignal.shift(1)

    def BTC_LTC_ARB(data):
        intraSignal = pd.DataFrame(index=mdata["Close"].index,
            columns=["BTCUSD", "LTCUSD"])
        ratio = mdata["Close"]["LTCUSD"].div(mdata["Close"]["BTCUSD"]).div(mdata["Close"]["LTCBTC"])
        mv = ratio.ewm(span=30, min_periods=1, adjust=False).mean()
        sd = ratio.ewm(span=30, min_periods=1, adjust=False).std()

        longCondition  = ratio > mv + 2 * sd
        shortCondition = ratio < mv - 2 * sd

        intraSignal.loc[longCondition, "LTCUSD"] = -1.0
        intraSignal.loc[longCondition, "BTCUSD"] = 1.0
        intraSignal.loc[shortCondition, "LTCUSD"] = 1.0
        intraSignal.loc[shortCondition, "BTCUSD"] = -1.0

        intraSignal.fillna(method="ffill", inplace=True)

        return intraSignal.shift(1)


    btcSignal = BTC_USD_EUR_ARB(mdata)
    btcltcSignal = BTC_LTC_ARB(mdata)

    intraEqualWeight = pd.DataFrame(index=btcSignal.index, 
        columns=btcSignal.columns)
    intraEqualWeight.fillna(1.0 / len(intraEqualWeight.columns), inplace=True)

    intraStats = IntraPort("BTCEUR-BTCUSD", btcSignal, mdata["Close"], intraEqualWeight, 5)
    intraStats2 = IntraPort("BTC-LTC", btcltcSignal, mdata["Close"], intraEqualWeight, 5)

    """
    fig, ax = plt.subplots()
    pd.DataFrame({"Cum PnL (BTC-LTC)": intraStats2.portPnL.cumsum()}).plot(ax=ax, grid=True)
    plt.legend(loc="best")

    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    """

    """
    pd.DataFrame({"Cum PnL (3-Day Reversion)": stats.portPnL.cumsum()}).plot(grid=True)
    plt.legend(loc="best")
    """