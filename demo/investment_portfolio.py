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
stock = ['000413', '000063', '002007', '000001', '000002']

def get_stock_data(code, start='2015-01-01',end='2015-12-31'):
    st = ts.get_hist_data(code,start=start,end=end)
    st = st['close']
    st.name = code
    return st

d=pd.DataFrame([get_stock_data(st) for st in stock])
##转置
data=d.T

#规范化后时序数据
#(data/data.ix[0]*100).plot(figsize = (8,5))

#计算年化收益和协方差---------------------------------------------
returns = np.log(data / data.shift(1))
print returns
print returns.mean()*252
print returns.cov()*252

#给不同资产随机分配初始权重-----------------------------------------
noa=len(returns.T)
weights = np.random.random(noa)
weights /= np.sum(weights)
print weights

#计算预期组合年化收益、组合方差和组合标准差--------------------------
print np.sum(returns.mean()*weights)*252
print np.dot(weights.T, np.dot(returns.cov()*252,weights))
print np.sqrt(np.dot(weights.T, np.dot(returns.cov()* 252,weights)))

#用蒙特卡洛模拟产生大量随机组合----------------------------------------
port_returns = []
port_variance = []
for p in range(4000):
    weights = np.random.random(noa)
    weights /=np.sum(weights)
    port_returns.append(np.sum(returns.mean()*252*weights))
    port_variance.append(np.sqrt(np.dot(weights.T, np.dot(returns.cov()*252, weights))))

port_returns = np.array(port_returns)
port_variance = np.array(port_variance)

#无风险利率设定为4%
#risk_free = 0.04
#plt.figure(figsize = (8,4))
#plt.scatter(port_variance, port_returns, c=(port_returns-risk_free)/port_variance, marker = 'o')
#plt.grid(True)
#plt.xlabel('excepted volatility')
#plt.ylabel('expected return')
#plt.colorbar(label = 'Sharpe ratio')

#投资组合优化1——sharpe最大------------------------------------------------------------------
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

#优化函数调用中忽略的唯一输入是起始参数列表(对权重的初始猜测)。我们简单的使用平均分布。
opts = sco.minimize(min_sharpe, noa*[1./noa,], method = 'SLSQP', bounds = bnds, constraints = cons)
print opts
#到的最优组合权重向量为：
print opts['x'].round(3)

#预期收益率、预期波动率、最优夏普指数
statistics(opts['x']).round(3)


#投资组合优化2——方差最小----------------------------------------------------------------------------------
def min_variance(weights):
    return statistics(weights)[1]

optv = sco.minimize(min_variance, noa*[1./noa,],method = 'SLSQP', bounds = bnds, constraints = cons)
print optv
#方差最小的最优组合权重向量及组合的统计数据分别为
print optv['x'].round(3)

#得到的预期收益率、波动率和夏普指数
statistics(optv['x']).round(3)
#组合的有效前沿------------------------------------------------------------------------------------------

#在不同目标收益率水平（target_returns）循环时，最小化的一个约束条件会变化。
target_returns = np.linspace(0.0,0.5,50)
target_variance = []
for tar in target_returns:
    cons = ({'type':'eq','fun':lambda x:statistics(x)[0]-tar},{'type':'eq','fun':lambda x:np.sum(x)-1})
    res = sco.minimize(min_variance, noa*[1./noa,],method = 'SLSQP', bounds = bnds, constraints = cons)
    target_variance.append(res['fun'])

target_variance = np.array(target_variance)

#下面是最优化结果的展示----------------------------------------------------------------------
#画图有个报错，用命令：defaults write org.python.python ApplePersistenceIgnoreState NO

plt.figure(figsize = (8,4))
#圆圈：蒙特卡洛随机产生的组合分布
plt.scatter(port_variance, port_returns, c = port_returns/port_variance,marker = 'o')
#叉号：有效前沿
plt.scatter(target_variance,target_returns, c = target_returns/target_variance, marker = 'x')
#红星：标记最高sharpe组合
plt.plot(statistics(opts['x'])[1], statistics(opts['x'])[0], 'r*', markersize = 15.0)
#黄星：标记最小方差组合
plt.plot(statistics(optv['x'])[1], statistics(optv['x'])[0], 'y*', markersize = 15.0)
plt.grid(True)
plt.xlabel('expected volatility')
plt.ylabel('expected return')
plt.colorbar(label = 'Sharpe ratio')

print "finish"