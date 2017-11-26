import pandas as pd
import numpy as np
from functools import partial
from scipy.stats import pearsonr
from sklearn.model_selection import cross_val_score

from sklearn import preprocessing
from sklearn.linear_model import SGDClassifier

from stdb import LocalDataProxy
from data_process import process_index

from acheat import random_select

dataProxy = LocalDataProxy()
index = process_index(dataProxy,'0000001',pd.Timestamp('2016-5-5'),600,'1d')
scaler = preprocessing.StandardScaler().fit(index)
data = scaler.transform(index)
rise = dataProxy.history('0000001',pd.Timestamp('2016-5-5'),600,'1d','rise').values
rise[0:len(rise)-1] = rise[1:len(rise)]
rise[-1] = 0
binarizer = preprocessing.Binarizer().fit(rise)
target = binarizer.transform(rise).transpose().reshape(len(rise),)
print(float(sum(target))/len(target))

print("select fecture-------------------------------------------")
def evl(selection,data,target):
    new_data = np.zeros([data.shape[0],len(selection)])
    for i in range(len(selection)):
        new_data[:,i] = data[:,selection[i]]
    clf = SGDClassifier()
    scores = cross_val_score(clf, new_data, target)
    score = scores.mean()

    l = int(len(new_data) * 0.6)
    X_train = new_data[:l]
    X_test = new_data[l:]
    y_train = target[:l]
    y_test = target[l:]

    clf = SGDClassifier().fit(X_train,y_train)
    score = score + clf.score(X_test,y_test)

    print(selection)
    print(score * 0.5)
    return score * 0.5

index_t = index.transpose()
scores = [0 for i in range(len(index_t))]
relate_table=[]
for i in range(len(index_t)):
    rl = []
    for j in range(len(index_t)):
        if j < i:
            p = pearsonr(index_t[i],index_t[j])
            rl.append(1-abs(p[0]))
        else:
            rl.append(0)
    relate_table.append(rl)
for i in range(len(index_t)):
    for j in range(i+1,len(index_t)):
        relate_table[i][j] = relate_table[j][i]
evl_handle = partial(evl,data=data,target=target)
print(random_select(evl_handle,5,np.array(scores),relate_table,[20,10,5,2,1],0.66))