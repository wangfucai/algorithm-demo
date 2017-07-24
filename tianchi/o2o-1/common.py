# coding=UTF-8
'''
Created on Mar 6, 2017

@author: Heng.Zhang
'''

from global_var import *
import csv
import datetime
import time
import numpy as np
from greenlet import getcurrent
from utils import *

def load_users(file_name, start_from, user_cnt, on_off):
    user_file_handle = open(r"%s\..\data\%s" % (runningPath, file_name), encoding="utf-8", mode='r')
    users = csv.reader(user_file_handle)

    index = 0
    for each_user in users:
        if (user_cnt > 0 and index < start_from):
            index += 1
            continue

        g_users_for_algo[on_off].add(each_user[0])
        index += 1
        if (user_cnt > 0 and index > (start_from + user_cnt)):
            break
    return

def should_read_data(date_received, date, date_diff, slide_win):
    # 如果是由contorller启动， 则slide_win不为空， 需判断日期是否在slide window 中
    if (slide_win is not None):

        # 如果是使用优惠券，则判断date 是否在[fcst_start, fcst_end)中
        if (date_diff is not None and (date >= slide_win[2] and date < slide_win[3])):
            return True

        # 如果购买没有使用优惠券，则判断date是否在[train_start, train_end) 中
        if (date_diff is None and date is not None and (date >= slide_win[0] and date < slide_win[1])):
            return True

        # date 为空则用date_received判断 是否在[train_start, train_end) 中
        if (date is None and (date_received >= slide_win[0] and date_received < slide_win[1])):
            return True

        return False

    return True

def load_ONLINE_data(slide_win, file_prefix, on_off):
    train_win_start, train_win_end, fcst_win_start, fcst_win_end = \
        datetime2Str(slide_win[0]), datetime2Str(slide_win[1]), datetime2Str(slide_win[2]), datetime2Str(slide_win[3])
        
    file_name = r"%s\..\data\slide_window\%s.%s.%s.%s.%s" % (runningPath, file_prefix, train_win_start, train_win_end, fcst_win_start, fcst_win_end)
    print("loading ONLINE %s" % file_name)

    online_file = open(file_name, encoding="utf-8", mode='r')

    user_behavior = csv.reader(online_file)

    index = 0

    for aline in user_behavior:
        if (index == 0):
            index += 1
            continue

        user_id = aline[0]

        if (user_id not in g_users_for_algo[on_off]):
            continue

        m_id = aline[1]
        action = int(aline[2])
        c_id = aline[3]
        if (len(c_id) == 0):
            c_id = None

        discount_rate = float(aline[4])
        min_charge = int(aline[5])

        date_received = transStr2Datetime(aline[6])
        date = transStr2Datetime(aline[7])

        date_diff = aline[8]
        if (len(date_diff) > 0):
            date_diff = int(date_diff)
        else:
            date_diff = None
        
        opt_tuple = (action, c_id, discount_rate, min_charge, date_received, date, date_diff)

        # user_id -- m_id
        if (user_id not in g_user_merchant_dict):
            g_user_merchant_dict[user_id] = dict()
            g_user_merchant_dict[user_id][ONLINE] = dict()
            g_user_merchant_dict[user_id][OFFLINE] = dict()

        if (m_id not in g_user_merchant_dict[user_id][ONLINE]):
            g_user_merchant_dict[user_id][ONLINE][m_id] = dict()

        if (opt_tuple not in g_user_merchant_dict[user_id][ONLINE][m_id]):
            g_user_merchant_dict[user_id][ONLINE][m_id][opt_tuple] = 1
        else:
            g_user_merchant_dict[user_id][ONLINE][m_id][opt_tuple] += 1

        # m_id -- user_id
        if (m_id not in g_merchant_user_dict):
            g_merchant_user_dict[m_id] = dict()
            g_merchant_user_dict[m_id][ONLINE] = dict()
            g_merchant_user_dict[m_id][OFFLINE] = dict()
            
        if (user_id not in g_merchant_user_dict[m_id][ONLINE]):
            g_merchant_user_dict[m_id][ONLINE][user_id] = dict()
            
        if (opt_tuple not in g_merchant_user_dict[m_id][ONLINE][user_id]):
            g_merchant_user_dict[m_id][ONLINE][user_id][opt_tuple] = 1
        else:
            g_merchant_user_dict[m_id][ONLINE][user_id][opt_tuple] += 1

        # c_id -- m_id
        if (c_id is not None):
            c_m_tuple = (c_id, m_id)
            if (c_m_tuple not in g_coupon_merchant_dict):
                g_coupon_merchant_dict[c_m_tuple] = dict()
                g_coupon_merchant_dict[c_m_tuple][ONLINE] = dict()
                g_coupon_merchant_dict[c_m_tuple][OFFLINE] = dict()
    
            if (opt_tuple in g_coupon_merchant_dict[c_m_tuple][OFFLINE]):
                g_coupon_merchant_dict[c_m_tuple][OFFLINE][opt_tuple] += 1
            else:
                g_coupon_merchant_dict[c_m_tuple][OFFLINE][opt_tuple] = 1

        index += 1
        if (index % 10000 == 0):
            print("%d lines read\r" % index, end="")

    
    return



