from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

from goaltemplates    import *
from mydicts          import *
from myschemas        import *
from modelutils       import *
from htmlutils        import *
from utils            import *
from timeutils        import *

def goalhandlers():
    return [('/listgoals',       ListGoals),
            ('/addgoal',         AddGoal),
            ('/doaddgoal',       DoAddGoal),
            ('/deletegoal/(.*)', DeleteGoal),
            ('/viewgoal/(.*)',   ViewGoal)]

def addgoal(request,name,description):
    user = users.get_current_user()
    if user:
        dict_name = request.request.get('dict_name', USERDICT)
        ogoal = Goal(parent=dict_key(dict_name))
        ogoal.name        = name
        ogoal.description = description
        ogoal.status      = "TODO"
        ogoal.email       = user.email()
        ogoal.put()
    return ogoal
                
    
# [START ListGoal]
class ListGoals(webapp2.RequestHandler):
    def get(self):
        self.response.write('<html><body>')

        user = users.get_current_user()
        if user:
            rows = [[goal.name,goal.description,buttonformget("/viewgoal/" + goal.key.urlsafe(),"+"), buttonformget("/addroutine/" + goal.key.urlsafe(),"Add Routine"), buttonformpost("/deletegoal/" + goal.key.urlsafe(),"Del")] for goal in getallgoals(self,user.email())]
            content = htmltable(htmlrows(rows))
            self.response.write(LIST_GOAL_TEMPLATE % content)
        else:
            self.response.write('You must login')

        self.response.write('</body></html>')
# [END ListGoal]


# [START AddGoal]
class AddGoal(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user == None:
            self.response.write('<html><body>')
            self.response.write(ADD_GOAL_TEMPLATE)
            self.response.write('</body></html>')
        else:
            self.response.write('<html><body>Sorry, you must login to access this page</body></html>')
# [END AddGoal]

# [START DoAddGoal]
class DoAddGoal(webapp2.RequestHandler):
    def post(self):
        goalname           = self.request.get('goalname')
        goaldescription    = self.request.get('goaldescription')
        goal = addgoal(self,goalname,goaldescription)
        self.redirect("/listgoals")
# [END DoAddChiChar]

def deletegoal(request,goalid):
    goal_key = ndb.Key(urlsafe=goalid)
    goal     = goal_key.get()
    goal.key.delete()
    

# [START DeleteGoal]
class DeleteGoal(webapp2.RequestHandler):
    def post(self,goalid):
        deletegoal(self,goalid)
        self.redirect("/listgoals")

# [END DeleteGoal]


# [START ViewGoal]
class ViewGoal(webapp2.RequestHandler):
    def get(self,goalid):
        self.response.write('<html><body>')
        self.response.write(headcss())


        user = users.get_current_user()
        if user:
            dict_name      = self.request.get('dict_name',USERDICT)
            goal_key = ndb.Key(urlsafe=goalid)
            goal = goal_key.get()

            self.response.write(html("h1","Description"))

            self.response.write(htmltable( htmlrows( [ ["Name", goal.name],["Description", goal.description]])))

            self.response.write(html("h1","Routines"))

            self.response.write(htmltable(htmlrows( [ [routine.name, routine.description, routine.status, date2string(utc2local(routine.date))] for routine in getroutines(goal.name,user.email()) ] ) ) )

            self.response.write("<hr>")

            self.response.write(htmltable(htmlrow( [buttonformget("/addroutine/" + goal.key.urlsafe(),"Add Routine"), buttonformget("/listgoals","List"), buttonformget("/","Home")])))

        self.response.write('</body></html>')
