#coding=utf-8
#author=godpgf

import pandas as pd
import datetime
import backtrader as bt
import numpy as np
from stdb import *



class DB(object):


    def __init__(self, cache_path=None, is_offline=False):
        self.dataProxy = LocalDataProxy(cache_path, is_offline)
        self.codeProxy = LocalCodeProxy(cache_path, is_offline)
        self.fundamentalProxy = LocalFundamentalProxy(cache_path, is_offline)

    def get_all_data(self, order_book_id = '0000001', fromdate = pd.Timestamp('2015-05-05'), todate = pd.Timestamp('2016-05-05')):
        bars = None

        if len(order_book_id) > 7:
            #获取行业数据
            choose = []
            codes = self.get_codes()
            for code in codes:
                bi = self.get_base_info(code[0])
                if bi is not None and bi.loc['industry'] == order_book_id:
                    data = self.get_all_data(code[0], fromdate, todate)
                    if data is not None:
                        data.totals = bi.loc['totals']
                        data.code = code[0]
                        choose.append(data)
            return choose
        else:
            bars = self.dataProxy.get_table(order_book_id)
        if bars.index[0] > todate or bars.index[-1] < fromdate:
            return None
        return bars[(bars.index >= fromdate) & (bars.index <= todate)]

    def get_codes(self):
        return self.codeProxy.get_codes()

    def get_base_info(self, code_id):
        return self.fundamentalProxy.base_info(code_id)

