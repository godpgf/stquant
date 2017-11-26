#coding=utf-8
#author=godpgf

import numpy as np
import talib

def get_k(data):
    k = np.zeros(len(data))
    k[1:] = data[1:] - data[0:-1]
    return k

NO_USE_DATA_NUM = 40

def process_index(data_proxy, order_book_id, dt, bar_count, frequency):
    close = data_proxy.history(order_book_id, dt, bar_count+NO_USE_DATA_NUM, frequency, 'close').values
    high = data_proxy.history(order_book_id, dt, bar_count+NO_USE_DATA_NUM, frequency, 'high').values
    low = data_proxy.history(order_book_id, dt, bar_count+NO_USE_DATA_NUM, frequency, 'low').values
    volume = data_proxy.history(order_book_id, dt, bar_count+NO_USE_DATA_NUM, frequency, 'volume').values

    swing = high - low
    swingk = get_k(swing)
    macd, signal,hist = talib.MACD(close,12,26,9)
    #kdj
    slowk, slowd = talib.STOCH(high,low,close,fastk_period=9,slowk_period=3,slowk_matype=0,slowd_period=3,slowd_matype=0)
    #boll
    upper, middle, lower = talib.BBANDS(close, timeperiod=15, nbdevup=1, nbdevdn=1, matype=0)
    band = upper - lower
    rp = close - middle
    bandk = get_k(band)

    volumek = get_k(volume)
    pricek = get_k(close)

    atr = talib.ATR(high,low,close,timeperiod=14)
    willr = talib.WILLR(high,low,close,timeperiod=14)
    ad = talib.AD(high,low,close,volume)
    rsi = talib.RSI(close, timeperiod=14)
    mom = talib.MOM(close, timeperiod=5)
    cci = talib.CCI(high,low,close,timeperiod=14)
    obv = talib.OBV(close,volume)
    apo = talib.APO(close, fastperiod=12, slowperiod=26, matype=0)
    cmo = talib.CMO(close,timeperiod=14)
    ppo = talib.PPO(close, fastperiod=12, slowperiod=26, matype=0)
    rocr = talib.ROCR(close, timeperiod=10)
    #trix = talib.TRIX(close, timeperiod=30)

    all_index = []
    #gaussian:([8, 10, 18, 5, 14], 0.57669206313491173)
    #
    for i in range(NO_USE_DATA_NUM, bar_count + NO_USE_DATA_NUM):
        index = [
            swing[i],
            swingk[i],
            macd[i],
            signal[i],
            hist[i],
            slowk[i],
            slowd[i],
            rp[i],
            band[i],
            bandk[i],
            volume[i],
            volumek[i],
            pricek[i],
            atr[i],
            willr[i],
            ad[i],
            rsi[i],
            mom[i],
            cci[i],
            obv[i],
            apo[i],
            cmo[i],
            ppo[i],
            rocr[i],
        ]
        all_index.append(index)
    return np.array(all_index)

def process_step_normal(data_proxy, order_book_id, dt, bar_count, frequency, step_num=4):
    close = data_proxy.history(order_book_id, dt, bar_count+step_num, frequency, 'close').values
    high = data_proxy.history(order_book_id, dt, bar_count+step_num, frequency, 'high').values
    low = data_proxy.history(order_book_id, dt, bar_count+step_num, frequency, 'low').values
    typical_price = (close + high + low) / 3
    open = data_proxy.history(order_book_id, dt, bar_count+step_num, frequency, 'open').values
    volume = data_proxy.history(order_book_id, dt, bar_count+step_num, frequency, 'volume').values

    mean_price = close.mean()
    sigma_price = np.sqrt( ((typical_price - mean_price)**2).sum() / len(close) )

    mean_volume = volume.mean()
    sigma_volume = np.sqrt( ((volume - mean_volume)**2).sum() / len(volume) )

    all_index = []
    for i in range(len(close)-step_num):
        index = []
        for j in range(step_num):
            index.append((close[i + j] - mean_price)/sigma_price)
            index.append((open[i + j] - mean_price)/sigma_price)
            index.append((high[i + j] - mean_price)/sigma_price)
            index.append((low[i + j] - mean_price)/sigma_price)
            index.append((volume[i+j] - mean_volume)/sigma_volume)
        all_index.append(index)
    return np.array(all_index)

