from utils     import *
from myschemas import *
from mydicts   import *

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





