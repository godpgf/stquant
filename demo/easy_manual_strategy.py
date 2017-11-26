#coding=utf-8
#author=godpgf

import backtrader as bt
import numpy as np
import pandas as pd

if __name__ == '__main__':
    from stquant.data_adapt.DB import DB
    from stquant.benchmark import get_benchmark_returns, get_mul_2_one
    from stquant.plot.quant_plot import QuantPlot
    db = DB("test",True)
    data = db.get_all_data()
    ca = bt.ChargeAccount()
    ca.add_market_data(data)
    ca.add_data('000001',data.copy())
    history_close = [None,None]
    is_init = False
    hold_day = 0
    for index, row in data.iterrows():
        if is_init is False:
            for i in range(len(history_close)):
                if history_close[i] is None:
                    history_close[i] = row['Close']
                    if i == 1:
                        is_init = True
                    break
        else:
            #没有买入
            if hold_day <= 0 and history_close[0] > history_close[1] and history_close[1] > row['Close']:
                ca.add_charge(np.datetime64(index),'000001',200, True)
                hold_day = 5
            elif hold_day > 0:
                hold_day -= 1
                if hold_day == 0:
                    ca.add_charge(np.datetime64(index),'000001',-200, True)
            history_close[0] = history_close[1]
            history_close[1] = row['Close']
    br, ar = ca.back_trade()
    QuantPlot.show_quant_result('easy_strategy', br['rate'], ar['rate'])