def process_boll_step_normal(data_proxy, order_book_id, dt, bar_count, frequency, step_num=4):
    timeperiod = 19
    close = data_proxy.history(order_book_id, dt, bar_count+step_num+timeperiod, frequency, 'close').values
    high = data_proxy.history(order_book_id, dt, bar_count+step_num+timeperiod, frequency, 'high').values
    low = data_proxy.history(order_book_id, dt, bar_count+step_num+timeperiod, frequency, 'low').values
    open = data_proxy.history(order_book_id, dt, bar_count+step_num+timeperiod, frequency, 'open').values
    volume = data_proxy.history(order_book_id, dt, bar_count+step_num+timeperiod, frequency, 'volume').values
    
    upper, middle, lower = talib.BBANDS(close, timeperiod=timeperiod+1, nbdevup=1, nbdevdn=1, matype=0)
    
    close = close[timeperiod:]
    high = high[timeperiod:]
    low = low[timeperiod:]
    open = open[timeperiod:]
    volume = volume[timeperiod:]
    upper = upper[timeperiod:]
    middle = middle[timeperiod:]
    lower = lower[timeperiod:]
    typical_price = (close + high + low) / 3
    relate_price = typical_price - middle
    boll_dis = upper - lower

    #均值
    mean_volume = np.mean(volume)
    mean_boll_price = np.mean(middle)
    mean_boll_dis = np.mean(boll_dis)

    #标准差
    sigma_relate_price = np.sqrt((relate_price ** 2).sum()/len(relate_price))
    sigma_volume = np.sqrt(((volume - mean_volume)**2).sum()/len(volume))
    sigma_boll_price = np.sqrt(((middle-mean_boll_price)**2).sum()/len(middle))
    sigma_boll_dis = np.sqrt(((boll_dis-mean_boll_dis)**2).sum()/len(boll_dis))

    n_close = (close - middle) / sigma_relate_price
    n_open = (open - middle) / sigma_relate_price
    n_high = (high - middle) / sigma_relate_price
    n_low = (low - middle) / sigma_relate_price
    n_volume = (volume - mean_volume) / sigma_volume
    n_boll_price = (middle - mean_boll_price) / sigma_boll_price
    n_boll_dis = (boll_dis - mean_boll_dis) / sigma_boll_dis

    all_index = []
    for i in range(len(close)-step_num):
        index = []
        for j in range(step_num):
            index.append(n_open[i+j])
            index.append(n_close[i+j])
            index.append(n_high[i+j])
            index.append(n_low[i+j])
            index.append(n_volume[i+j])
            index.append(n_boll_price[i+j])
            index.append(n_boll_dis[i+j])
        all_index.append(index)
    return np.array(all_index)

def split_sentence(data, sentence_len):
    split_num = len(data) / sentence_len
    return np.array([data[i * sentence_len: (i+1) * sentence_len] for i in range(split_num)])

def process_wave_data(data_proxy, order_book_id, dt, bar_count, frequency, timeperiod=7):
    close = data_proxy.history(order_book_id, dt, bar_count, frequency, 'close').values
    #volume = data_proxy.history(order_book_id, dt, bar_count, frequency, 'volume').values
    w = get_wave(close,timeperiod)
    wave = []
    for i in range(1,len(w)-1):
        d = []
        d.append(close[w[i]])
        #d.append(volume[w[i]])
        d.append(w[i]-w[i-1])
        wave.append(d)
    return np.array(wave)

def get_wave(price, timeperiod=7):
    w = []
    w.append(0)
    for i in range(1,len(price)-1):
        left = max(i-timeperiod,0)
        right = min(len(price),i+timeperiod+1)
        minValue = price[i]
        maxValue = price[i]
        for j in range(left,right):
            minValue = min(minValue,price[j])
            maxValue = max(maxValue,price[j])
        if minValue == price[i] or maxValue == price[i] :
            w.append(i)
    w.append(len(price)-1)
    return w