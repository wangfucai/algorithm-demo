'''
Created on Mar 8, 2017

@author: Heng.Zhang
'''


from global_var import *
import numpy as np
import datetime
from common import *
import logging
from nltk.tbl import feature
from utils import *

# 用户领取优惠券的次数以及线上线下占总领取次数的比例
def feature_user_get_coupon_cnt(user_id, user_get_coupon_cnt_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off):
    action = opt_tuple[0]
    date_received = opt_tuple[4]
    date = opt_tuple[5]
    
    if (user_id not in user_get_coupon_cnt_dict):
        user_get_coupon_cnt_dict[user_id] = dict()
        user_get_coupon_cnt_dict[user_id][ONLINE] = 0
        user_get_coupon_cnt_dict[user_id][OFFLINE] = 0

    if (date_received is not None and date is None and \
        date_received >= expected_date_tup[0] and date_received < expected_date_tup[1]):
        user_get_coupon_cnt_dict[user_id][on_off] += tuple_cnt
    return 


# 用户使用优惠券消费的次数以及从领取优惠券到使用之间的平均天数
def feature_user_buy_cnt_with_coupon(user_id, user_buy_cnt_with_coupon_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off):
    c_id = opt_tuple[1]
    date_received = opt_tuple[4]
    date = opt_tuple[5]
    date_diff = opt_tuple[6]
    
    if (user_id not in user_buy_cnt_with_coupon_dict):
        user_buy_cnt_with_coupon_dict[user_id] = dict()
        user_buy_cnt_with_coupon_dict[user_id][ONLINE] = []
        user_buy_cnt_with_coupon_dict[user_id][OFFLINE] = []

    if (c_id is not None and date is not None and \
        date >= expected_date_tup[0] and date < expected_date_tup[1]):
        user_buy_cnt_with_coupon_dict[user_id][on_off].extend([date_diff for x in range(tuple_cnt)])

    return

# 用户没有使用优惠券消费的次数
def feature_user_buy_cnt_without_coupon(user_id, user_buy_cnt_without_coupon_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off):
    c_id = opt_tuple[1]
    date = opt_tuple[5]
    
    if (user_id not in user_buy_cnt_without_coupon_dict):
        user_buy_cnt_without_coupon_dict[user_id] = dict()
        user_buy_cnt_without_coupon_dict[user_id][ONLINE] = 0
        user_buy_cnt_without_coupon_dict[user_id][OFFLINE] = 0    

    if (c_id is None and date is not None and \
        date >= expected_date_tup[0] and date < expected_date_tup[1]):
        user_buy_cnt_without_coupon_dict[user_id][on_off] += tuple_cnt
    return

# 用户使用 【0， 50】， 【51， 200】，【201， 500】， >500 的优惠券占使用优惠券的次数的比值
# 先计算出每种类型的优惠券的使用次数
# 用户使用优惠券各个折扣率出现的次数  <=0.5, (0.5, 0.7], (0.7, 0.9], > 0.9
def feature_user_coupon_fraction(user_id, user_coupon_fraction_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off):
    action = opt_tuple[0]
    c_id = opt_tuple[1]
    date = opt_tuple[5]
    
    if (user_id not in user_coupon_fraction_dict):
        user_coupon_fraction_dict[user_id] = dict()
        # 每种类型的优惠券的使用次数, 用户使用优惠券各个折扣率出现的次数, 折扣率的最大/最小值
        user_coupon_fraction_dict[user_id][ONLINE] = [np.zeros((1, 4)), np.zeros((1, 4)), 0, 0]
        user_coupon_fraction_dict[user_id][OFFLINE] = [np.zeros((1, 4)), np.zeros((1, 4)), 0, 0]    

    
    if (date is not None and c_id is not None):
        discount_rate = opt_tuple[2]
        min_charge = opt_tuple[3]
        
        # 每种类型的优惠券的使用次数
        min_charge_type = get_min_charge_type(min_charge)
        if (min_charge_type >= 0):
            user_coupon_fraction_dict[user_id][on_off][0][0, min_charge_type] += tuple_cnt
        else:
            logging.error("unknown min charge %s" % opt_tuple)

        discount_type = get_distount_type(discount_rate)
        if (discount_type >= 0):
            user_coupon_fraction_dict[user_id][on_off][1][0, discount_type] += tuple_cnt
        else:
            logging.error("unknown discount rate %s" % opt_tuple)

        # 用户使用优惠券各个折扣率出现的次数
        if (discount_rate > 0 and discount_rate < user_coupon_fraction_dict[user_id][on_off][2]):
                user_coupon_fraction_dict[user_id][on_off][2] = discount_rate
        
        if (discount_rate > 0 and discount_rate > user_coupon_fraction_dict[user_id][on_off][3]):
                user_coupon_fraction_dict[user_id][on_off][3] = discount_rate
    return


