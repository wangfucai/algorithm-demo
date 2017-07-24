'''
Created on Mar 16, 2017

@author: Heng.Zhang
'''


from global_var import *
import numpy as np
import datetime
from common import *
import logging
from nltk.tbl import feature
from utils import *

# 商家的优惠券被领取和使用的次数,两者之间的天数, 最大/最小天数, 在该商家使用优惠券的用户列表
def feature_merchant_coupon_cnt(m_id, user_id, merchant_coupon_cnt_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off):
    c_id = opt_tuple[1]
    discount_rate = opt_tuple[2]
    min_charge = opt_tuple[3]
    date_received = opt_tuple[4]
    date = opt_tuple[5]
    date_diff = opt_tuple[6]

    if (m_id not in merchant_coupon_cnt_dict):
        merchant_coupon_cnt_dict[m_id] = dict()
        merchant_coupon_cnt_dict[m_id][ONLINE] = [0, 0, [], 0, 0, set()]
        merchant_coupon_cnt_dict[m_id][OFFLINE] = [0, 0, [], 0, 0, set()]

    dict_ptr = merchant_coupon_cnt_dict[m_id][on_off]

    if (c_id is not None and discount_rate >= 0):
        if (date is None): # 领取优惠券
            if (date_received >= expected_date_tup[0] and date_received < expected_date_tup[1]): 
                dict_ptr[0] += tuple_cnt                
        elif (date >= expected_date_tup[0] and date < expected_date_tup[1]): #  使用优惠券
            dict_ptr[0] += tuple_cnt  # 使用优惠券隐含了领取优惠券
            dict_ptr[1] += tuple_cnt

            dict_ptr[2].extend([date_diff for x in range(tuple_cnt)])
            #  最大/最小天数
            if (dict_ptr[3] > date_diff):
                dict_ptr[3] = date_diff
            if (dict_ptr[4] < date_diff):
                dict_ptr[4] = date_diff

            dict_ptr[5].add(user_id)
    return


# 商家发放的 【0， 50】， 【51， 200】，【201， 500】， >500 的优惠券 的领取次数以及使用次数 
# 商家发放的各个折扣率领取的次数以及使用次数  <=0.5, (0.5, 0.7], (0.7, 0.9], > 0.9
def feature_merchant_coupon_discount(m_id, merchant_coupon_discount_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off):
    c_id = opt_tuple[1]
    discount_rate = opt_tuple[2]
    min_charge = opt_tuple[3]
    date_received = opt_tuple[4]
    date = opt_tuple[5]
    date_diff = opt_tuple[6]

    if (m_id not in merchant_coupon_discount_dict):
        # min charge 领取，使用次数， discount 领取，使用次数
        merchant_coupon_discount_dict[m_id] = dict()
        merchant_coupon_discount_dict[m_id][ONLINE] = [np.zeros((1, 4)), np.zeros((1, 4)), np.zeros((1, 4)), np.zeros((1, 4))]
        merchant_coupon_discount_dict[m_id][OFFLINE] = [np.zeros((1, 4)), np.zeros((1, 4)), np.zeros((1, 4)), np.zeros((1, 4))]
        
    dict_ptr = merchant_coupon_discount_dict[m_id][on_off]

    if (c_id is not None and discount_rate >= 0):
        discount_type = get_distount_type(discount_rate)
        min_charge_type = get_min_charge_type(min_charge)
        if (date is None):
            if (date_received >= expected_date_tup[0] and date_received < expected_date_tup[1]): # 领取优惠券
                dict_ptr[0][0, min_charge_type] += tuple_cnt
                dict_ptr[2][0, discount_type] += tuple_cnt
        elif (date >= expected_date_tup[0] and date < expected_date_tup[1]): #  使用优惠券
            dict_ptr[1][0, min_charge_type] += tuple_cnt  # 使用优惠券隐含了领取优惠券
            dict_ptr[3][0, discount_type] += tuple_cnt
    return


# 商家的用户的距离， 最大/最小距离
def feature_merchant_distance_date_diff(m_id, merchant_distance_dict, expected_date_tup, opt_tuple, tuple_cnt):
    if (m_id not in merchant_distance_dict):
        merchant_distance_dict[m_id] = [[], 0, 0]
        
    distance = opt_tuple[0]
    date_received = opt_tuple[4]
    date = opt_tuple[5]
    date_diff = opt_tuple[6]
    
    if (date is None):
        date = date_received
        
    dict_ptr = merchant_distance_dict[m_id]
    
    if (distance >= 0 and date >= expected_date_tup[0] and date < expected_date_tup[1]):
        merchant_distance_dict[m_id][0].extend([distance for x in range(tuple_cnt)])
        if (dict_ptr[1] > distance):
            dict_ptr[1] = distance

        if (dict_ptr[2] < distance):
            dict_ptr[2] = distance

    return 

