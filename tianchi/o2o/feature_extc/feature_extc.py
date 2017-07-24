import datetime
import pickle


def str2time(str_time):
    d = datetime.date(int(str_time[: 4]), int(str_time[4: 6]), int(str_time[6:]))
    return d


def day_duration(sd1, sd2):
    d1 = str2time(sd1)
    d2 = str2time(sd2)
    return (d2 - d1).days


def cal_relative_value(pt, t_l, u_l):
    relative_v_l = []
    for i in range(len(u_l)):
        t = t_l[i]
        u = u_l[i]
        relative_v_d = {}
        for key in t.keys():
            if t[key] < 100:
                continue
            relative_v = u.get(key, 0) / t[key] - pt
            relative_v_d[key] = relative_v
        relative_v_l.append(relative_v_d)
    return relative_v_l


def read_file(file_name):
    file_data = open(file_name, 'r')
    file_text = file_data.readlines()[:]
    print(file_text[0], file_text[5])
    total_num = 0
    consum_num = 0
    user_total = {}
    user_use = {}
    merchant_total = {}
    merchant_use = {}
    discount_total = {}
    discount_use = {}
    distance_total = {}
    distance_use = {}
    for line in file_text[1:]:
        cols = line.strip().split(',')
        user_id = cols[0]
        merchant_id = cols[1]
        discount_rate = cols[3]
        distance = cols[4]

        if cols[-2] != 'null':
            total_num += 1
            user_total.setdefault(user_id, 0)
            user_total[user_id] += 1
            merchant_total.setdefault(merchant_id, 0)
            merchant_total[merchant_id] += 1
            discount_total.setdefault(discount_rate, 0)
            discount_total[discount_rate] += 1
            distance_total.setdefault(distance, 0)
            distance_total[distance] += 1

        if cols[-2] != 'null' and cols[-1] != 'null' and day_duration(cols[-2], cols[-1]) <= 15:
            consum_num += 1
            user_use.setdefault(user_id, 0)
            user_use[user_id] += 1
            merchant_use.setdefault(merchant_id, 0)
            merchant_use[merchant_id] += 1
            discount_use.setdefault(discount_rate, 0)
            discount_use[discount_rate] += 1
            distance_use.setdefault(distance, 0)
            distance_use[distance] += 1
    file_data.close()
    p_t = consum_num / total_num
    receive_t = [user_total, merchant_total, discount_total, distance_total]
    receive_u = [user_use, merchant_use, discount_use, distance_use]
    c_l = cal_relative_value(p_t, receive_t, receive_u)
    return c_l


def read_file2(file_name):
    file_data = open(file_name, 'r')
    file_text = file_data.readlines()[:]
    print(file_text[0], file_text[5])
    total_num = 0
    consum_num = 0
    user_total = {}
    user_use = {}
    merchant_total = {}
    merchant_use = {}
    discount_total = {}
    discount_use = {}

    for line in file_text[1:]:
        cols = line.strip().split(',')
        user_id = cols[0]
        merchant_id = cols[1]
        discount_rate = cols[4]

        if cols[-2] != 'null':
            total_num += 1
            user_total.setdefault(user_id, 0)
            user_total[user_id] += 1
            merchant_total.setdefault(merchant_id, 0)
            merchant_total[merchant_id] += 1
            discount_total.setdefault(discount_rate, 0)
            discount_total[discount_rate] += 1

        if cols[-2] != 'null' and cols[-1] != 'null' and day_duration(cols[-2], cols[-1]) <= 15:
            consum_num += 1
            user_use.setdefault(user_id, 0)
            user_use[user_id] += 1
            merchant_use.setdefault(merchant_id, 0)
            merchant_use[merchant_id] += 1
            discount_use.setdefault(discount_rate, 0)
            discount_use[discount_rate] += 1

    file_data.close()
    p_t = consum_num / total_num
    receive_t = [user_total, merchant_total, discount_total]
    receive_u = [user_use, merchant_use, discount_use]
    c_l = cal_relative_value(p_t, receive_t, receive_u)
    return c_l


def extc_feature():
    c_l = read_file('C:/Users/WangFuCai/PycharmProjects/DecisionTree/tianchi/o2o/data/ccf_offline_stage1_train.csv')
    c_l2 = read_file2('C:/Users/WangFuCai/PycharmProjects/DecisionTree/tianchi/o2o/data/ccf_online_stage1_train.csv')
    c_l.extend(c_l2)
    try:
        feature_v_f = open('C:/Users/WangFuCai/PycharmProjects/DecisionTree/tianchi/o2o/data/feature_values', 'wb')
        pickle.dump(c_l, feature_v_f)
    except Exception as e:
        print(e)
    finally:
        feature_v_f.close()