# 用户在各个商家领取以及使用的优惠券的数量以及占该用户使用优惠券的比例
def feature_user_coupon_of_merchant_fraction(user_id, m_id, user_coupon_of_merchant_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off):
    c_id = opt_tuple[1]
    date_received = opt_tuple[4]
    date = opt_tuple[5]

    if (user_id not in user_coupon_of_merchant_dict):
        user_coupon_of_merchant_dict[user_id] = dict()
    
    if (m_id not in user_coupon_of_merchant_dict[user_id]):
        user_coupon_of_merchant_dict[user_id][m_id] = dict()
        user_coupon_of_merchant_dict[user_id][m_id][ONLINE] = [0, 0] # 领取的数量，使用的数量
        user_coupon_of_merchant_dict[user_id][m_id][OFFLINE] = [0, 0]

    if (c_id is not None):
        # 领取的数量
        if (date is None and date_received is not None and \
            date_received >= expected_date_tup[0] and date_received < expected_date_tup[1]):
            user_coupon_of_merchant_dict[user_id][m_id][on_off][0] += tuple_cnt        
        # 使用的数量
        elif (date is not None and 
              date >= expected_date_tup[0] and date < expected_date_tup[1]):
            user_coupon_of_merchant_dict[user_id][m_id][on_off][1] += tuple_cnt

    return

# 用户从领取优惠券到使用之间的平均天数
# 这里先计算总共的天数，然后再除以使用次数
def feature_user_coupon_days_diff(user_id, user_coupon_days_diff_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off):
    if (user_id not in user_coupon_days_diff_dict):
        user_coupon_days_diff_dict[user_id] = dict()
        user_coupon_days_diff_dict[user_id][ONLINE] = 0
        user_coupon_days_diff_dict[user_id][OFFLINE] = 0

    c_id = opt_tuple[1]
    date_received = opt_tuple[4] 
    date = opt_tuple[5]

    if (c_id is not None and date is not None and \
        date >= expected_date_tup[0] and date < expected_date_tup[1]):
        user_coupon_days_diff_dict[user_id][on_off] += ((date - date_received).days * tuple_cnt)
    return

# 用户线下使用优惠券距离商家的平均/最大/最小距离
def feature_user_distance(user_id, m_id, user_distance_dict, expected_date_tup, opt_tuple, tuple_cnt):
    if (user_id not in user_distance_dict):
        user_distance_dict[user_id] = [[], 0, 0]
    
    distance = opt_tuple[0]
    date = opt_tuple[5]
    
    if (distance >= 0 and date is not None and
        date >= expected_date_tup[0] and date < expected_date_tup[1]):
        user_distance_dict[user_id][0].extend([distance for x in range(tuple_cnt)])
        if (distance < user_distance_dict[user_id][1]):
            user_distance_dict[user_id][1] = distance

        if (distance > user_distance_dict[user_id][2]):
            user_distance_dict[user_id][2] = distance
    return

