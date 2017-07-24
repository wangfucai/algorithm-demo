'''
Created on Mar 6, 2017

@author: Heng.Zhang
'''
import sys

g_user_merchant_dict = dict()
g_merchant_user_dict = dict()
g_coupon_merchant_dict = dict()

g_fcst_user_data_dict = dict()
g_fcst_merchant_data_dict = dict()
g_fcst_coupon_merchant_data_dict = dict()

# 没有使用过优惠券的用户直接预测为0
g_fcst_users_without_coupon = set()


ONLINE = 0
OFFLINE = 1
BOTH = 2
g_users_for_algo = {ONLINE:set(), OFFLINE:set(), BOTH:set()}

g_feature_values = dict()

runningPath = sys.path[0]
sys.path.append("%s\\features\\" % runningPath)

output_filename_fmt = r"%s\..\output\subdata\forecast.(%s.%s).%s.%d.csv"