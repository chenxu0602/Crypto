
import os, sys, re
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
import numpy as np

#pd.set_option('display.expand_frame_repr', False)

def load_minute_BTCEUR():
    return load_minute_data("Bitstamp_BTCEUR_m.csv")

def load_minute_BTCUSD():
    return load_minute_data("Bitstamp_BTCUSD_m.csv")

def load_minute_ETHEUR():
    return load_minute_data("Bitstamp_ETHEUR_m.csv")

def load_minute_ETHUSD():
    return load_minute_data("Bitstamp_ETHUSD_m.csv")

def load_minute_LTCBTC():
    return load_minute_data("Bitstamp_LTCBTC_m.csv")

def load_minute_LTCEUR():
    return load_minute_data("Bitstamp_LTCEUR_m.csv")

def load_minute_LTCUSD():
    return load_minute_data("Bitstamp_LTCUSD_m.csv")

def load_minute_XRPUSD():
    return load_minute_data("Bitstamp_XRPUSD_m.csv")

def load_minute_data(f):
    print("Loading file {0} ...".format(f))
    parser = lambda date: datetime.strptime(date[:-3], "%Y-%m-%d %H:%M")
    return pd.read_csv(f, parse_dates=[0], index_col=[0], date_parser=parser)

def minuteOHLC(data):
    print("Generating OHLC data ...")
    res = defaultdict(pd.DataFrame)
    for fld in ["Open", "High", "Low", "Close"]:
        resDict = {}
        for sym in sorted(data.keys()):
            resDict[sym] = data[sym][fld]
        res[fld] = pd.DataFrame(resDict)
    res["Ret"] = np.log(res["Close"]).diff()
    return res



def processRawData(fileName="crypto-markets.csv", start="2015-01-01", dump=True):
    if not os.path.exists(fileName):
        print("{0} doesn't exist!".format(fileName))
        return pd.DataFrame()

    print("Pocessing raw data from {0} ...".format(fileName))

    data = pd.read_csv(fileName, parse_dates=["date"])
    data = data[data["date"] >= start]
    data.set_index(["slug", "date"], inplace=True)

    frames = defaultdict(lambda: defaultdict(pd.Series))
    for sym, df in data.groupby(level="slug"):
        print(sym)
        df2 = df.xs(sym, level="slug")

        for fld in data.columns:
            series = df2[fld]
            flt = series.groupby(level=0).filter(lambda x: len(x) > 1)
            if len(flt) > 0: print(sym, flt)
            frames[fld][sym] = series

    results = defaultdict(pd.DataFrame)
    for fld in frames:
        print("Generating dataframe for {0} ...".format(fld))
        results[fld] = pd.DataFrame(frames[fld])

    if dump:
        outputdir = fileName.split('.')[0]
        if not os.path.exists(outputdir):
            print("Creating directory {0} ...".format(outputdir))
            os.system("mkdir -p {0}".format(outputdir))

        for fld in results:
            outputfile = os.path.join(outputdir, "{0}.csv".format(fld))
            print("Generating file {0} ...".format(outputfile))
            results[fld].to_csv(outputfile)

    return results

def loadDailyOpen(directory="crypto-markets"):
    return loadDailyField(directory, "open")

def loadDailyHigh(directory="crypto-markets"):
    return loadDailyField(directory, "high")

def loadDailyLow(directory="crypto-markets"):
    return loadDailyField(directory, "low")

def loadDailyClose(directory="crypto-markets"):
    return loadDailyField(directory, "close")

def loadDailyVolume(directory="crypto-markets"):
    return loadDailyField(directory, "volume")

def loadDailyMktCap(directory="crypto-markets"):
    return loadDailyField(directory, "market")

def loadDailyField(directory, fld):
    if not os.path.exists(directory):
        print("Directory {0} doesn't exist!".format(directory))
        return 

    csvfile = os.path.join(directory, "{0}.csv".format(fld))
    if not os.path.exists(csvfile):
        print("CSV file {0} doesn't exist!".format(csvfile))
        return

    print("Loading {0} data from {1} ...".format(fld, csvfile))
    res = pd.read_csv(csvfile, parse_dates=[0], index_col=[0])
    return res


if __name__ == "__main__":
    pass

    """
    res = processRawData()
    dailyOpen   = loadDailyOpen()
    dailyHigh   = loadDailyHigh()
    dailyLow    = loadDailyLow()
    dailyClose  = loadDailyClose()
    dailyVolume = loadDailyVolume()
    dailyMktCap = loadDailyMktCap()
    """

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