# 用户线上操作次数, 及各操作的比例 
def feature_user_opt_online(user_id, user_opt_online_dict, expected_date_tup, opt_tuple, tuple_cnt):
    if (user_id not in user_opt_online_dict):
        user_opt_online_dict[user_id] = [0, 0, 0] # 0 点击， 1购买，2领取优惠券

    action = opt_tuple[0]
    date = opt_tuple[5]
    date_received = opt_tuple[4]
    
    if ((action == 0 or action == 1)and (date >= expected_date_tup[0] and date < expected_date_tup[1])):
        user_opt_online_dict[user_id][action] += tuple_cnt
    elif (date_received is not None and date_received >= expected_date_tup[0] and date_received < expected_date_tup[1]):
        user_opt_online_dict[user_id][action] += tuple_cnt

    return

# 用户在一周内的第几天使用过几次优惠券
def feature_user_coupon_weekday(user_id, user_coupon_weekday_dict, expected_date_tup, opt_tuple, tuple_cnt, on_off):
    if (user_id not in user_coupon_weekday_dict):
        user_coupon_weekday_dict[user_id] = dict()
        user_coupon_weekday_dict[user_id][ONLINE] = [0 for x in range(7)]
        user_coupon_weekday_dict[user_id][OFFLINE] = [0 for x in range(7)]
        
    date_received = opt_tuple[4]
    date = opt_tuple[5]
    date_diff = opt_tuple[6]
    
    if (date_diff is not None and date >= expected_date_tup[0] and date < expected_date_tup[1]):
        user_coupon_weekday_dict[user_id][on_off][date.weekday()] = tuple_cnt
    
    return


def create_user_feature_value(expected_date_tup, samples, users_on_off):
    # 用户领取优惠券的次数
    user_get_coupon_cnt_dict = dict()

    # 用户使用优惠券消费的次数以及从领取优惠券到使用之间的平均天数    
    user_buy_cnt_with_coupon_dict = dict()

    # 用户没有使用优惠券消费的次数
    user_buy_cnt_without_coupon_dict = dict()

    # 用户使用 【0， 50】， 【51， 200】，【201， 500】， >500 的优惠券占使用优惠券的次数的比值, 先计算出每种类型的优惠券的使用次数
    # 用户使用优惠券各个折扣率出现的次数  <=0.5, (0.5, 0.7], (0.7, 0.9], > 0.9, fixed 按照  <=0.5算
    user_coupon_fraction_dict = dict()
    
    # 用户从领取优惠券到使用之间的平均天数
    user_coupon_days_diff_dict = dict()
    
    # 用户在各个商家使用的优惠券的数量以及占该用户使用优惠券的比例
    user_coupon_of_merchant_dict = dict()
    
    # 用户线下使用优惠券距离商家的平均/最大/最小距离
    user_distance_dict = dict()
    
    # 用户线上操作次数
    user_opt_online_dict = dict()
    
    # 用户在一周内的第几天使用过几次优惠券
    user_coupon_weekday_dict = dict()
    
    # 统计各个特征
    sample_cnt = len(samples)
    user_calculated_set = set()
    
    # 取得用户的哪些数据
    if (users_on_off == BOTH):
        being_caled_on_off = [ONLINE, OFFLINE]
    else:
        being_caled_on_off = [users_on_off]

    for index in range(sample_cnt):
        user_id = samples[index][0]
        m_id = samples[index][1]

        if (user_id not in g_users_for_algo[users_on_off]):
            continue

        if (user_id in user_calculated_set):            
            if (index % 10000 == 0):
                print("%s calculating User feature values, %d / %d handled\r" % (getCurrentTime(), index, sample_cnt), end="")
            continue

        user_calculated_set.add(user_id)

        for on_off in being_caled_on_off:
