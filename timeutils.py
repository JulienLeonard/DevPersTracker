import datetime
from utils import *

def utc2local(date):
    return date + datetime.timedelta(hours=11)

def local2utc(date):
    return date - datetime.timedelta(hours=11)

def utcnow():
    return datetime.datetime.utcnow()

def localnow():
    # return datetime.datetime.now(pytz.timezone('Australia/Sydney'))
    return utc2local(utcnow())

def midnightdate(date):
    return datetime.datetime(date.year, date.month, date.day)

# def getlastdaymidnights(ndays):
#     today = datetoday()
#     dates = lreverse([today-datetime.timedelta(i) for i in range(ndays)])
#     dates = [midnightdate(date) for date in dates]
#     return dates

def getlastdaymidnightrangesutc(localtoday,ndays):
    utctoday          = local2utc(localtoday)
    lastlocalmidnight = datetime.datetime(localtoday.year, localtoday.month, localtoday.day)
    lastutcmidnight   = local2utc(lastlocalmidnight)

    dates = lreverse([utctoday] + [lastutcmidnight - datetime.timedelta(i) for i in range(ndays)])
    return [(d1,d2) for (d1,d2) in pairs(dates)]

def utcnowdayrange():
    localtoday        = localnow()
    lastlocalmidnight = datetime.datetime(localtoday.year, localtoday.month, localtoday.day)
    lastutcmidnight   = local2utc(lastlocalmidnight)
    return (lastutcmidnight,utcnow())


def sday(date):
    return date.strftime("%B")[0:3] + date.strftime("%d")

def date2string(date):
    return date.strftime("%a, %d %b %Y %H:%M:%S")

#def date2stringlocal(date):
#    return date2string(utc2local(date))

def isdateinrange(daterange,date):
    return daterange[0] <= date and date <= daterange[1]
