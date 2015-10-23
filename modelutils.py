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

def getroutinechecks(routinename):
    return RoutineCheck.query(RoutineCheck.routinename == routinename).fetch()

def getdateroutinechecks(routinename,utcdaterange):
    result = []
    for routinecheck in getroutinechecks(routinename):
        if isdateinrange(utcdaterange,routinecheck.date):
            result.append(routinecheck)
    return result

#
# can be NA, OK or KO
#
def getroutinestatus(routine,utcdaterange):
    routinechecks = getdateroutinechecks(routine.name,utcdaterange)
    if len(routinechecks):
            return "OK"
    else:
        if routine.status == "NA" or routine.date > utcdaterange[0]:
            return "NA"
        else:
            return "KO"


def getroutinedayfrequency(routine):
    if "every day" in routine.description:
        return 1
    if "every week" in routine.description:
        return 7
    if "every 2 days" in routine.description:
        return 2