# 商家的线上操作, 及各操作的比例
def feature_merchant_online_opt_cnt(m_id, merchant_online_opt_dict, expected_date_tup, opt_tuple, tuple_cnt):
    if (m_id not in merchant_online_opt_dict):
        merchant_online_opt_dict[m_id] = [0, 0, 0] # 0 点击， 1购买，2领取优惠券 

    action = opt_tuple[0]
    date_received = opt_tuple[4]
    date = opt_tuple[5]
    if ((action == 0 or action == 1)and (date >= expected_date_tup[0] and date < expected_date_tup[1])):
        merchant_online_opt_dict[m_id][action] += tuple_cnt
    elif (date_received is not None and date_received >= expected_date_tup[0] and date_received < expected_date_tup[1]):
        merchant_online_opt_dict[m_id][action] += tuple_cnt

    return

def create_merchant_feature_values(expected_date_tup, samples, users_on_off):
   # 商家的优惠券被领取和使用的次数,两者之间的天数, 最大/最小天数, 在该商家使用优惠券的用户列表
    merchant_coupon_cnt_dict = dict()
    
    # 商家发放的 【0， 50】， 【51， 200】，【201， 500】， >500 的优惠券 的领取次数以及使用次数 
    # 商家发放的各个折扣率领取的次数以及使用次数  <=0.5, (0.5, 0.7], (0.7, 0.9], > 0.9
    merchant_coupon_discount_dict = dict()
        
    # 商家的用户的距离， 最大/最小距离
    merchant_distance_dict = dict()
    
    # 用户线上操作次数, 及各操作的比例 
    merchant_online_opt_dict = dict()
    
    sample_cnt = len(samples)
    
    calculated_merchant_set = set()
    
    # 取得用户的哪些数据
    if (users_on_off == BOTH):
        being_caled_on_off = [ONLINE, OFFLINE]
    else:
        being_caled_on_off = [users_on_off]

    # 统计各个特征
    for index in range(sample_cnt):
        user_id = samples[index][0]
        m_id = samples[index][1]

        if (user_id not in g_users_for_algo[users_on_off]):
            continue
        
        if (m_id in calculated_merchant_set):
            if (index % 10000 == 0):
                print("calculating Merchant feature matrix, %d / %d handled\r" % (index, sample_cnt), end="")
            continue

        calculated_merchant_set.add(m_id)

        if (m_id not in g_merchant_user_dict):
            continue

        for on_off in being_caled_on_off:
            on_off_data_dict = g_merchant_user_dict[m_id][on_off]
            for user_id in on_off_data_dict.keys():
                for opt_tuple, tuple_cnt in on_off_data_dict[user_id].items(): 

                    # 商家的优惠券被领取和使用的次数,两者之间的天数, 最大/最小天数, 在该商家使用优惠券的用户列表
                    feature_merchant_coupon_cnt(m_id, user_id, merchant_coupon_cnt_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off)

                    # 商家发放的 【0， 50】， 【51， 200】，【201， 500】， >500 的优惠券 的领取次数以及使用次数 
                    # 商家发放的各个折扣率领取的次数以及使用次数  <=0.5, (0.5, 0.7], (0.7, 0.9], > 0.9
                    feature_merchant_coupon_discount(m_id, merchant_coupon_discount_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off)

                    if (on_off == ONLINE):
                        feature_merchant_online_opt_cnt(m_id, merchant_online_opt_dict, expected_date_tup, opt_tuple, tuple_cnt)                        
                    else:
                        feature_merchant_distance_date_diff(m_id, merchant_distance_dict, expected_date_tup, opt_tuple, tuple_cnt)

        if (index % 10000 == 0):
            print("calculating Merchant feature matrix, %d / %d handled\r" % (index, sample_cnt), end="")
    
    return merchant_coupon_cnt_dict, merchant_coupon_discount_dict, merchant_distance_dict, merchant_online_opt_dict

