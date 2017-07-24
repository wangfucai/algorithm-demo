# coding=UTF-8
'''
Created on Mar 8, 2017

@author: Heng.Zhang
'''
from common import *
from takingsamples import *
from utils import *
from feature_creation import *
from sklearn.utils import shuffle
import logging
import os
from utils import *

from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.cross_validation import StratifiedKFold 
from sklearn.grid_search import GridSearchCV

from sklearn.metrics import roc_curve, auc  


def train_with_slide_window(slide_windows, on_off):
    models = []
    for each_window in slide_windows:        
        train_win_start = each_window[0]
        train_win_end = each_window[1]
        fcst_start = each_window[2]
        fcst_end = each_window[3]
        
        cleanGlobalVar()
        
        print("==========================================")
        print("traing slide window (%s, %s), (%s, %s), %s" % \
              (datetime2Str(train_win_start), datetime2Str(train_win_end), datetime2Str(fcst_start), datetime2Str(fcst_end), getOn_offStr(on_off)))
        print("==========================================")

        load_OFFLINE_data(each_window, "pre_processed_offline_with_coupon", on_off)
        load_ONLINE_data(each_window, "pre_processed_online_with_offline_coupon", on_off)
        load_FORECAST_data(on_off)
        print("%s Total %d %s users loaded" % (getCurrentTime(), len(g_user_merchant_dict), getOn_offStr(on_off)))    
        
        expected_date_tup = (train_win_start, train_win_end)

        positive_samples, Y_pos_lab = takeSamples((fcst_start, fcst_end), True, on_off)
        nagetive_samples, Y_nag_lab = takeSamples(expected_date_tup, False, on_off)
        if (len(positive_samples) == 0 or len(nagetive_samples) == 0):
            print("WARNNING: No +/- samples (%d, %d) on (%s, %s)" % (len(positive_samples), len(nagetive_samples), fcst_start, fcst_end))
            continue

        samples = []
        samples.extend(positive_samples)
        samples.extend(nagetive_samples)

        Y_lables = []
        Y_lables.extend(Y_pos_lab)
        Y_lables.extend(Y_nag_lab)

        Y_lables, samples = shuffle(Y_lables, samples, random_state=13)
        create_feature_values(expected_date_tup, samples, on_off)

        X_feature_mat = createFeatureMatrixEx(samples, on_off)

        print("%s Training model..." % (getCurrentTime()))
        gbdt_gs_params = {"n_estimators":[500], "max_depth":[7], "learning_rate":[0.1], "loss":["deviance"]}
        clf = GradientBoostingClassifier(n_estimators=500, max_depth=7, learning_rate=0.1, loss="deviance")
        clf.fit(X_feature_mat, Y_lables)
        models.append(clf)
        
#         clf_gc = GridSearchCV(clf, gbdt_gs_params, n_jobs=-1, cv=5)
#         clf_gc.fit(X_feature_mat, Y_lables)
#         models.append(clf_gc.best_estimator_)
#         logging.info("slide window (%s, %s), (%s, %s), best params: %s" % (datetime2Str(train_win_start), datetime2Str(train_win_end), \
#                      datetime2Str(fcst_start), datetime2Str(fcst_end), clf_gc.best_params_))

    return models

def run_for_submission(slide_windows, on_off):
    
    slide_models = train_with_slide_window(slide_windows, on_off)

    print("%s Creating samples for forecasting..." % (getCurrentTime()))
    submission_train_date = (datetime.datetime.strptime("20160601", "%Y%m%d"), datetime.datetime.strptime("20160630", "%Y%m%d"))   
    samples_fcst = takeSamplesForForecasting(on_off)
    if (len(samples_fcst) == 0):
        print("Here are no forecasting samples for ", getOn_offStr(on_off))
        return []

    create_feature_values(submission_train_date, samples_fcst, on_off)
    X_feature_fcst_mat = createFeatureMatrixEx(samples_fcst, on_off)
    fcst_prob_mat = np.zeros((len(samples_fcst), len(slide_models)))

    print("%s Forecasting..." % (getCurrentTime()))    
    for i, each_model in enumerate(slide_models):
        fcst_prob_mat[:, i] = each_model.predict_proba(X_feature_fcst_mat)[:, 1]

    fcst_proba = np.mean(fcst_prob_mat, axis=1)

    prediction_on_off = []
    for idx, each_smp in enumerate(samples_fcst):
        user_id = each_smp[0]
        c_id = each_smp[2]
        date_received = each_smp[3]
        prediction_on_off.append((user_id, c_id, date_received, fcst_proba[idx]))
  
    return prediction_on_off

def run_for_local_test(on_off):
    print("%s run_for_local_test running..." % (getCurrentTime()))

    slide_windows = create_slide_window()
    slide_models = train_with_slide_window(slide_windows[0 : len(slide_windows)-1], on_off) # 本地测试用最后一个窗口做验证
    local_test_window = slide_windows[-1]

    positive_samples, Y_pos_lab = takeSamples((local_test_window[2], local_test_window[3]), True, on_off)
    nagetive_samples, Y_nag_lab = takeSamples((local_test_window[2], local_test_window[3]), False, on_off)

    samples = []
    samples.extend(positive_samples)
    samples.extend(nagetive_samples)

    Y_lables = []
    Y_lables.extend(Y_pos_lab)
    Y_lables.extend(Y_nag_lab)

    Y_lables, samples = shuffle(Y_lables, samples, random_state=13)
    
    expected_date_tup = (local_test_window[0], local_test_window[1])    
    create_feature_values(expected_date_tup, samples)
    
    X_feature_fcst_mat = createFeatureMatrixEx(samples, on_off)
    
    fcst_prob_mat = np.zeros((len(samples), len(slide_models)))
    
    for i, each_model in enumerate(slide_models):
        fcst_prob_mat[:, i] = each_model.predict_proba(X_feature_fcst_mat)[:, 1]

    fcst_proba = np.mean(fcst_prob_mat, axis=1)

    fcst_proba2 = []
    fcst_proba2.extend(fcst_proba)

    for i in g_fcst_users_without_coupon:
        Y_lables.append(0)
        fcst_proba2.append(0.0)

    fpr, tpr, thresholds = roc_curve(Y_lables, fcst_proba2)

    roc_auc = auc(fpr, tpr)

    print("%s auc" % (getCurrentTime()), roc_auc)    
    return Y_lables, fcst_proba

