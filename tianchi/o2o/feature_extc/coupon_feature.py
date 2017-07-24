import datetime


def str2time(str_time):
    d = datetime.date(int(str_time[: 4]), int(str_time[4: 6]), int(str_time[6:]))
    return d
