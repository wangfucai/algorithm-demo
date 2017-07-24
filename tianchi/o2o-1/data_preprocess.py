'''
Created on Mar 3, 2017

@author: Heng.Zhang
'''


import csv
import datetime
import csv
from global_var import *
from common import *
from utils import *

def preprocess_onlinedata():
    print("pre-processing ONLINE data...")
    file_name = r"F:\doc\ML\TianChi\O2O\data\ccf_online_stage1_train.csv"
    filehandle1 = open(file_name, encoding="utf-8", mode='r')
    online_data = csv.reader(filehandle1)
    
    output_filename = r"F:\doc\ML\TianChi\O2O\data\pre_processed_ccf_online_stage1_train.csv"
    output_handle = open(output_filename, encoding="utf-8", mode='w')
    output_handle.write("User_id,Merchant_id,Action,Coupon_id,Discount_rate,Min_charge,Date_received,Date\n")
    
    index = 0
    
    for aline in online_data:
        if (index == 0):
            index += 1
            continue

        user_id = aline[0]
        m_id = aline[1]
        action = int(aline[2])
        c_id = aline[3]
        if (c_id == 'null'):
            c_id = ""

        discount = aline[4]
        min_charge = 0
        if (discount == 'null'):
            discount = 0
        elif (discount == 'fixed'):
            discount = -1
        else:
            min_charge, reduction = discount.split(":")
            min_charge = int(min_charge)
            reduction = int(reduction)
            discount = 1 - reduction/min_charge

        date_received = aline[5]
        if (date_received == 'null'):
            date_received = ""

        date = aline[6]
        if (date == 'null'):
            date = ""
            
        days_diff = ""
        if (len(date) > 0 and len(date_received) > 0):
            tmp1 = datetime.datetime.strptime(date, "%Y%m%d")
            tmp2 = datetime.datetime.strptime(date_received, "%Y%m%d")
            days_diff = (tmp1 - tmp2).days

        output_handle.write("%s,%s,%d,%s,%.2f,%d,%s,%s,%s\n" %(user_id, m_id, action, c_id, discount, min_charge, date_received, date, days_diff))
        
        index += 1
        if (index % 10000 == 0):
            print("%d lines read\r" % index, end="")

    output_handle.close()

    return 0


def preprocess_offlinedata():
    print("pre-processing OFFLINE data...")
    file_name = r"F:\doc\ML\TianChi\O2O\data\ccf_offline_stage1_train.csv"
    filehandle1 = open(file_name, encoding="utf-8", mode='r')
    online_data = csv.reader(filehandle1)

    output_filename = r"F:\doc\ML\TianChi\O2O\data\pre_processed_ccf_offline_stage1_train.csv"
    output_handle = open(output_filename, encoding="utf-8", mode='w')
    output_handle.write("User_id,Merchant_id,Coupon_id,Discount_rate,Min_charge,Distance,Date_received,Date\n")

    index = 0
    
    for aline in online_data:
        if (index == 0):
            index += 1
            continue

        user_id       = aline[0]
        m_id       = aline[1]
        c_id = aline[2]
        if (c_id == 'null'):
            c_id = ""
            
        discount_rate = aline[3]
        min_charge = 0
        if (discount_rate == 'null'):
            discount_rate = 0
        elif (discount_rate == 'fixed'):
            discount_rate = -1
        elif (discount_rate[0:2] == "0."):
            discount_rate = float(discount_rate)
        else:
            min_charge, reduction = discount_rate.split(":")
            min_charge = int(min_charge)
            reduction = int(reduction)
            discount_rate = 1 - reduction/min_charge
            
        distance = aline[4]
        if (distance == 'null'):
            distance = '-1'

        date_received = aline[5]
        if (date_received == 'null'):
            date_received = ""
        
        date = aline[6]
        if (date == 'null'):
            date = ""

        days_diff = ""
        if (len(date) > 0 and len(date_received) > 0):
            tmp1 = datetime.datetime.strptime(date, "%Y%m%d")
            tmp2 = datetime.datetime.strptime(date_received, "%Y%m%d")
            days_diff = (tmp1 - tmp2).days

        output_handle.write("%s,%s,%s,%.2f,%d,%s,%s,%s,%s\n" % \
                            (user_id, m_id, c_id, discount_rate, min_charge, distance, date_received, date, days_diff))

        index += 1
        if (index % 10000 == 0):
            print("%d lines read\r" % index, end="")

    output_handle.close()

    return 0


