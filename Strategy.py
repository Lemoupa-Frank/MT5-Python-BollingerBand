import math
import time

import MetaTrader5 as mt5
import pandas as pd

SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M1
Tradevolume = 0.01
Deviation = 5 
Magic = 10 #automated trade identify helps identify which took what trade
SMA_PERIOD = 20 #simple moving average 
STANDARD_DEV = 2 #Bollinger Band Deviation
close = "close"
open = "open"
TP = 2
SL = 2


def market_order(symbol, volume, order_type, deviation, magic, sl, tp):
    tick = mt5.symbol_info_tick(symbol)
    order_dic = {"buy": 0, "sell": 1}
    price_dic = {"buy": tick.ask, "sell": tick.bid}
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dic[order_type],
        "price": price_dic[order_type],
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": magic,  # unique order identifier
        "connect": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,  # validity of order
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    order = mt5.order_send(request)
    print(order)

    return order


def get_signal():
    # obtaining data of last 20 bars
    bars = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 1, SMA_PERIOD)
    candle = mt5.symbol_info_tick(SYMBOL)
    candle_buy = candle.bid
    candle_sell = candle.ask

    df = pd.DataFrame(bars)

    sma = df["close"].mean()
    # calculate standard deviation
    sd = df["close"].std()
    # calculate lower band
    lb = sma - STANDARD_DEV * sd
    # calculate upper band
    ub = sma + STANDARD_DEV * sd
    # getting info about last row
    last_close = df.iloc[-1]["close"]

    print(last_close)
    if TIMEFRAME == 16388:
        floor = lb - 0.00100
        top = ub + 0.00100
    if TIMEFRAME == 1:
        floor = lb - 0.00020
        top = ub + 0.00020
    if (last_close < lb) or math.isclose(candle_buy, floor):
        return "buy", sma, lb, ub
    elif (last_close > ub) or math.isclose(candle_sell, top):
        return "sell", sma, lb, ub
    else:
        return [None, None, None, None]

        # connect to platform


if not mt5.initialize(login=5005468062, server="MetaQuotes-Demo", password="1tlbstiz", timeout=20000):
    print("initialize() failed")
    mt5.shutdown()
else:
    print("connected")

while True:
    signal, sma, lb, ub = get_signal()

    tick = mt5.symbol_info_tick(SYMBOL)

    print(tick.bid)
    print(SYMBOL)
    if signal == "buy":
        print(signal, sma)
        market_order(SYMBOL, Tradevolume, "buy", Deviation, 10, (lb - (sma - lb) * 1.92 / 3), sma + 0.00005)
        print("Buy Done ")
        time.sleep(180)

    elif signal == "sell":
        print(signal, sma)
        market_order(SYMBOL, Tradevolume, "sell", Deviation, 10, (ub + (ub - sma) * 1.92 / 3), sma - 0.00005)
        print("Buy Done")
        if time.sleep(180):
            a = 3
    else:
        print(signal, sma)

    # check for signal every 10second
    time.sleep(10)
