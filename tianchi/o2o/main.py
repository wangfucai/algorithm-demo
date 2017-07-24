import pickle

import tianchi.o2o.feature_extc.feature_extc as fc
import tianchi.o2o.models.train as tr

fc.extc_feature()
feature_v_f = open('C:/Users/WangFuCai/PycharmProjects/DecisionTree/tianchi/o2o/data/feature_values', 'rb')
c_l = pickle.load(feature_v_f)
feature_v_f.close()
print 'testtest'
for c in c_l:
    for each in c.items():
        print(each)
    print('\n')
X, y = tr.get_input_data(c_l)
print(len(X), len(y))
print(X[10: 20])
print(y[10: 20])
