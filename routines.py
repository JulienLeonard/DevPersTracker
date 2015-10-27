from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

from routinetemplates    import *
from mydicts          import *
from myschemas        import *
from modelutils       import *
from htmlutils        import *
from utils            import *

def routinehandlers():
    return [('/listroutines',       ListRoutines),
            ('/addroutine/(.*)',    AddRoutine),
            ('/doaddroutine/(.*)',  DoAddRoutine),
            ('/deleteroutine/(.*)', DeleteRoutine),
            ('/viewroutine/(.*)',   ViewRoutine),
            ('/editroutine/(.*)',   EditRoutine),
            ('/doeditroutine/(.*)',   DoEditRoutine)]

def addroutine(request,name,description,goalname):
    user = users.get_current_user()
    if user:
        dict_name = request.request.get('dict_name', USERDICT)
        oroutine = Routine(parent=dict_key(dict_name))
        oroutine.name        = name
        oroutine.description = description
        oroutine.goalname    = goalname
        oroutine.status      = "TODO"
        oroutine.email       = user.email()
        oroutine.put()
        return oroutine
                
    
# [START ListRoutine]
class ListRoutines(webapp2.RequestHandler):
    def get(self):
        self.response.write('<html><body>')
        user = users.get_current_user()
        if user:
            rows = [[routine.name,routine.description,routine.goalname,buttonformget("/viewroutine/" + routine.key.urlsafe(),"+"), buttonformpost("/deleteroutine/" + routine.key.urlsafe(),"Del")] for routine in getallroutines(self,user.email())]
            content = htmltable(htmlrows(rows))
            self.response.write(LIST_ROUTINE_TEMPLATE % content)

        self.response.write('</body></html>')
# [END ListRoutine]


# [START AddRoutine]
class AddRoutine(webapp2.RequestHandler):
    def get(self,goalid):
        user = users.get_current_user()
        if not user == None:
            self.response.write('<html><body>')
            self.response.write(ADD_ROUTINE_TEMPLATE % goalid)
            self.response.write('</body></html>')
        else:
            self.response.write('<html><body>Sorry, you must login to access this page</body></html>')
# [END AddRoutine]

# [START DoAddRoutine]
class DoAddRoutine(webapp2.RequestHandler):
    def post(self,goalid):
        dict_name      = self.request.get('dict_name',USERDICT)
        goal_key = ndb.Key(urlsafe=goalid)
        goal = goal_key.get()
        routinename           = self.request.get('routinename')
        routinedescription    = self.request.get('routinedescription')
        routine = addroutine(self,routinename,routinedescription,goal.name)
        self.redirect("/listroutines")
# [END DoAddChiChar]

def deleteroutine(request,routineid):
    routine_key = ndb.Key(urlsafe=routineid)
    routine     = routine_key.get()
    routine.key.delete()
    

# [START DeleteRoutine]
class DeleteRoutine(webapp2.RequestHandler):
    def post(self,routineid):
        deleteroutine(self,routineid)
        self.redirect("/listroutines")

# [END DeleteRoutine]


# [START ViewRoutine]
class ViewRoutine(webapp2.RequestHandler):
    def get(self,routineid):

        content = []

        dict_name   = self.request.get('dict_name',USERDICT)
        routine_key = ndb.Key(urlsafe=routineid)
        routine     = routine_key.get()

        content.append(html("h1","Routine " + routine.name))
        content.append("<hr>")
        content.append(htmltable( htmlrows( [ ["Name", routine.name],["Description", routine.description],["Frequency", getroutinedayfrequency(routine)],["Intensity",routine.intensity],["Goal", routine.goalname]])))
        content.append("<hr>")
        content.append(htmltable(htmlrow( [buttonformget("/editroutine/" + routine.key.urlsafe(),"Edit"), buttonformget("/listroutines","List"), buttonformget("/","Home")])))
        writehtmlresponse(self,content)



# [START EditRoutine]
class EditRoutine(webapp2.RequestHandler):
    def get(self,routineid):

        content = []

        dict_name   = self.request.get('dict_name',USERDICT)
        routine_key = ndb.Key(urlsafe=routineid)
        routine     = routine_key.get()

        content.append(html("h1","Routine " + routine.name))
        content.append("<hr>")
        content.append(htmlform("/doeditroutine/" + routine.key.urlsafe(), 
                                     [routine.name, htmltextarea("routinedescription",routine.description), htmltextarea("routineintensity",str(routine.intensity))], 
                                     "Submit"))
        content.append("<hr>")
        content.append(htmltable(htmlrow( [buttonformget("/viewroutine/" + routine.key.urlsafe(),"Cancel"), buttonformget("/","Home")])))
        writehtmlresponse(self,content)

# [START DoEditRoutine]
class DoEditRoutine(webapp2.RequestHandler):
    def post(self,routineid):

        dict_name   = self.request.get('dict_name',USERDICT)
        routine_key = ndb.Key(urlsafe=routineid)
        routine     = routine_key.get()

        routine.description = self.request.get('routinedescription')
        routine.intensity   = self.request.get('routineintensity')
        routine.put()

        self.redirect("/viewroutine/" + routine.key.urlsafe())