#         for on_off in g_user_merchant_dict[user_id].keys():
#             if (users_on_off != BOTH and on_off != users_on_off):
#                 continue

            on_off_data_dict = g_user_merchant_dict[user_id][on_off]
            for m_id in g_user_merchant_dict[user_id][on_off].keys():
                opt_tuples_dict = on_off_data_dict[m_id]
                for opt_tuple, opt_cnt in opt_tuples_dict.items():

                    # 用户领取优惠券的次数以及线上线下占总领取次数的比例
                    feature_user_get_coupon_cnt(user_id, user_get_coupon_cnt_dict, expected_date_tup, opt_tuple, opt_cnt, on_off)

                    # 用户使用优惠券消费的次数以及从领取优惠券到使用之间的平均天数
                    feature_user_buy_cnt_with_coupon(user_id, user_buy_cnt_with_coupon_dict, expected_date_tup, opt_tuple, opt_cnt, on_off)

                    # 用户没有使用优惠券消费的次数
                    feature_user_buy_cnt_without_coupon(user_id, user_buy_cnt_without_coupon_dict, expected_date_tup, opt_tuple, opt_cnt, on_off)

                    # 用户使用 【0， 50】， 【51， 200】，【201， 500】， >500 的优惠券占使用优惠券的次数的比值, 先计算出每种类型的优惠券的使用次数
                    # 用户使用优惠券各个折扣率出现的次数  <=0.5, (0.5, 0.7], (0.7, 0.9], > 0.9
                    feature_user_coupon_fraction(user_id, user_coupon_fraction_dict, expected_date_tup, opt_tuple, opt_cnt, on_off)

                    # 用户从领取优惠券到使用之间的平均天数
                    # 这里先计算总共的天数，然后再除以使用次数
                    feature_user_coupon_days_diff(user_id, user_coupon_days_diff_dict, expected_date_tup, opt_tuple, opt_cnt, on_off)
                    
                    # 用户在各个商家使用的优惠券占该用户使用优惠券的比例
                    feature_user_coupon_of_merchant_fraction(user_id, m_id, user_coupon_of_merchant_dict, expected_date_tup, opt_tuple, opt_cnt, on_off)

                    # 用户在一周内的第几天使用过几次优惠券
                    feature_user_coupon_weekday(user_id, user_coupon_weekday_dict, expected_date_tup, opt_tuple, opt_cnt, on_off)

                    if (on_off == ONLINE):
                        # 用户线上操作次数
                        feature_user_opt_online(user_id, user_opt_online_dict, expected_date_tup, opt_tuple, opt_cnt)
                    else:
                        # 用户线下使用优惠券距离商家的平均/最大/最小距离
                        feature_user_distance(user_id, m_id, user_distance_dict, expected_date_tup, opt_tuple, opt_cnt)

        if (index % 10000 == 0):
            print("%s calculating User feature values, %d / %d handled\r" % (getCurrentTime(), index, sample_cnt), end="")

    del user_calculated_set

    return user_get_coupon_cnt_dict, user_buy_cnt_with_coupon_dict, user_buy_cnt_without_coupon_dict, user_coupon_fraction_dict,\
           user_coupon_days_diff_dict, user_coupon_of_merchant_dict, user_distance_dict, user_opt_online_dict, user_coupon_weekday_dict


def create_user_online_matrix(samples):
    user_opt_online_dict = g_feature_values["user_opt_online_dict"]
    # 特征矩阵
    feature_cnt = 6
    feature_idx = 0

    user_features_matrix = np.zeros((len(samples), 100))

    user_feature_values_dict = dict()

    sample_cnt = len(samples)

    for index in range(sample_cnt):
        user_id = samples[index][0]
        m_id = samples[index][1]

        if (user_id in user_feature_values_dict):
            user_features_matrix[index] = user_feature_values_dict[user_id]

            if (index % 10000 == 0):
                print("%s creating user ONLINE feature matrix, %d / %d handled\r" % (getCurrentTime(), index, sample_cnt), end="")       
            continue
        
        feature_idx = 0

        if (user_id not in user_opt_online_dict):
            if (index % 1000 == 0):
                print("%s creating user ONLINE feature matrix, %d / %d handled\r" % (getCurrentTime(), index, sample_cnt), end="")
            continue

        # 用户线上操作次数, 及各操作的比例
        user_opt_cnt_online = sum(user_opt_online_dict[user_id]) + 1
        user_features_matrix[:, feature_idx : feature_idx + 3] = user_opt_cnt_online; feature_idx += 3
        user_features_matrix[:, feature_idx] = user_opt_online_dict[user_id][0] / user_opt_cnt_online; feature_idx += 1
        user_features_matrix[:, feature_idx] = user_opt_online_dict[user_id][1] / user_opt_cnt_online; feature_idx += 1
        user_features_matrix[:, feature_idx] = user_opt_online_dict[user_id][2] / user_opt_cnt_online; feature_idx += 1
    
        if (index % 1000 == 0):
            print("%s creating user ONLINE feature matrix, %d / %d handled\r" % (getCurrentTime(), index, sample_cnt), end="")

        user_feature_values_dict[user_id] = user_features_matrix[index]
        
        if (feature_cnt != feature_idx):
            feature_cnt = feature_cnt

    del user_feature_values_dict
    print("%s User ONLINE matrix (%d, %d)" % (getCurrentTime(), sample_cnt, feature_cnt))
    return user_features_matrix[:, 0:feature_cnt]
    