def create_merchant_features_online_matrix(samples):
    merchant_online_opt_dict = g_feature_values["merchant_online_opt_dict"]
    
    merchant_feature_matrix = np.zeros((len(samples), 100))
    
    merchant_feature_value_dict = dict()

   # 特征矩阵
    feature_cnt = 6
    feature_idx = 0
    sample_cnt = len(samples)
    for index in range(sample_cnt):
        user_id = samples[index][0]
        m_id = samples[index][1]
        
        if (m_id in merchant_feature_value_dict):
            if (index % 10000 == 0):
                print("creating Merchant feature matrix, %d / %d handled\r"  % (index, sample_cnt), end="") 

            merchant_feature_matrix[index] = merchant_feature_value_dict[m_id]
            continue

        if (m_id not in g_merchant_user_dict or 
            m_id not in merchant_online_opt_dict):
            continue

        feature_idx = 0

        totoal_opt_cnt = sum(merchant_online_opt_dict[m_id]) + 1

        # 商家的操作次数, 以及所占的比例
        merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][0]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][1]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][2]; feature_idx += 1

        merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][0] / totoal_opt_cnt; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][1] / totoal_opt_cnt; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][2] / totoal_opt_cnt; feature_idx += 1

        merchant_feature_value_dict[m_id] = merchant_feature_matrix[index]

        if (feature_cnt != feature_idx):
            feature_cnt = feature_cnt

    print("%s Merchant ONLINE feature matrix (%d, %d)" % (getCurrentTime(), sample_cnt, feature_cnt))
    return merchant_feature_matrix[:, 0:feature_cnt]    



def create_merchant_features_offline_matrix(samples):    
    merchant_distance_dict = g_feature_values["merchant_distance_dict"]
        
    merchant_feature_matrix = np.zeros((len(samples), 100))
    
    merchant_feature_value_dict = dict()

    # 特征矩阵
    feature_cnt = 3
    feature_idx = 0
    sample_cnt = len(samples)
    for index in range(sample_cnt):
        user_id = samples[index][0]
        m_id = samples[index][1]
        
        if (m_id in merchant_feature_value_dict):
            if (index % 10000 == 0):
                print("creating Merchant feature matrix, %d / %d handled\r"  % (index, sample_cnt), end="") 

            merchant_feature_matrix[index] = merchant_feature_value_dict[m_id]
            continue
        
        if (m_id not in g_merchant_user_dict or
            m_id not in merchant_distance_dict):
            continue

        feature_idx = 0
        
        # 商家的用户的平均距离， 最大/最小距离
        merchant_feature_matrix[index, feature_idx] = sum(merchant_distance_dict[m_id][0])/(len(merchant_distance_dict[m_id][0]) + 1); feature_idx += 1
        merchant_feature_matrix[index, feature_idx] = merchant_distance_dict[m_id][1]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] = merchant_distance_dict[m_id][2]; feature_idx += 1
        
        merchant_feature_value_dict[m_id] = merchant_feature_matrix[index]
        
        if (feature_cnt != feature_idx):
            feature_cnt = feature_cnt

    print("%s Merchant OFFLINE feature matrix (%d, %d)" % (getCurrentTime(), sample_cnt, feature_cnt))
    return merchant_feature_matrix[:, 0:feature_cnt]    