# 从online中删除没有领取过offline优惠券的用户
def preprecess_online_users_without_offline(offline_user_with_coupon):
    print("Here are total %d offline users" % len(offline_user_with_coupon))    
    online_file_handle = open("%s\\..\\data\\pre_processed_ccf_online_stage1_train.csv" % (runningPath), encoding="utf-8", mode='r')
    online_data = csv.reader(online_file_handle)
    index = 0

    online_with_offline_handle = open("%s\\..\\data\\pre_processed_online_with_offline_coupon.csv" % (runningPath), encoding="utf-8", mode='w')
    online_with_offline_handle.write("User_id,Merchant_id,Action,Coupon_id,Discount_rate,Min_charge,Date_received,Date,Day_diff\n")

    # reopen
    online_file_handle.close()
    online_file_handle = open("%s\\..\\data\\pre_processed_ccf_online_stage1_train.csv" % (runningPath), encoding="utf-8", mode='r')
    online_data = csv.reader(online_file_handle)
    removed_online_users = set()
    kept_online_users = set()
    index = 0
    for aline in online_data:
        if (index == 0):
            index += 1
            continue

        user_id = aline[0]
        if (user_id in offline_user_with_coupon):
            kept_online_users.add(user_id)
            online_with_offline_handle.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
                                             (aline[0],aline[1],aline[2],aline[3],aline[4],aline[5],aline[6],aline[7],aline[8]))
        else:
            removed_online_users.add(user_id)
        index += 1
        if (index % 10000 == 0):            
            print("%d online data read\r" % index, end="")

    print("Here are total %d online users removed, %d online users kept" % (len(removed_online_users), len(kept_online_users)))
    online_file_handle.close()
    online_with_offline_handle.close()

    return

# 从offline中删除所有从未领取过优惠券的用户
def remove_offline_users_without_coupon():
    data_file_handle = open(r"%s\..\data\pre_processed_ccf_offline_stage1_train.csv" % (runningPath), encoding="utf-8", mode='r')
    offline_users_data = csv.reader(data_file_handle)

    # 读取offline
    index = 0
    offline_user_with_coupon = set()
    for aline in offline_users_data:
        if (index == 0):
            index += 1
            continue

        user_id = aline[0]
        date_received = aline[6]
        date_diff = aline[8]
        if (len(date_diff) > 0):
            offline_user_with_coupon.add(user_id) 

        index += 1
        if (index % 10000 == 0):
            print("%d offline data read for getting coupon\r" % index, end="")

    print("Here are %s offline users with coupon" % (len(offline_user_with_coupon)))

    # reopen
    data_file_handle.close()
    data_file_handle = open(r"%s\..\data\pre_processed_ccf_offline_stage1_train.csv" % (runningPath), encoding="utf-8", mode='r')
    offline_users_data = csv.reader(data_file_handle)

    index = 0
    offline_users_with_coupon = set()
    removed_offline_users = set()
    
    offline_with_coupon_handle = open("%s\\..\\data\\pre_processed_offline_with_coupon.csv" % (runningPath), encoding="utf-8", mode='w')
    offline_with_coupon_handle.write("User_id,Merchant_id,Coupon_id,Discount_rate,Min_charge,Distance,Date_received,Date,Days_diff\n")
    
    for aline in offline_users_data:
        if (index == 0):
            index += 1
            continue

        user_id = aline[0]

        if (user_id in offline_user_with_coupon):
            offline_users_with_coupon.add(user_id)
            offline_with_coupon_handle.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
                                             (aline[0],aline[1],aline[2],aline[3],aline[4],aline[5],aline[6],aline[7],aline[8]))
        else:
            removed_offline_users.add(user_id)

        index += 1
        if (index % 10000 == 0):
            print("%d offline data read\r" % index, end="")

    print("here are %d offline users removed, %d offline users kept" % (len(removed_offline_users), len(offline_users_with_coupon)))

    offline_with_coupon_handle.close()
    data_file_handle.close()

    return offline_user_with_coupon

# 读取所有的用户
def extract_users(data_file_name):    
    print("%s loading file %s..." % (getCurrentTime(), data_file_name))
    data_file_handle = open(r"%s\..\data\%s" % (runningPath, data_file_name), encoding="utf-8", mode='r')
    user_behavior = csv.reader(data_file_handle)

    index = 0
    
    user_set = set()

    index = 0
    for aline in user_behavior:
        if (index == 0):
            index += 1
            continue

        user_id = aline[0]
        
        user_set.add(user_id)
        
        index += 1
        if (index % 10000 == 0):
            print("%d lines read\r" % index, end="")

    return user_set
    
    
def output_users_to_file(user_set, users_file_name):
    print("outputting ", users_file_name)
    users_file_output = open("%s\\..\\data\\%s" % (runningPath, users_file_name), encoding="utf-8", mode='w')
    index = 0
    for user_id in user_set:
        users_file_output.write("%s\n" % user_id)
        index += 1
        if (index % 10000 == 0):
            print("%d users output\r" % index, end="")

    return
    
# 将用户分成 只有online， 只有offline， on/off信息都有的 三类    
def split_users_by_on_off():
#     online_user_set = extract_users("pre_processed_ccf_online_stage1_train.csv")
#     offline_user_set = extract_users("pre_processed_ccf_offline_stage1_train.csv")
    
    online_user_set = extract_users("part_ccf_offline_stage1_train.csv")
    offline_user_set = extract_users("part_ccf_online_stage1_train.csv")
    
    users_only_online = online_user_set - offline_user_set
    users_only_offline = offline_user_set - online_user_set
    users_both_on_off = online_user_set & offline_user_set
    
    print("here %d ONLY-ONLIE users, %d ONLY-OFFLINE users, %d BOTH users " % \
          (len(users_only_online), len(users_only_offline), len(users_both_on_off)))

    output_users_to_file(users_only_online, "part_users_only_online.txt")
    output_users_to_file(users_only_offline, "part_users_only_offline.txt")
    output_users_to_file(users_both_on_off, "part_users_both_on_off.txt")
    
if __name__ == '__main__':
    split_users_by_on_off()
    