def create_user_offline_matrix(samples):
    user_distance_dict = g_feature_values["user_distance_dict"]
    
    feature_cnt = 3
    feature_idx = 0
    
    user_features_matrix = np.zeros((len(samples), 100))
    
    user_feature_values_dict = dict()
    
    sample_cnt = len(samples)
    
    for index in range(sample_cnt):
        user_id = samples[index][0]
        m_id = samples[index][1]

        if (user_id in user_feature_values_dict):
            user_features_matrix[index] = user_feature_values_dict[user_id]

            if (index % 10000 == 0):
                print("creating feature OFFLINE matrix, %d / %d handled\r" % (index, sample_cnt), end="")       
            continue            

        feature_idx = 0

        if (user_id not in user_distance_dict):
            if (index % 1000 == 0):
                print("%s creating user OFFLINE feature matrix, %d / %d handled\r" % (getCurrentTime(), index, sample_cnt), end="")
            continue

        # 用户线下使用优惠券距离商家的平均/最大/最小距离
        user_features_matrix[:, feature_idx] = len(user_distance_dict[user_id][0])/(sum(user_distance_dict[user_id][0]) + 1); feature_idx += 1
        user_features_matrix[:, feature_idx] = user_distance_dict[user_id][1]; feature_idx += 1
        user_features_matrix[:, feature_idx] = user_distance_dict[user_id][2]; feature_idx += 1

        if (index % 1000 == 0):
            print("%s creating user OFFLINE feature matrix, %d / %d handled\r" % (getCurrentTime(), index, sample_cnt), end="")

        user_feature_values_dict[user_id] = user_features_matrix[index] 
        
        if (feature_cnt != feature_idx):
            feature_cnt = feature_cnt

    print("%s User OFFLINE matrix (%d, %d)" % (getCurrentTime(), sample_cnt, feature_cnt))
    return user_features_matrix[:, 0:feature_cnt]    
    