def load_OFFLINE_data(slide_win, file_prefix, on_off):
    train_win_start, train_win_end, fcst_win_start, fcst_win_end = \
        datetime2Str(slide_win[0]), datetime2Str(slide_win[1]), datetime2Str(slide_win[2]), datetime2Str(slide_win[3])

    file_name = r"%s\..\data\slide_window\%s.%s.%s.%s.%s" % (runningPath, file_prefix, train_win_start, train_win_end, fcst_win_start, fcst_win_end)
    print("loading OFFLINE ", file_name)

    online_file = open(file_name, encoding="utf-8", mode='r')

    user_behavior = csv.reader(online_file)

    index = 0

    for aline in user_behavior:
        if (index == 0):
            index += 1
            continue

        user_id = aline[0]
        if (user_id not in g_users_for_algo[on_off]):
            continue

        m_id = aline[1]        
        c_id = aline[2]
        if (len(c_id) == 0):
            c_id = None

        discount_rate = float(aline[3])
        min_charge = int(aline[4])
        distance = int(aline[5])

        date_received = transStr2Datetime(aline[6])
        date = transStr2Datetime(aline[7])

        date_diff = aline[8]
        if (len(date_diff) > 0):
            date_diff = int(date_diff)
        else:
            date_diff = None
 
        opt_tuple = (distance, c_id, discount_rate, min_charge, date_received, date, date_diff)

        # user - m_id
        if (user_id not in g_user_merchant_dict):
            g_user_merchant_dict[user_id] = dict()
            g_user_merchant_dict[user_id][ONLINE] = dict()
            g_user_merchant_dict[user_id][OFFLINE] = dict()
        
        if (m_id not in g_user_merchant_dict[user_id][OFFLINE]):
            g_user_merchant_dict[user_id][OFFLINE][m_id] = dict()
        
        if (opt_tuple not in g_user_merchant_dict[user_id][OFFLINE][m_id]):
            g_user_merchant_dict[user_id][OFFLINE][m_id][opt_tuple] = 1
        else:
            g_user_merchant_dict[user_id][OFFLINE][m_id][opt_tuple] += 1

        # m_id -- user_id
        if (m_id not in g_merchant_user_dict):
            g_merchant_user_dict[m_id] = dict()
            g_merchant_user_dict[m_id][OFFLINE] = dict()
            g_merchant_user_dict[m_id][ONLINE] = dict()

        if (user_id not in g_merchant_user_dict[m_id][OFFLINE]):
            g_merchant_user_dict[m_id][OFFLINE][user_id] = dict()

        if (opt_tuple not in g_merchant_user_dict[m_id][OFFLINE][user_id]):
            g_merchant_user_dict[m_id][OFFLINE][user_id][opt_tuple] = 1
        else:
            g_merchant_user_dict[m_id][OFFLINE][user_id][opt_tuple] += 1

        # c_id -- m_id
        if (c_id is not None):
            c_m_tuple = (c_id, m_id)
            if (c_m_tuple not in g_coupon_merchant_dict):
                g_coupon_merchant_dict[c_m_tuple] = dict()
                g_coupon_merchant_dict[c_m_tuple][ONLINE] = dict()
                g_coupon_merchant_dict[c_m_tuple][OFFLINE] = dict()
    
            if (opt_tuple in g_coupon_merchant_dict[c_m_tuple][OFFLINE]):
                g_coupon_merchant_dict[c_m_tuple][OFFLINE][opt_tuple] += 1
            else:
                g_coupon_merchant_dict[c_m_tuple][OFFLINE][opt_tuple] = 1

        index += 1
        if (index % 10000 == 0):
            print("%d lines read\r" % index, end="")            

    return 0