# (action,   c_id, discount_rate, min_charge, date_received, date, date_diff)
# (distance, c_id, discount_rate, min_charge, date_received, date, date_diff)
def create_merchant_feature_on_off_matrix(samples, on_off):

    merchant_coupon_cnt_dict = g_feature_values["merchant_coupon_cnt_dict"]
    merchant_coupon_discount_dict = g_feature_values["merchant_coupon_discount_dict"]
    
    merchant_feature_matrix = np.zeros((len(samples), 100))

    merchant_feature_value_dict = dict()

    # 特征矩阵
    feature_cnt = 30
    sample_cnt = len(samples)
    for index in range(sample_cnt):
        user_id = samples[index][0]
        m_id = samples[index][1]

        if (m_id in merchant_feature_value_dict):
            if (index % 10000 == 0):
                print("creating Merchant feature matrix, %d / %d handled\r"  % (index, sample_cnt), end="") 

            merchant_feature_matrix[index] = merchant_feature_value_dict[m_id]
            continue

        if (m_id not in g_merchant_user_dict):
            continue

        feature_idx = 0
        
        if (m_id not in merchant_coupon_cnt_dict):
            continue

        # 商家的优惠券被领取和使用的次数,两者之间的平均天数, 最大/最小天数, 用户在该商家平均使用的优惠券数量
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][on_off][0]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][on_off][1]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  sum(merchant_coupon_cnt_dict[m_id][on_off][2])/\
                                                       (len(merchant_coupon_cnt_dict[m_id][on_off][2]) + 1); feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][on_off][3]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][on_off][4]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][on_off][1]/ \
                                                       (len(merchant_coupon_cnt_dict[m_id][on_off][5]) + 1); feature_idx += 1

        # 商家发放的 【0， 50】， 【51， 200】，【201， 500】， >500 的优惠券 的领取次数以及使用次数 ,
        # 商家发放的各个折扣率领取的次数以及使用次数  <=0.5, (0.5, 0.7], (0.7, 0.9], > 0.9
        # 使用次数与领取次数的比值
        # min chagre 领取次数
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][on_off][0]; feature_idx += 4
        # 使用次数
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][on_off][1]; feature_idx += 4
        # 使用次数占领取的比例 
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  \
            merchant_coupon_discount_dict[m_id][ONLINE][1] / (merchant_coupon_discount_dict[m_id][on_off][1] + 1); feature_idx += 4
        # discount rate 领取次数
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][on_off][2]; feature_idx += 4
        # 使用次数
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][on_off][3]; feature_idx += 4
        # 使用次数占领取的比例
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  \
            merchant_coupon_discount_dict[m_id][ONLINE][3] / (merchant_coupon_discount_dict[m_id][on_off][2] + 1); feature_idx += 4
                           
        if (feature_cnt != feature_idx):
            feature_cnt = feature_cnt

        merchant_feature_value_dict[m_id] = merchant_feature_matrix[index]

        if (index % 1000 == 0):
            print("%s creating Merchant feature matrix, %d / %d handled\r"  % (getCurrentTime(), index, sample_cnt), end="") 
  
    print("%s Merchant ON/OFF feature matrix (%d, %d)" % (getCurrentTime(), sample_cnt, feature_cnt))
    return merchant_feature_matrix[:, 0:feature_cnt]    

# (action,   c_id, discount_rate, min_charge, date_received, date, date_diff)
# (distance, c_id, discount_rate, min_charge, date_received, date, date_diff)
def create_merchant_feature_matrix_ex(samples, on_off):

    if (on_off == BOTH):
        feature_mat = create_merchant_feature_on_off_matrix(samples, ONLINE)
        Xmat = create_merchant_feature_on_off_matrix(samples, OFFLINE)
        feature_mat = np.column_stack((feature_mat, Xmat))
        
        Xmat = create_merchant_features_online_matrix(samples)
        feature_mat = np.column_stack((feature_mat, Xmat))
        
        Xmat = create_merchant_features_offline_matrix(samples)
        feature_mat = np.column_stack((feature_mat, Xmat))
        
        return feature_mat
 
    feature_mat = create_merchant_feature_on_off_matrix(samples, on_off)
    if (on_off == ONLINE):        
        Xmat = create_merchant_features_online_matrix(samples)
    else:
        Xmat = create_merchant_features_offline_matrix(samples)
         
    feature_mat = np.column_stack((feature_mat, Xmat))
    
    return feature_mat

    return feature_mat