def create_user_on_off_matrix(samples, on_off):    
    user_get_coupon_cnt_dict = g_feature_values["user_get_coupon_cnt_dict"] 
    user_coupon_days_diff_dict = g_feature_values["user_coupon_days_diff_dict"] 
    user_buy_cnt_with_coupon_dict = g_feature_values["user_buy_cnt_with_coupon_dict"] 
    user_buy_cnt_without_coupon_dict = g_feature_values["user_buy_cnt_without_coupon_dict"] 
    user_coupon_fraction_dict = g_feature_values["user_coupon_fraction_dict"]
    user_coupon_of_merchant_dict = g_feature_values["user_coupon_of_merchant_dict"] 
    user_coupon_weekday_dict = g_feature_values["user_coupon_weekday_dict"]
    
    # 特征矩阵
    feature_cnt = 32
    feature_idx = 0

    user_features_matrix = np.zeros((len(samples), 100))

    user_feature_values_dict = dict()

    sample_cnt = len(samples)

    for index in range(sample_cnt):
        user_id = samples[index][0]
        m_id = samples[index][1]

        if (user_id in user_feature_values_dict):
            user_features_matrix[index] = user_feature_values_dict[user_id]

            if (index % 10000 == 0):
                print("%s creating user ON/OFF feature matrix, %d / %d handled\r" % (getCurrentTime(), index, sample_cnt), end="")       
            continue            
        
        feature_idx = 0

        if (user_id not in user_get_coupon_cnt_dict):
            if (index % 10000 == 0):
                print("%s creating user ON/OFF feature matrix, %d / %d handled\r" % (getCurrentTime(), index, sample_cnt), end="")       
            continue
        
        # 用户领取优惠券的次数以及线上线下占总领取次数的比例
        user_features_matrix[index, feature_idx] = user_get_coupon_cnt_dict[user_id][on_off]; feature_idx += 1

        # 比例
        user_get_coupon_cnt_total = user_get_coupon_cnt_dict[user_id][on_off] + user_get_coupon_cnt_dict[user_id][on_off] + 1
        user_features_matrix[index, feature_idx] = user_get_coupon_cnt_dict[user_id][on_off]/user_get_coupon_cnt_total; feature_idx += 1

        # 用户从领取优惠券到使用之间的平均天数
        # 这里先计算总共的天数，然后再除以使用次数
        user_features_matrix[index, feature_idx] = user_coupon_days_diff_dict[user_id][on_off] / user_get_coupon_cnt_total

        # 用户使用优惠券消费的次数, 线上线下各占总使用次数的比例以及从领取优惠券到使用之间的平均天数
        user_features_matrix[index, feature_idx] = len(user_buy_cnt_with_coupon_dict[user_id][on_off]); feature_idx += 1
        # 比例
        user_buy_with_coupon_total = len(user_buy_cnt_with_coupon_dict[user_id][on_off]) + len(user_buy_cnt_with_coupon_dict[user_id][OFFLINE]) + 1
        user_features_matrix[index, feature_idx] = len(user_buy_cnt_with_coupon_dict[user_id][on_off])/user_buy_with_coupon_total; feature_idx += 1

        # 平均天数
        user_features_matrix[index, feature_idx] = \
            round(np.sum(user_buy_cnt_with_coupon_dict[user_id][on_off])/
                  (len(user_buy_cnt_with_coupon_dict[user_id][on_off]) + 1), 1); feature_idx += 1

        # 用户没有使用优惠券消费的次数
        user_features_matrix[index, feature_idx] = user_buy_cnt_without_coupon_dict[user_id][on_off]; feature_idx += 1
 
        # 用户使用 【0， 50】， 【51， 200】，【201， 500】， >500 的优惠券占使用优惠券的次数的比例
        user_features_matrix[index, feature_idx:feature_idx+4] = \
            user_coupon_fraction_dict[user_id][on_off][0]/ (len(user_buy_cnt_with_coupon_dict[user_id][on_off]) + 1); feature_idx += 4

        # 用户使用优惠券各个折扣率出现的次数  <=0.5, (0.5, 0.7], (0.7, 0.9], > 0.9
        user_features_matrix[index, feature_idx:feature_idx+4] = user_coupon_fraction_dict[user_id][on_off][1]; feature_idx += 4

        # 用户使用优惠券的平均折扣率 
        # sum(用户使用优惠券各个折扣率出现的次数 * 折扣率中值) /  用户使用优惠的次数
        discount_rate_mid = np.array([0.25, 0.6, 0.8, 0.95])
        user_features_matrix[index, feature_idx] =  \
            np.sum(user_coupon_fraction_dict[user_id][on_off][1] * discount_rate_mid) / (len(user_buy_cnt_with_coupon_dict[user_id][on_off])+ 1); feature_idx += 1 # + 1 是为了防止除 0

        # 用户使用优惠券的最高/最低折扣率
        user_features_matrix[index, feature_idx] = user_coupon_fraction_dict[user_id][on_off][2]; feature_idx += 1
        user_features_matrix[index, feature_idx] = user_coupon_fraction_dict[user_id][on_off][3]; feature_idx += 1

        # 用户在各个商家使用的优惠券的数量, 使用的优惠券的数量占领取的比例以及占该用户使用优惠券的比例
        if (m_id in user_coupon_of_merchant_dict[user_id]):
            user_features_matrix[index, feature_idx] = user_coupon_of_merchant_dict[user_id][m_id][on_off][1]; feature_idx += 1
            # 使用的,未使用的优惠券的数量占在该商家领取的比例
            user_total_get_c_from_m = user_coupon_of_merchant_dict[user_id][m_id][on_off][0] + user_coupon_of_merchant_dict[user_id][m_id][OFFLINE][0]
            user_total_use_c_of_m = user_coupon_of_merchant_dict[user_id][m_id][on_off][1] + user_coupon_of_merchant_dict[user_id][m_id][OFFLINE][1]
            user_features_matrix[index, feature_idx] = user_total_use_c_of_m / (user_total_get_c_from_m + 1); feature_idx += 1
            user_features_matrix[index, feature_idx] = 1 - user_total_use_c_of_m / (user_total_get_c_from_m + 1); feature_idx += 1
            # 占该用户 总的使用优惠券的比例
            user_features_matrix[index, feature_idx] = user_coupon_of_merchant_dict[user_id][m_id][on_off][1] / \
                                                       (len(user_buy_cnt_with_coupon_dict[user_id][on_off]) + 1); feature_idx += 1
        else:
            feature_idx += 4  # train， forecast 的feature 数量保持一致

        # 用户总共消费的次数（包括使用/未使用优惠券）
        user_features_matrix[:, feature_idx] = user_get_coupon_cnt_dict[user_id][on_off] + len(user_buy_cnt_with_coupon_dict[user_id][on_off]); feature_idx += 1 

        # 用户使用优惠券消费的次数占消费次数的比例
        user_total_buy_cnt_on_off = user_buy_cnt_without_coupon_dict[user_id][on_off] + len(user_buy_cnt_with_coupon_dict[user_id][on_off])
        user_features_matrix[:, feature_idx] = len(user_buy_cnt_with_coupon_dict[user_id][on_off]) / (user_total_buy_cnt_on_off + 1) ; feature_idx += 1

        # 用户没有使用优惠券消费的次数占消费次数的比例
        user_features_matrix[:, feature_idx] = user_buy_cnt_without_coupon_dict[user_id][on_off] / (user_total_buy_cnt_on_off + 1) ; feature_idx += 1

        # 用户使用优惠券消费的次数与没有使用次数的比值
        user_features_matrix[:, feature_idx] = len(user_buy_cnt_with_coupon_dict[user_id][on_off]) / \
                                               (user_buy_cnt_without_coupon_dict[user_id][on_off] + 1); feature_idx += 1 
        # 用户在一周内的第几天使用过几次优惠券
        user_features_matrix[:, feature_idx : feature_idx + 7] = user_coupon_weekday_dict[user_id][on_off]; feature_idx += 7

        if (index % 1000 == 0):
            print("%s creating user ON/OFF feature matrix, %d / %d handled\r" % (getCurrentTime(), index, sample_cnt), end="")

        user_feature_values_dict[user_id] = user_features_matrix[index] 
        
        if (feature_cnt != feature_idx):
            feature_cnt = feature_cnt
    
    del user_feature_values_dict

    print("%s User ON/OFF feature matrix (%d, %d)" % (getCurrentTime(), sample_cnt, feature_cnt))
    return user_features_matrix[:, 0:feature_cnt] 

def create_user_feature_matrix_ex(samples, on_off):
    if (on_off == BOTH):
        Xmat_1 = create_user_on_off_matrix(samples, ONLINE)
        Xmat_2 = create_user_on_off_matrix(samples, OFFLINE)        
        Xmat_3 = create_user_online_matrix(samples)
        Xmat_4 = create_user_offline_matrix(samples)

        feature_mat = np.column_stack((Xmat_1, Xmat_2, Xmat_3, Xmat_4))

        return feature_mat

    feature_mat = create_user_on_off_matrix(samples, on_off)
    if (on_off == ONLINE):
        Xmat = create_user_online_matrix(samples)
    else:
        Xmat = create_user_offline_matrix(samples)

    feature_mat = np.column_stack((feature_mat, Xmat))
    return feature_mat 
    
