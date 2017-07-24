'''
Created on Mar 8, 2017

@author: Heng.Zhang
'''

from global_var import *
from common import *
from utils import *


# 用户 --优惠券类型样本
# 在 expected_date_tup[0] - expected_date_tup[1] 期间使用过优惠券则作为正样本
# 在 expected_date_tup[0] - expected_date_tup[1] 期间领取过优惠券但没有使用则作为负样本  
#  每个样本都是一个tuple， 包含3项  (user_id, m_id, c_id)
def takeSamples(expected_date_tup, take_positive, users_on_off):
    print("taking samples (%s, %s), Taking %d smaples for %s" % \
          (expected_date_tup[0], expected_date_tup[1], take_positive, getOn_offStr(users_on_off)))
    samples = []

    for user_id, user_data_dict in g_user_merchant_dict.items():
        if (user_id not in g_users_for_algo[users_on_off]):
            continue

        for on_off, on_off_data_dict in user_data_dict.items(): 
            if (users_on_off != BOTH and on_off != users_on_off):
                continue

            for m_id in on_off_data_dict.keys():
                opt_tuples_dict = on_off_data_dict[m_id]
                for opt_tuple in opt_tuples_dict.keys():
                    action = opt_tuple[0]
                    c_id = opt_tuple[1]
                    discount_rate = opt_tuple[2]
                    min_charge = opt_tuple[3]
                    date_received = opt_tuple[4]
                    date = opt_tuple[5]
                    date_diff = opt_tuple[6]
                    if (take_positive):
                        if (date_diff is not None and date >= expected_date_tup[0] and date < expected_date_tup[1]): 
                            samples.append((user_id, m_id, c_id)) # date_diff 不为none说明用户使用了优惠券  
                    else:
                        # 负样本: 领取了优惠券但没有使用
                        if (date is None and c_id is not None and \
                            date_received >= expected_date_tup[0] and date_received < expected_date_tup[1]):
                                samples.append((user_id, m_id, c_id))
    if (take_positive):
        print("%s take %d Positive samples" % (getCurrentTime(), len(samples)))
        Y_lables = [1 for x in range(len(samples))]
    else:
        Y_lables = [0 for x in range(len(samples))]
        print("%s take %d Negative samples" % (getCurrentTime(), len(samples)))

    return samples, Y_lables

# (c_id, discount_rate, min_charge, distance, date_received)
# 每个sample 都是tuple，包括(user_id, m_id, c_id, date_received)
def takeSamplesForForecasting(users_on_off):
    samples = []
    for user_id, user_opt_dict in g_fcst_user_data_dict.items():
        for m_id, opt_tuple_cnt in user_opt_dict.items():
            for opt_tuple, tuple_cnt in opt_tuple_cnt.items():
                c_id = opt_tuple[0]
                date_received = opt_tuple[4]
                samples.append((user_id, m_id, c_id, date_received))
    
    print("%s takeSamplesForForecasting, here are %d smaples for forecasting" % (getCurrentTime(), len(samples)))
    return samples
