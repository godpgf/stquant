#coding=utf-8
#author=godpgf
import numpy as np
import math
from scipy.stats import pearsonr

class Alpha(object):

    @classmethod
    def op_add(cls, d1, d2):
        return d1 + d2

    @classmethod
    def op_reduce(cls, d1, d2):
        return d1 - d2

    @classmethod
    def op_mul(cls, d1, d2):
        return d1 * d2

    @classmethod
    def op_div(cls, d1, d2):
        return d1 / d2

    @classmethod
    def op_eq(cls, d1, d2):
        return d1 == d2

    @classmethod
    def op_or(cls, d1, d2):
        return d1 | d2

    @classmethod
    def op_and(cls, d1, d2):
        return d1 & d2

    @classmethod
    def op_if_else(cls, condition, d1, d2):
        return np.array([d1[i] if condition[i] else d2[i] for i in range(len(condition))])


    @classmethod
    def abs(cls, x):
        return np.abs(x)

    @classmethod
    def log(cls, x):
        return np.log(x)

    @classmethod
    def sign(cls, x):
        return np.sign(x)

    #返回数据的升序排名,归一化
    @classmethod
    def rank(cls, x):
        return x.argsort()/len(x)

    @classmethod
    def delay(cls, x, d):
        y = x.copy()
        y[d:len(x)] = x[0:len(x)-d]
        y[0:d] = x[len(x)-d:len(x)]
        return y

    @classmethod
    def correlation(cls, x, y, d):
        z = []
        for i in len(x):
            if i < d - 1:
                z.append(None)
            else:
                z.append(pearsonr(x[i+1-d:i+1], y[i+1-d:i+1]))
        return np.array(z)

    @classmethod
    def covariance(cls, x, y, d):
        z = []
        for i in len(x):
            if i < d - 1:
                z.append(None)
            else:
                z.append(np.cov(x[i+1-d:i+1], y[i+1-d:i+1]))
        return np.array(z)

    @classmethod
    def scale(cls, x, a = 1):
        m = np.max(np.abs(x))
        return x * (a / m)

    @classmethod
    def delta(x, d):
        y = x.copy()
        y[0:d] -= x[len(x)-d:len(x)]
        y[d:len(x)] -= x[0:len(x)-d]
        return y

    @classmethod
    def signedpower(cls, x, a):
        return x ** a

    @classmethod
    def decay_linear(cls, x, d):
        #w = (d + 1) * d * 0.5
        y = [0.0 for i in range(len(x))]
        for j in range(len(y)):
            for i in range(0,d):
                if j >= d - 1:
                    y[j] += x[j-i] * (d - i)
                else:
                    y[j] += x[j-i] * (j - i + 1)
            if j >= d - 1:
                y[j] /= (d + 1) * d * 0.5
            else:
                y[j] /= (j + 1 + 1) * (j + 1) * 0.5
        return np.array(y)

    @classmethod
    def ts_min(cls, x, d):
        y = x.copy()
        for i in range(1,d):
            for j in range(len(y)):
                if j >= i:
                    y[j] = min(y[j], x[j-i])
        return y

    @classmethod
    def ts_max(cls, x, d):
        y = x.copy()
        for i in range(1,d):
            for j in range(len(y)):
                if j >= i:
                    y[j] = max(y[j], x[j-i])
        return y

    @classmethod
    def ts_argmin(cls, x, d):
        y = range(len(x))
        for i in range(1,d):
            for j in range(len(y)):
                if j >= i and x[y[i]] > x[j-i]:
                    y[j] = j-i
        for i in range(len(y)):
            y[i] = i - y[i]
        return np.array(y)

    @classmethod
    def ts_argmax(cls, x, d):
        y = range(len(x))
        for i in range(1,d):
            for j in range(len(y)):
                if j >= i and x[y[i]] < x[j-i]:
                    y[j] = j-i
        for i in range(len(y)):
            y[i] = i - y[i]
        return np.array(y)

    @classmethod
    def ts_rank(cls, x, d):
        y = [0 for i in range(len(x))]
        for i in range(1,d):
            for j in range(len(y)):
                if j >= i and x[j] < x[j-i]:
                    y[i] += 1

    @classmethod
    def sum(cls, x, d):
        y = x.copy()
        for i in range(1,d):
            for j in range(len(y)):
                if j >= i:
                    y[j] += x[j-i]
        return y

    @classmethod
    def product(cls, x, d):
        y = x.copy()
        for i in range(1,d):
            for j in range(len(y)):
                if j >= i:
                    y[j] *= x[j-i]
        return y

    @classmethod
    def stddev(cls, x, d):
        #均值
        y = cls.sum(x, d)
        for i in range(len(y)):
            if i < d:
                y[i] /= i
            else:
                y[i] /= d
        z = [0 for i in range(len(x))]
        #标准差
        for i in range(0,d):
            for j in range(len(y)):
                if j >= i:
                    z[j] += (x[j-i] - y[j]) ** 2
        for i in range(len(y)):
            if i < d:
                z[i] = math.sqrt( z[i] / i )
            else:
                z[i] = math.sqrt( z[i] / d )
        return np.array(z)

    #收益率
    @classmethod
    def returnrate(cls, x, d):
        y = cls.delay(x, d)
        return (x - y) / y

    #针对行业g取样x
    @classmethod
    def indneutralize(x, g):
        #TODO
        pass
