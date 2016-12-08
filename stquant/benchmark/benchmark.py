#coding=utf-8
#author=godpgf

import backtrader as bt
import numpy as np
import pandas as pd


class BenchmarkStrategy(bt.Strategy):
    def __init__(self, simulate):
        bt.Strategy.__init__(self,simulate)
        self.is_buy = False

    def next(self):
        if self.is_buy is False:
            self.is_buy = True
            self.order = self.buy()


def get_benchmark_returns(dataframe):
    cerebro = bt.Simulator()
    cerebro.addstrategy(BenchmarkStrategy)
    cerebro.adddata(dataframe)
    cerebro.setcash(100000.0)
    cerebro.run()
    #cerebro.plot()
    rate = np.array(cerebro.statistics.cash)
    rate = (rate - rate[0])/rate[0]
    return pd.DataFrame(rate,np.array(cerebro.statistics.date),columns=["rate"])