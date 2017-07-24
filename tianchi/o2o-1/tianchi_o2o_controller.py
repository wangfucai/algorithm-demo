
import subprocess  
import os
import time
import sys
import datetime
import csv
import logging
from common import *
from dateutil.relativedelta import relativedelta
from global_var import *
from utils import *

runningPath = sys.path[0]
sys.path.append("%s\\samples\\" % runningPath)


def waitSubprocesses(runningSubProcesses):
    for start_from_user_cnt in runningSubProcesses:
        sub = runningSubProcesses[start_from_user_cnt]
        ret = subprocess.Popen.poll(sub)
        if ret == 0:
            logging.info("subprocess (%s, %s) ended" % (start_from_user_cnt[0], start_from_user_cnt[1]))
            runningSubProcesses.pop(start_from_user_cnt)
            return start_from_user_cnt
        elif ret is None:
            time.sleep(1) # running
        else:
            logging.info("subprocess (%s, %s) terminated" % (start_from_user_cnt[0], start_from_user_cnt[1]))
            runningSubProcesses.pop(start_from_user_cnt)
            return start_from_user_cnt
    return (None, None)


def submiteOneSubProcess(each_slide_win):
    train_win_start = each_slide_win[0]
    train_win_end = each_slide_win[1]
    fcst_win_start = each_slide_win[2]
    fcst_win_end = each_slide_win[3]
    
    cmdLine = "python tianchi_o2o.py train_win_start=%s train_win_end=%s fcst_win_start=%s fcst_win_end=%s" % \
              (datetime2Str(train_win_start), datetime2Str(train_win_end), datetime2Str(fcst_win_start), datetime2Str(fcst_win_end))

    sub = subprocess.Popen(cmdLine, shell=True)
    runningSubProcesses[(train_win_start, train_win_end)] = sub
    logging.info("running %s" % cmdLine)
    time.sleep(1)
    return

##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################

logging.basicConfig(level=logging.INFO,\
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
                    datefmt='%a, %d %b %Y %H:%M:%S',\
                    filename='..\\log\\controller.txt',\
                    filemode='w')

slide_windows = create_slide_window()
runningSubProcesses = {}
for each_slide_win in slide_windows:
    submiteOneSubProcess(each_slide_win)
    logging.info("after submiteOneSubProcess, runningSubProcesses len is %d" % len(runningSubProcesses))
    if (len(runningSubProcesses) == 10):
        while True:
            finished_start_from_user_cnt = waitSubprocesses(runningSubProcesses)
            if ((finished_start_from_user_cnt[0] is not None and finished_start_from_user_cnt[1] is not None)):
                logging.info("after waitSubprocesses, runningSubProcesses len is %d" % len(runningSubProcesses))
                break
            if (len(runningSubProcesses) == 0):
                break
 
while True:
    start_from_user_cnt = waitSubprocesses(runningSubProcesses)
    if (start_from_user_cnt[0] is not None and start_from_user_cnt[1] is not None):
        logging.info("after waitSubprocesses, runningSubProcesses len is %d" % len(runningSubProcesses))
    if len(runningSubProcesses) == 0:
        break

forecasted_user_item_prob = dict()

prediction_by_subporcess = {}

str_today = datetime2Str(datetime.date.today())

for each_slide_win in slide_windows:
    train_win_start= datetime2Str(each_slide_win[0])
    train_win_end = datetime2Str(each_slide_win[1])
    file_idx = 0
    output_file_name = output_filename_fmt % (runningPath, train_win_start, train_win_end, str_today, file_idx)
    
    # 找到 file_index 最大的文件
    while (os.path.exists(output_file_name)):
        file_idx += 1
        output_file_name = output_filename_fmt % (runningPath, train_win_start, train_win_end, str_today, file_idx)

    file_idx -= 1
    output_file_name = output_filename_fmt % (runningPath, train_win_start, train_win_end, str_today, file_idx)
    if (not os.path.exists(output_file_name)):
        print("WARNNING: output file does not exist! %s" % output_file_name)
        continue

    print("reading (%s, %s), %s" % (train_win_start, train_win_end, output_file_name))
    filehandle = open(output_file_name, encoding="utf-8", mode='r')
    csv_reader = csv.reader(filehandle)

    index = 0
    for i, aline in enumerate(csv_reader):
        if (i == 0):
            continue

        user_id       = aline[0]
        c_id          = aline[1]
        date_received = aline[2]
        fcst_proba    = float(aline[3])
        
        fcst_tup = (user_id, c_id, date_received)
        if (fcst_tup not in prediction_by_subporcess):
            prediction_by_subporcess[fcst_tup] = []
        
        prediction_by_subporcess[fcst_tup].append(fcst_proba)


file_idx = 0
output_file_name = "%s\\..\\output\\forecast.%s.%d.csv" % (runningPath, str_today, file_idx)

while (os.path.exists(output_file_name)):
    file_idx += 1
    output_file_name = "%s\\..\\output\\forecast.%s.%d.csv" % (runningPath, str_today, file_idx)

print("output forecast file %s" % output_file_name)
outputFile = open(output_file_name, encoding="utf-8", mode='w')
outputFile.write("User_id,Coupon_id,Date_received,Probability\n")

for fcst_tup, proba_by_subprocess in prediction_by_subporcess.items():
    user_id       = fcst_tup[0]
    c_id          = fcst_tup[1]
    date_received = fcst_tup[2]
    fcst_proba = np.mean(proba_by_subprocess)
    outputFile.write("%s,%s,%s,%s\n" % (user_id, c_id, date_received, str(fcst_proba)))


outputFile.close()

print("%s Done!" % (getCurrentTime()))