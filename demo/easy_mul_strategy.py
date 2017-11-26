#coding=utf-8
#author=godpgf

import backtrader as bt
import numpy as np
import pandas as pd
import datetime
import talib as ta

class AnnualizedStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.simulate.datas[0].date[0]
        print('%s, %s' % (dt, txt))

    @classmethod
    def choose_stocks(cls, codes, base_info):
        #找到市值最小的股票
        market_value = []
        code_value = []
        for i in range(len(codes)):
            bi = base_info(codes[i][0])
            if bi is not None and bi.loc['timeToMarket'] > 0 and "S" not in bi.loc['name']:
                date = datetime.datetime.strptime("%d"%bi.loc['timeToMarket'],"%Y%m%d")
                #选择上市百日的股票
                if int((datetime.datetime.now()-date).days) > 100:
                    market_value.append(bi.loc['totals'] * codes[i][1])
                    code_value.append(codes[i][0])
        market_value = np.array(market_value)
        sort_index = np.argsort(market_value)
        #return np.array([code_value[sort_index[j]] for j in range(len(market_value)-100,len(market_value))])
        return np.array([code_value[sort_index[j]] for j in range(100)])

    def __init__(self, simulate):
        bt.Strategy.__init__(self,simulate)
        for data in simulate.datas:
            data.order = None


    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f %.2f' % (self.datas[0].close[-1], self.tj1[0][0]))
        for data in self.simulate.datas:
            if self.is_training(data) == False:
                continue

            #卖出(确保当前没有跌停)
            if data.order and data.date.offset >= data.order.offset + 5:
                if self.sell(data):
                    data.order = None


            #买入(确保当前没有涨停)
            if self.getcash() > 10000.0 and data.order is None and data.close[0] < data.close[-1] and data.close[-1] < data.close[-2]:
                data.order = self.buy(data,10000.0//data.close[0])


def get_annualized_returns(dataframes):
    cerebro = bt.Simulator()
    #cerebro.addsizer(AnnualizedSizer, perc=1)
    cerebro.addstrategy(AnnualizedStrategy)
    for dataframe in dataframes:
        cerebro.adddata(dataframe)
    cerebro.setcash(100000.0)
    cerebro.run()
    #cerebro.plot()
    rate = np.array(cerebro.statistics.cash)
    rate = (rate - rate[0])/rate[0]
    return pd.DataFrame(rate,np.array(cerebro.statistics.date),columns=["rate"])

if __name__ == "__main__" :
    from stquant.data_adapt.DB import DB
    from stquant.benchmark import get_benchmark_returns
    from stquant.plot.quant_plot import QuantPlot
    db = DB("test",True)
    sts = AnnualizedStrategy.choose_stocks(db.get_codes(),db.get_base_info)
    ds = []
    for st in sts:
        data = db.get_all_data(st)
        if data is not None:
            ds.append(data)
    comp_data = db.get_all_data()

    br = get_benchmark_returns(comp_data)
    ar = get_annualized_returns(ds)
    QuantPlot.show_quant_result('easy_strategy', br['rate'], ar['rate'])
    print(sts)
