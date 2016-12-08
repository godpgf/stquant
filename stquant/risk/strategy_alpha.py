#coding=utf-8
#author=godpgf

import numpy as np

class StrategyAlpha(object):
    TRADING_DAYS_A_YEAR = 250
    def __init__(self,total_ar, total_br):
        self.total_ar = total_ar
        self.total_br = total_br
        self.daily_ar = StrategyAlpha.cal_daily_returns(total_ar)
        self.daily_br = StrategyAlpha.cal_daily_returns(total_br)
        self.volability = StrategyAlpha.cal_volability(self.daily_ar)

    """
    计算日收益率
    """
    @staticmethod
    def cal_daily_returns(total_rate):
        daily_rate = total_rate.copy()
        daily_rate[1:len(daily_rate)] = total_rate[1:len(total_rate)] - total_rate[0:len(total_rate)-1]
        return daily_rate

    """
    波动率
    """
    @staticmethod
    def cal_volability(daily_returns):
        #return np.var(daily_returns)
        return np.std(daily_returns)

    """
    年化收益率。表示投资期限为一年的预期收益率。具体计算方式为 (策略最终价值 / 策略初始价值 - 1) / 回测交易日数量 × 250
    """
    @staticmethod
    def cal_year_returns(total_r):
        fff = total_r[-1] / len(total_r) * StrategyAlpha.TRADING_DAYS_A_YEAR
        return total_r[-1] / len(total_r) * StrategyAlpha.TRADING_DAYS_A_YEAR

    """
    阿尔法。具体计算方式为 (策略年化收益 - 无风险收益) - beta × (参考标准年化收益 - 无风险收益)，这里的无风险收益指的是中国固定利率国债收益率曲线上10年期国债的年化到期收益率。
    """
    def cal_alpha(self, beta = 1, interest = 0.05):
        return (StrategyAlpha.cal_year_returns(self.total_ar) - interest) - beta * (StrategyAlpha.cal_year_returns(self.total_br) - interest)



    """
    贝塔。具体计算方法为 策略每日收益与参考标准每日收益的协方差 / 参考标准每日收益的方差 。
    """
    def cal_beta(self):
        cov = np.cov(np.vstack([
            self.daily_ar,
            self.daily_br,
        ]), ddof=1)
        return cov[0][1] / cov[1][1]

    """
    夏普比率。表示每承受一单位总风险，会产生多少的超额报酬。具体计算方法为 (策略年化收益率 - 回测起始交易日的无风险利率) / 策略收益波动率 。
    """
    def cal_sharpe_ratio(self, interest = 0.05):
        return (StrategyAlpha.cal_year_returns(self.total_ar) - interest) / self.volability

    """
    信息比率。衡量超额风险带来的超额收益。具体计算方法为 (策略每日收益 - 参考标准每日收益)的年化均值 / 年化标准差 。
    """
    def cal_information_rate(self):
        return (np.mean(self.daily_ar) / len(self.daily_ar) - np.mean(self.daily_br) / len(self.daily_br))*250/ self.volability

    """
    最大回撤。描述策略可能出现的最糟糕的情况。具体计算方法为 max(1 - 策略当日价值 / 当日之前虚拟账户最高价值)
    """
    def cal_max_drawdown(self):
        max_ar = self.total_ar[0]
        max_drawdown = 0
        for i in range(1,len(self.total_ar)):
            max_drawdown = max(max_ar-self.total_ar[i],max_drawdown)
            max_ar = max(self.total_ar[i],max_ar)
        return max_drawdown