def load_FORECAST_data(on_off):
    fcst_file = r"%s\..\data\ccf_offline_stage1_test_revised.csv" % (runningPath)
    print("%s loading FOECAST data %s" % (getCurrentTime(), fcst_file))
    fcst_file_handle = open(fcst_file, encoding="utf-8", mode='r')

    fcst_user_behavior = csv.reader(fcst_file_handle)

    index = 0

    for aline in fcst_user_behavior:
        if (index == 0):
            index += 1
            continue

        user_id = aline[0]

        m_id = aline[1]
        c_id = aline[2]
        discount_rate = aline[3]
        if (":" in discount_rate):
            m_d = aline[3].split(":")
            min_charge = int(m_d[0])
            discount_rate = float(m_d[1])
            discount_rate = 1 - round(discount_rate/min_charge, 2)
        else:
            discount_rate = float(discount_rate)
            min_charge = 0
        distance = aline[4]
        if (distance == 'null'):
            distance = None
        else:
            distance = int(distance)

        date_received = transStr2Datetime(aline[5])  

        if (user_id not in g_users_for_algo[on_off] or user_id not in g_user_merchant_dict):
            index += 1
            g_fcst_users_without_coupon.add((user_id, c_id, date_received))
            if (index % 10000 == 0):
                print("%d lines read\r" % index, end="")
            continue

        opt_tuple = (c_id, discount_rate, min_charge, distance, date_received)

        # user - m_id
        if (user_id not in g_fcst_user_data_dict):
            g_fcst_user_data_dict[user_id] = dict()
        
        if (m_id not in g_fcst_user_data_dict[user_id]):
            g_fcst_user_data_dict[user_id][m_id] = dict()
        
        if (opt_tuple not in g_fcst_user_data_dict[user_id][m_id]):
            g_fcst_user_data_dict[user_id][m_id][opt_tuple] = 1
        else:
            g_fcst_user_data_dict[user_id][m_id][opt_tuple] += 1

        # m_id -- user_id
        if (m_id not in g_fcst_merchant_data_dict):
            g_fcst_merchant_data_dict[m_id] = dict()

        if (user_id not in g_fcst_merchant_data_dict[m_id]):
            g_fcst_merchant_data_dict[m_id][user_id] = dict()

        if (opt_tuple not in g_fcst_merchant_data_dict[m_id][user_id]):
            g_fcst_merchant_data_dict[m_id][user_id][opt_tuple] = 1
        else:
            g_fcst_merchant_data_dict[m_id][user_id][opt_tuple] += 1

        # c_id -- m_id
        c_m_tuple = (c_id, m_id)
        if (c_m_tuple not in g_fcst_coupon_merchant_data_dict):
            g_fcst_coupon_merchant_data_dict[c_m_tuple] = dict()

        if (opt_tuple in g_fcst_coupon_merchant_data_dict[c_m_tuple]):
            g_fcst_coupon_merchant_data_dict[c_m_tuple][opt_tuple] += 1
        else:
            g_fcst_coupon_merchant_data_dict[c_m_tuple][opt_tuple] = 1

        index += 1
        if (index % 10000 == 0):
            print("%d lines read\r" % index, end="")    

    print("%s After loading forecast, here are %s %d users loaded" % (getCurrentTime(), getOn_offStr(on_off), len(g_fcst_user_data_dict)))
    return

def get_distount_type(discount_rate):
    if (discount_rate < 0.5):
        return 0       
    elif (discount_rate >= 0.5 and discount_rate < 0.7):
        return 1
    elif (discount_rate >= 0.7 and discount_rate < 0.9):
        return 2
    elif (discount_rate >= 0.9):
        return 3
    
    return -1


def get_min_charge_type(min_charge):
    if (min_charge < 50):
        return 0
    elif (min_charge >= 50 and min_charge < 200):
        return 1
    elif (min_charge >= 200 and min_charge < 500):
        return 2
    elif (min_charge >= 500):
        return 3
    
    return -1

def transStr2Datetime(str_date):
    if (len(str_date) > 0):
        return datetime.datetime.strptime(str_date, "%Y%m%d")
    else:
        return None

def datetime2Str(date):
    return "%d%02d%02d" % (date.year, date.month, date.day)
 
def getOn_offStr(on_off):
    if (on_off == ONLINE):
        return "ONLINE"
    
    if (on_off == OFFLINE):
        return "OFFLINE"
    
    if (on_off == BOTH):
        return "BOTH"
    
    return "UNKNOWN"

def cleanGlobalVar():
    g_user_merchant_dict.clear()
    g_merchant_user_dict.clear()
    g_coupon_merchant_dict.clear()

    g_fcst_user_data_dict.clear()
    g_fcst_merchant_data_dict.clear()
    g_fcst_coupon_merchant_data_dict.clear()
    return

if __name__ == '__main__':
    load_ONLINE_data(0, 0)
    load_OFFLINE_data(0, 0)    

    print("%s Here are total %d users, %d merchants" % (getCurrentTime(), len(g_user_merchant_dict), len(g_merchant_user_dict)))
