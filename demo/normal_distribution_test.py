#coding=utf-8
#author=godpgf
import sys

import tushare as ts
import pandas as pd
import numpy as np
import statsmodels.api as sm #统计运算
import scipy.stats as scs #科学计算
import matplotlib.pyplot as plt #绘图

#读出数据-------------------------------------------------------------------------------------
stock = ['002697', '600783', '600848', '601588']

def get_stock_data(code, start='2015-01-01',end='2015-12-31'):
    st = ts.get_hist_data(code,start=start,end=end)
    st = st['close']
    st.name = code
    return st

d=pd.DataFrame([get_stock_data(st) for st in stock])
##转置
data=d.T
print data.head()

#比较一下机制股票的情况。规范起点为100.
#(data/data.ix[0]*100).plot(figsize = (8,6))

#计算回报率,用log方便相加-----------------------------------------------
log_returns = np.log(data/data.shift(1))
print log_returns.head()
#绘制回报分布图
#log_returns.hist(bins = 50, figsize = (9,6))

#定义print_statistics函数，为了更加易于理解的方式
#输出给定(历史或者模拟)数据集均值、偏斜度或者峰度等统计数字
def print_statistics(array):
    sta = scs.describe(array)
    print '%14s %15s' %('statistic','value')
    print 30*'-'
    print '%14s %15d' %('size', sta[0])
    print '%14s %15.5f' %('min', sta[1][0])
    print '%14s %15.5f' %('max', sta[1][1])
    print '%14s %15.5f' %('mean', sta[2])
    print '%14s %15.5f' %('std', np.sqrt(sta[3]))
    print '%14s %15.5f' %('skew', sta[4])
    print '%14s %15.5f' %('kurtosis', sta[5])

for st in stock:
    print '\nResults for stock %s' %st
    print 30*'-'
    log_data = np.array(log_returns[st].dropna())
    print_statistics(log_data)
#分位数-分位数图
#sm.qqplot(log_returns['002697'].dropna(),line = 's')
#plt.grid(True)
#plt.xlabel('theoretical quantiles')
#plt.ylabel('sample quantiles')

def normality_test(array):
    '''
    对给定的数据集进行正态性检验
    组合了3中统计学测试
    偏度测试（Skewtest）——足够接近0
    峰度测试（Kurtosistest)——足够接近0
    正态性测试
    '''
    print 'Skew of data set %15.3f' % scs.skew(array)
    print 'Skew test p-value %14.3f' % scs.skewtest(array)[1]
    print 'Kurt of data set %15.3f' % scs.kurtosis(array)
    print 'Kurt test p-value %14.3f' % scs.kurtosistest(array)[1]
    print 'Norm test p-value %14.3f' % scs.normaltest(array)[1]

for st in stock:
    print '\nResults for st %s' %st
    print 32*'-'
    log_data = np.array(log_returns[st].dropna())
    normality_test(log_data)
#从上述测试的p值来看，否定了数据集呈正态分布的测试假设。 这说明，股票市场收益率的正态假设不成立。

""""
##回报率
returns = np.log(data / data.shift(1))
##年化收益率
print returns.mean()*252
##计算协方差矩阵
print returns.cov()*252

##计算股票个数
noa=len(data.T)

##随机生成初始化权重
weights = np.random.random(noa)
##计算百分比
weights /= np.sum(weights)
weights


##下面通过一次蒙特卡洛模拟，产生大量随机的权重向量，并记录随机组合的预期收益和方差。
port_returns = []

port_variance = []

for p in range(4000):
    weights = np.random.random(noa)
    weights /=np.sum(weights)
    port_returns.append(np.sum(returns.mean()*252*weights))
    port_variance.append(np.sqrt(np.dot(weights.T, np.dot(returns.cov()*252, weights))))
##因为要开更号，所以乘两次weight
##dot就是点乘 
port_returns = np.array(port_returns)
port_variance = np.array(port_variance)

#无风险利率设定为4%
risk_free = 0.04
plt.figure(figsize = (8,4))
plt.scatter(port_variance, port_returns, c=(port_returns-risk_free)/port_variance, marker = 'o')
plt.grid(True)
plt.xlabel('excepted volatility')
plt.ylabel('expected return')
plt.colorbar(label = 'Sharpe ratio')

##投资组合优化1——sharpe最大

def statistics(weights):
    weights = np.array(weights)
    port_returns = np.sum(returns.mean()*weights)*252
    port_variance = np.sqrt(np.dot(weights.T, np.dot(returns.cov()*252,weights)))
    return np.array([port_returns, port_variance, port_returns/port_variance])

#最优化投资组合的推导是一个约束最优化问题
import scipy.optimize as sco


#最小化夏普指数的负值
def min_sharpe(weights):
    return -statistics(weights)[2]

#约束是所有参数(权重)的总和为1。这可以用minimize函数的约定表达如下
cons = ({'type':'eq', 'fun':lambda x: np.sum(x)-1})

#我们还将参数值(权重)限制在0和1之间。这些值以多个元组组成的一个元组形式提供给最小化函数
bnds = tuple((0,1) for x in range(noa))


opts = sco.minimize(min_sharpe, noa*[1./noa,], method = 'SLSQP', bounds = bnds, constraints = cons)

opts


##sharpe最大的组合3个统计数据分别为：


#预期收益率、预期波动率、最优夏普指数

statistics(opts['x']).round(3)


##通过方差最小来选出最优投资组合。


def min_variance(weights):
    return statistics(weights)[1]
optv = sco.minimize(min_variance, noa*[1./noa,],method = 'SLSQP', bounds = bnds, constraints = cons)

optv

##方差最小的最优组合权重向量及组合的统计数据分别为：
optv['x'].round(3)

#得到的预期收益率、波动率和夏普指数
statistics(optv['x']).round(3)
"""