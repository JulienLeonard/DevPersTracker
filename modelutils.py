from utils     import *
from myschemas import *
from mydicts   import *
from timeutils import *

def getgoal(goalname,email):
    goals_query = Goal.query(Goal.name == goalname).filter(Goal.email == email)
    qresult = goals_query.fetch(1)
    if len(qresult) > 0:
        return qresult[0]
    return None

def getallgoals(request,email):
    dict_name = request.request.get('dict_name', USERDICT)
    return Goal.query(ancestor=dict_key(dict_name)).filter(Goal.email == email).order(-Goal.date)


def getallroutines(request,email):
    dict_name = request.request.get('dict_name', USERDICT)
    return Routine.query(ancestor=dict_key(dict_name)).filter(Routine.email == email).order(-Routine.date)

def getallroutinechecks(request,email):
    dict_name = request.request.get('dict_name', USERDICT)
    return RoutineCheck.query(ancestor=dict_key(dict_name)).filter(RoutineCheck.email == email).order(-RoutineCheck.date)

def getallallroutinechecks(request):
    dict_name = request.request.get('dict_name', USERDICT)
    return RoutineCheck.query(ancestor=dict_key(dict_name)).order(-RoutineCheck.date)

def getroutines(goalname,email):
    return Routine.query(Routine.goalname == goalname).filter(Routine.email == email)

def getroutinechecks(routinename,allroutinecheckdata):
    # return RoutineCheck.query(RoutineCheck.routinename == routinename).fetch()
    # return [routinecheck for routinecheck in allroutinechecks if routinecheck.routinename == routinename]
    return [routinecheck for routinecheck in allroutinecheckdata if routinecheck[0] == routinename]

def getdateroutinechecks(routinename,allroutinecheckdata,utcdaterange):
    result = []
    for routinecheck in getroutinechecks(routinename,allroutinecheckdata):
        if isdateinrange(utcdaterange,routinecheck[1]):
            result.append(routinecheck)
    return result

#
# can be NA, OK or KO
#
def getroutinestatus(routine,allroutinecheckdata,utcdaterange):
    routinechecks = getdateroutinechecks(routine.name,allroutinecheckdata,utcdaterange)
    if len(routinechecks) > 0:
            return "OK"
    else:
        if routine.status == "NA" or routine.date > utcdaterange[0]:
            return "NA"
        else:
            # check frequency covering
            newutcdaterange = (utcdaterange[0] - datetime.timedelta(getroutinedayfrequency(routine)),utcdaterange[1])
            freqroutinechecks = getdateroutinechecks(routine.name,allroutinecheckdata,newutcdaterange)
            
            if len(freqroutinechecks) > 0:
                return "COVER"
            else:
                return "KO"


def getroutinedayfrequency(routine):
    if "every day" in routine.description:
        return 1
    if "every week" in routine.description:
        return 7
    if "every month" in routine.description:
        return 31
    if "every 2 days" in routine.description:
        return 2


def addroutinecheck(request,routinename,value="True"):
    user = users.get_current_user()
    if user:
        dict_name = request.request.get('dict_name', USERDICT)
        oroutinecheck = RoutineCheck(parent=dict_key(dict_name))
        oroutinecheck.routinename        = routinename
        oroutinecheck.email              = user.email()
        oroutinecheck.value              = value
        oroutinecheck.put()
    return oroutinecheck

def addroutinecheckdate(request,routinename,date,value):
    user = users.get_current_user()
    if user:
        dict_name = request.request.get('dict_name', USERDICT)
        oroutinecheck = RoutineCheck(parent=dict_key(dict_name))
        oroutinecheck.routinename        = routinename
        oroutinecheck.email              = user.email()
        oroutinecheck.date               = date
        oroutinecheck.value              = value
        oroutinecheck.put()
    return oroutinecheck