# (action,   c_id, discount_rate, min_charge, date_received, date, date_diff)
# (distance, c_id, discount_rate, min_charge, date_received, date, date_diff)
def create_merchant_feature_matrix(expected_date_tup, samples):
    
    merchant_coupon_cnt_dict, \
    merchant_coupon_discount_dict, \
    merchant_distance_dict, \
    merchant_online_opt_dict = \
        create_merchant_feature_values(expected_date_tup, samples)

    merchant_feature_matrix = np.zeros((len(samples), 100))
    
    merchant_feature_value_dict = dict()

    # 特征矩阵
    feature_idx = 0
    sample_cnt = len(samples)
    for index in range(sample_cnt):
        user_id = samples[index][0]
        m_id = samples[index][1]
        
        if (m_id in merchant_feature_value_dict):
            if (index % 10000 == 0):
                print("creating Merchant feature matrix, %d / %d handled\r"  % (index, sample_cnt), end="") 

            merchant_feature_matrix[index] = merchant_feature_value_dict[m_id]
            continue
        
        if (m_id not in g_merchant_user_dict):
            continue

        feature_idx = 0

        # 商家的优惠券被领取和使用的次数,两者之间的平均天数, 最大/最小天数, 用户在该商家平均使用的优惠券数量
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][ONLINE][0]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][ONLINE][1]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  sum(merchant_coupon_cnt_dict[m_id][ONLINE][2])/\
                                                       (len(merchant_coupon_cnt_dict[m_id][ONLINE][2]) + 1); feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][ONLINE][3]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][ONLINE][4]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][ONLINE][1]/ \
                                                       (len(merchant_coupon_cnt_dict[m_id][ONLINE][5]) + 1); feature_idx += 1
                                                       
         # 商家发放的 【0， 50】， 【51， 200】，【201， 500】， >500 的优惠券 的领取次数以及使用次数 ,
        # 商家发放的各个折扣率领取的次数以及使用次数  <=0.5, (0.5, 0.7], (0.7, 0.9], > 0.9
        # 使用次数与领取次数的比值
        # min chagre 领取次数
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][ONLINE][0]; feature_idx += 4
        # 使用次数
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][ONLINE][1]; feature_idx += 4
        # 使用次数占领取的比例 
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  \
            merchant_coupon_discount_dict[m_id][ONLINE][1] / (merchant_coupon_discount_dict[m_id][ONLINE][1] + 1); feature_idx += 4
        # discount rate 领取次数
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][ONLINE][2]; feature_idx += 4
        # 使用次数
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][ONLINE][3]; feature_idx += 4
        # 使用次数占领取的比例
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  \
            merchant_coupon_discount_dict[m_id][ONLINE][3] / (merchant_coupon_discount_dict[m_id][ONLINE][2] + 1); feature_idx += 4
                                                           
        
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][OFFLINE][0]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][OFFLINE][1]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  sum(merchant_coupon_cnt_dict[m_id][OFFLINE][2])/\
                                                       (len(merchant_coupon_cnt_dict[m_id][OFFLINE][2]) + 1); feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][OFFLINE][3]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][OFFLINE][4]; feature_idx += 1
        merchant_feature_matrix[index, feature_idx] =  merchant_coupon_cnt_dict[m_id][OFFLINE][1]/\
                                                       (len(merchant_coupon_cnt_dict[m_id][OFFLINE][5]) + 1); feature_idx += 1
        
       
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][OFFLINE][0]; feature_idx += 4
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][OFFLINE][1]; feature_idx += 4
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  \
            merchant_coupon_discount_dict[m_id][OFFLINE][1] / (merchant_coupon_discount_dict[m_id][OFFLINE][1] + 1); feature_idx += 4
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][OFFLINE][2]; feature_idx += 4
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  merchant_coupon_discount_dict[m_id][OFFLINE][3]; feature_idx += 4
        merchant_feature_matrix[index, feature_idx : feature_idx + 4] =  \
            merchant_coupon_discount_dict[m_id][OFFLINE][3] / (merchant_coupon_discount_dict[m_id][OFFLINE][2] + 1); feature_idx += 4

        # 商家的用户的平均距离， 最大/最小距离
        if (m_id in merchant_distance_dict):
            merchant_feature_matrix[index, feature_idx] = sum(merchant_distance_dict[m_id][0])/(len(merchant_distance_dict[m_id][0]) + 1); feature_idx += 1
            merchant_feature_matrix[index, feature_idx] = merchant_distance_dict[m_id][1]; feature_idx += 1
            merchant_feature_matrix[index, feature_idx] = merchant_distance_dict[m_id][2]; feature_idx += 1
        else:
            # 没有feature 填 0， 这样特征数可以保持一致
            feature_idx += 3
        
        # 商家的操作次数, 以及所占的比例
        if (m_id in merchant_online_opt_dict):
            totoal_opt_cnt = sum(merchant_online_opt_dict[m_id]) + 1

            merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][0]; feature_idx += 1
            merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][1]; feature_idx += 1
            merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][2]; feature_idx += 1

            merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][0] / totoal_opt_cnt; feature_idx += 1
            merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][1] / totoal_opt_cnt; feature_idx += 1
            merchant_feature_matrix[index, feature_idx] = merchant_online_opt_dict[m_id][2] / totoal_opt_cnt; feature_idx += 1
        else:
            feature_idx += 6 # 没有feature 填 0， 这样特征数可以保持一致

        merchant_feature_value_dict[m_id] = merchant_feature_matrix[index]

        if (index % 1000 == 0):
            print("%s creating Merchant feature matrix, %d / %d handled\r"  % (getCurrentTime(), index, sample_cnt), end="") 
  
    print("%s Merchant feature matrix (%d, %d)" % (getCurrentTime(), sample_cnt, feature_idx))
    return merchant_feature_matrix[:, 0:feature_idx]
