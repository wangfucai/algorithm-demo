from sklearn import svm
from sklearn.externals import joblib
import tianchi.o2o.feature_extc.feature_extc as fc
import numpy as np


def get_input_data(feature_values):
    X = []
    y = []
    file_data = open('C:/Users/WangFuCai/PycharmProjects/DecisionTree/tianchi/o2o/data/ccf_offline_stage1_train.csv', 'r')
    file_text = file_data.readlines()[:]
    for line in file_text[1:]:
        cols = line.strip().split(',')
        user_id = cols[0]
        merchant_id = cols[1]
        discount_rate = cols[3]
        distance = cols[4]
        keys = (user_id, merchant_id, discount_rate, distance, user_id, merchant_id, discount_rate)
        v_l = []
        if cols[-2] != 'null':
            for i in range(len(feature_values)):
                v = feature_values[i].get(keys[i], 0)
                v_l.append(v)
            X.append(v_l)
            if cols[-1] != 'null' and fc.day_duration(cols[-2], cols[-1]) <= 15:
                y.append(1)
            else:
                y.append(0)
    X = np.array(X)
    y = np.array(y)
    return X, y

# clf = svm.SVC(kernel='rbf')
# clf.fit(X[: 200000], y[: 200000])
# joblib.dump(clf, 'svm.model')
# clf = joblib.load('svm.model')
# y = clf.predict(X[:1000])
# print(y)