def create_feature_values(expected_date_tup, samples, on_off):
    g_feature_values.clear()

    g_feature_values["user_get_coupon_cnt_dict"], \
    g_feature_values["user_buy_cnt_with_coupon_dict"], \
    g_feature_values["user_buy_cnt_without_coupon_dict"], \
    g_feature_values["user_coupon_fraction_dict"],\
    g_feature_values["user_coupon_days_diff_dict"], \
    g_feature_values["user_coupon_of_merchant_dict"], \
    g_feature_values["user_distance_dict"], \
    g_feature_values["user_opt_online_dict"], \
    g_feature_values["user_coupon_weekday_dict"] = create_user_feature_value(expected_date_tup, samples, on_off)

    g_feature_values["coupon_cnt_dict"] = create_coupon_feature_values(expected_date_tup, samples)

    g_feature_values["merchant_coupon_cnt_dict"], \
    g_feature_values["merchant_coupon_discount_dict"], \
    g_feature_values["merchant_distance_dict"], \
    g_feature_values["merchant_online_opt_dict"] = create_merchant_feature_values(expected_date_tup, samples, on_off)
    return

if __name__ == '__main__':
    train_win_start = sys.argv[1].split("=")[1]
    train_win_end = sys.argv[2].split("=")[1]
    fcst_win_start = sys.argv[3].split("=")[1]
    fcst_win_end = sys.argv[4].split("=")[1]
    log_file = "%s\\..\\log\\by_controller.%s.%s.txt" % (runningPath, train_win_start, train_win_end)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=log_file,
                        filemode='w')
    print("tianchi_o2o is running with (%s, %s, %s, %s)" % (train_win_start, train_win_end, fcst_win_start, fcst_win_end))

    train_win_start = transStr2Datetime(train_win_start)
    train_win_end = transStr2Datetime(train_win_end)
    fcst_win_start = transStr2Datetime(fcst_win_start)
    fcst_win_end = transStr2Datetime(fcst_win_end)

    slide_windows = [(train_win_start, train_win_end, fcst_win_start, fcst_win_end)]

    submission = 1
    if (submission == 1):
#         load_users("users_only_online.txt", 0, 0, ONLINE)
        load_users("users_only_offline.txt", 0, 0, OFFLINE)
        load_users("users_both_on_off.txt", 0, 0, BOTH)
        print("here are %d OFFLINE users, %d BOTH users" % (len(g_users_for_algo[OFFLINE]), len(g_users_for_algo[BOTH])))

        prediction = []
#         prediction_on = run_for_submission(slide_windows, ONLINE)
        prediction_both = run_for_submission(slide_windows, BOTH)
        prediction_off = run_for_submission(slide_windows, OFFLINE)

#         prediction.extend(prediction_on)
        prediction.extend(prediction_off)
        prediction.extend(prediction_both)

        file_idx = 0
        output_file_name = output_filename_fmt % \
                           (runningPath, datetime2Str(slide_windows[0][0]), datetime2Str(slide_windows[-1][1]), \
                            datetime2Str(datetime.date.today()), file_idx)
        while (os.path.exists(output_file_name)):
            file_idx += 1
            output_file_name = output_filename_fmt % \
                               (runningPath, datetime2Str(slide_windows[0][0]), datetime2Str(slide_windows[-1][1]), \
                                datetime2Str(datetime.date.today()), file_idx)

        print("%s outputting %s" % (getCurrentTime(), output_file_name))
        output_fcst_file = open(output_file_name, encoding="utf-8", mode='w')
        output_fcst_file.write("User_id,Coupon_id,Date_received,Probability\n")
        for each_smp in prediction:
            user_id = each_smp[0]
            c_id = each_smp[1]
            date_received = each_smp[2]
            fcst_proba = each_smp[3]

            output_fcst_file.write("%s,%s,%s,%s\n" % (user_id, c_id, datetime2Str(date_received), str(fcst_proba)))

        for each_rmed_user in g_fcst_users_without_coupon:
            user_id = each_rmed_user[0]
            c_id = each_rmed_user[1]
            date_received = each_rmed_user[2]
            output_fcst_file.write("%s,%s,%d%02d%02d,0.0\n" % \
                                   (user_id, c_id, date_received.year, date_received.month, date_received.day))

        output_fcst_file.close()            
    else:
        load_users("users_only_online.txt", 0, 5000, ONLINE)
        load_users("users_only_offline.txt", 0, 5000, OFFLINE)
        load_users("users_both_on_off.txt", 0, 5000, BOTH)
    
        Y_on, proba_on= run_for_local_test(ONLINE)
        Y_off, proba_off= run_for_local_test(OFFLINE)
        Y_both, proba_both = run_for_local_test(BOTH)
        
    
    
    
    
