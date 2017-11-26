#coding=utf-8
#author=godpgf

import backtrader as bt
import numpy as np
import pandas as pd


class AnnualizedStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.simulate.datas[0].date[0]
        print('%s, %s' % (dt, txt))

    def __init__(self, simulate):
        bt.Strategy.__init__(self,simulate)
        # 使用收盘作为数据
        self.dataclose = self.simulate.datas[0].close



    def next(self):
        # 模拟器每一天都会调用这个函数
        self.log('Close, %.2f' % self.dataclose[0])

        # 如果当前订单数量是0，表示没有买入任何股票
        if len(self.simulate.orders) == 0:

            # 今天的股价小于昨天
            if self.dataclose[0] < self.dataclose[-1]:
                    # 昨天的股价小于前天

                    if self.dataclose[-1] < self.dataclose[-2]:
                        # 买入股票
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])
                        self.buy()
                        #买入股票池中第二只股票，100股
                        #self.buy(self.datas[1], 100)


        else:

            # 如果持有某只股票超过5天
            if self.simulate.datas[0].date.offset >= (self.simulate.orders[0].offset + 5):
                # 卖出股票
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.sell()
                # 买入股票池中第二只股票，50股
                #self.sell(self.simulate.datas[1],50)

def get_annualized_returns(dataframe):
    cerebro = bt.Simulator()
    cerebro.addstrategy(AnnualizedStrategy)
    cerebro.adddata(dataframe)
    cerebro.setcash(100000.0)
    cerebro.run()
    #cerebro.plot()
    rate = np.array(cerebro.statistics.cash)
    rate = (rate - rate[0])/rate[0]
    return pd.DataFrame(rate,np.array(cerebro.statistics.date),columns=["rate"])

if __name__ == '__main__':
    from stquant.data_adapt.DB import DB
    from stquant.benchmark import get_benchmark_returns, get_mul_2_one
    from stquant.plot.quant_plot import QuantPlot
    db = DB("test",True)
    data = db.get_all_data()

    #br = get_benchmark_returns(get_mul_2_one(db.get_all_data('房产服务')))

    br = get_benchmark_returns(data)
    ar = get_annualized_returns(data)
    QuantPlot.show_quant_result('easy_strategy', br['rate'], ar['rate'])
