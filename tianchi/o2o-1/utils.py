'''
Created on Mar 21, 2017

@author: Heng.Zhang
'''

import csv
from global_var import *
from common import *
from dateutil.relativedelta import relativedelta
from concurrent.futures._base import RUNNING


ISOTIMEFORMAT="%Y-%m-%d %X"
def getCurrentTime():
    return time.strftime(ISOTIMEFORMAT, time.localtime())


# 滑动窗口, 每个窗口为6周， 用1，2，3，4周数据预测5，6周的行为
# 每次向后滑动 2 周, 每周以周日开始，周六结束
def create_slide_window():

    slide_windows = []

    # 源数据从20160101开始，不是一周对齐的，所以第一个窗口多加了几天
    train_win_start = datetime.datetime.strptime("20160101", "%Y%m%d")
    train_win_end = datetime.datetime.strptime("20160131", "%Y%m%d")

    fcst_win_start = datetime.datetime.strptime("20160131", "%Y%m%d") 
    fcst_win_end = fcst_win_start + relativedelta(weeks=2)

    slide_windows.append((train_win_start, train_win_end, fcst_win_start, fcst_win_end))
    
    train_win_start = datetime.datetime.strptime("20160117", "%Y%m%d")
    train_win_end = train_win_start + relativedelta(weeks=4)
    
    fcst_win_start = fcst_win_start+ relativedelta(weeks=2)        
    fcst_win_end = fcst_win_start + relativedelta(weeks=2)
    
    # 源数据中date_received只给到6-15号    
    last_std_win_end = datetime.datetime.strptime("20160522", "%Y%m%d")
    
    while train_win_end <= last_std_win_end:
        slide_windows.append((train_win_start, train_win_end, fcst_win_start, fcst_win_end))

        train_win_start = train_win_start + relativedelta(weeks=2)
        train_win_end = train_win_start + relativedelta(weeks=4)

        fcst_win_start = fcst_win_start+ relativedelta(weeks=2)        
        fcst_win_end = fcst_win_start + relativedelta(weeks=2)

    # 源数据中date_received只给到6-15号，所以最后一个窗口从 [5-22, 6-15), 预测为[6-15, 7-01)
    train_win_end = datetime.datetime.strptime("20160601", "%Y%m%d")
    fcst_win_start = datetime.datetime.strptime("20160601", "%Y%m%d")
    fcst_win_end = datetime.datetime.strptime("20160616", "%Y%m%d")
    slide_windows.append((train_win_start, train_win_end, fcst_win_start, fcst_win_end))

    return slide_windows


def splitDataBySlideWindow(slide_windows, source_file_name, output_file_prefix, file_header):
    
    online_file = r"%s\..\data\%s" % (runningPath, source_file_name)
    print("%s loading ONLINE data %s" % (getCurrentTime(), online_file))    
    online_file = open(online_file, encoding="utf-8", mode='r')
    user_behavior = csv.reader(online_file)

    index = 0

    slide_window_data_file = []
    for each_win in slide_windows:
        train_win_start, train_win_end, fcst_win_start, fcst_win_end = \
        datetime2Str(each_win[0]), datetime2Str(each_win[1]), datetime2Str(each_win[2]), datetime2Str(each_win[3])        
        outputFile = open(r"%s\..\data\slide_window\%s.%s.%s.%s.%s" % (runningPath, output_file_prefix, train_win_start, train_win_end, fcst_win_start, fcst_win_end), \
                          encoding="utf-8", mode='w')
        slide_window_data_file.append(outputFile)
        outputFile.write(file_header)

    for aline in user_behavior:
        if (index == 0):
            index += 1
            continue

        date_received = transStr2Datetime(aline[6])
        date = transStr2Datetime(aline[7])

        date_diff = aline[8]
        if (len(date_diff) > 0):
            date_diff = int(date_diff)
        else:
            date_diff = None

        for i, each_win in enumerate(slide_windows):
            if (should_read_data(date_received, date, date_diff, each_win)):                
                slide_window_data_file[i].write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
                                                (aline[0], aline[1], aline[2], aline[3], aline[4], aline[5], aline[6], aline[7], aline[8]))
        index += 1
        if (index % 10000 == 0):
            print("%s %d lines read\r" % (source_file_name, index), end="")
            
    for each_file in slide_window_data_file:
        each_file.close()

    return

def splitDataBySlideWindowWarper():
    slide_windows = create_slide_window()
    splitDataBySlideWindow(slide_windows, 
                           "pre_processed_online_with_offline_coupon.csv", 
                           "pre_processed_online_with_offline_coupon", 
                           "User_id,Merchant_id,Action,Coupon_id,Discount_rate,Min_charge,Date_received,Date,Day_diff\n")
    
    splitDataBySlideWindow(slide_windows, 
                           "pre_processed_offline_with_coupon.csv", 
                           "pre_processed_offline_with_coupon", 
                           "User_id,Merchant_id,Coupon_id,Discount_rate,Min_charge,Distance,Date_received,Date,Days_diff")
    return

def checkFcstUsersOnline():
    fcst_file = r"%s\..\data\ccf_offline_stage1_test_revised.csv" % (runningPath)
    print("%s loading FOECAST data %s" % (getCurrentTime(), fcst_file))
    fcst_file_handle = open(fcst_file, encoding="utf-8", mode='r')

    fcst_user_behavior = csv.reader(fcst_file_handle)

    index = 0
    
    fcst_users = set()

    for aline in fcst_user_behavior:
        if (index == 0):
            index += 1
            continue

        user_id = aline[0]
        
        fcst_users.add(user_id)
        
    load_users("users_only_online.txt", 0, 0, ONLINE)
    
    fcst_users_in_online = fcst_users - g_users_for_algo[ONLINE]
    return


if __name__ == '__main__':
    print("utils")
    
    splitDataBySlideWindowWarper()
