# Crypto

crytocurrency data source: 

    https://www.kaggle.com/jessevent/all-crypto-currencies/data
    http://www.cryptodatadownload.com

Tested strategies:

1) Results/3D_Reversion

    Data:     Daily OHLC, volume and market cap data of about 1400 crypto currencies.

    Universe: Select top 100 in market cap and daily trading volume above 1M USD.

    Strategy: Rank 3-Day risk adjusted returns, long the bottom half and short the top half.

	 Transaction Cost: 10bps.


2) Results/BTCEUR_BTCUSD

    Data:     Minute OHLC of cyptocurrency pairs

    Universe: BTC/EUR and BTC/USD

    Strategy: Volatiltity in EUR/USD is neglegible compared to volatilities of BTC/EUR and BTC/USD,     reversal strategy similar to bollinger band.

	 Transaction Cost: 5bps.

3) Results/BTC_LTC

    Data:     Minute OHLC of cyptocurrency pairs

    Universe: BTC/USD, LTC/USD and BTC/LTC

    Strategy: Reversal strategy about ratio = BTC/USD.div(LTC/USD).div(BTC/LTC)

	 Transaction Cost: 5bps.
