#coding=utf-8
#author=godpgf

import backtrader as bt
import numpy as np
import pandas as pd

class Mul2OneStrategy(bt.Strategy):
    def __init__(self, simulate):
        bt.Strategy.__init__(self,simulate)
        simulate.statistics.index = []
        simulate.statistics.data = []
        simulate.statistics.last_close = 100

    def next(self):
        self.simulate.statistics.index.append(self.simulate.date)
        cup = 0

        #收盘涨幅
        close_rise = 0
        open_rise = 0
        high_rise = 0
        low_rise = 0
        volume = 0
        vwap = 0
        for data in self.simulate.datas:
            if self.is_training(data):
                dcup = data.close[0] * data.totals
                dr = data.rise[0] * dcup
                close_rise += dr
                open_rise += dr * data.open[0] / data.close[0]
                high_rise += dr * data.high[0] / data.close[0]
                low_rise += dr * data.low[0] / data.close[0]
                volume += data.volume[0]
                vwap += data.vwap[0]
                cup += dcup
        close_rise /= (cup * len(self.simulate.datas))
        open_rise /= (cup * len(self.simulate.datas))
        high_rise /= (cup * len(self.simulate.datas))
        low_rise /= (cup * len(self.simulate.datas))

        last_close = self.simulate.statistics.last_close
        data = [last_close*(1+open_rise), last_close*(1+high_rise), last_close*(1+low_rise), last_close*(1+close_rise),volume,vwap,close_rise]
        self.simulate.statistics.last_close = last_close*(1+close_rise)
        self.simulate.statistics.data.append(data)
        #index = [pd.Timestamp(int2date(data / 1000000)) for data in date_col]
        #data = [[bars["open"][i],bars["high"][i],bars["low"][i],bars["close"][i],bars["volume"][i],bars["vwap"][i],bars["rise"][i]] for i in range(len(index))]
        #return pd.DataFrame(np.array(data),index,columns=["Open","High","Low","Close","Volume","Vwap","Rise"])

def get_mul_2_one(dataframes):
    cerebro = bt.Simulator()
    #cerebro.addsizer(AnnualizedSizer, perc=1)
    cerebro.addstrategy(Mul2OneStrategy)
    for dataframe in dataframes:
        cerebro.adddata(dataframe)
    cerebro.run()
    return pd.DataFrame(np.array(cerebro.statistics.data),cerebro.statistics.index,columns=["Open","High","Low","Close","Volume","Vwap","Rise"])