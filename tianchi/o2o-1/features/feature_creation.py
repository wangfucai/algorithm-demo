'''
Created on Mar 8, 2017

@author: Heng.Zhang
'''
import datetime


from global_var import * 
from common import *
from user_features import *
from takingsamples import *
from merchant_features import *
from coupon_features import *
from utils import *
from sklearn import preprocessing

def createFeatureMatrixEx(samples, on_off):
    coupon_feature_mat = create_coupon_feature_matrix_ex(samples, on_off)
    merchant_feature_mat = create_merchant_feature_matrix_ex(samples, on_off)
    user_feature_mat = create_user_feature_matrix_ex(samples, on_off)
    
    feature_mat = np.column_stack((coupon_feature_mat, merchant_feature_mat, user_feature_mat))
    print(getCurrentTime(),"Coupon matrix ", coupon_feature_mat.shape, \
          " Merchant matrix ", merchant_feature_mat.shape, " User matrix ", user_feature_mat.shape)

    print("%s Total " % (getCurrentTime()), feature_mat.shape)
    feature_mat = preprocessing.scale(feature_mat)
    return feature_mat


if __name__ == '__main__':
    exit(0)
