#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from maintemplates import *
from goals         import *
from routines      import *
from utils         import *
from htmlutils     import *
from modelutils    import *
from timeutils     import *
# import pytz



def htmlroutinetodaycheck(routine,utcdaterange):
    status = getroutinestatus(routine,utcdaterange)
    if status == "KO" or status == "NA":
        checklabel = "Check"
        return buttonformpost("/addroutinecheck/" + routine.key.urlsafe(), checklabel,"routinecheck")
    if status == "OK":
        checklabel = "Uncheck"
        return buttonformpost("/addroutinecheck/" + routine.key.urlsafe(), checklabel,"routineuncheck")
    return status


def tableschedule(request,ndays):
    
    # first compute the last seven days
    dateranges = getlastdaymidnightrangesutc(localnow(),ndays)

    sdates = [sday(utc2local(daterange[0])) for daterange in dateranges]

    headrow = [("Date","scheduletitle"), ("Frequency","scheduletitle")] + [(sdate,"scheduletitle") for sdate in sdates]

    routinedata = {}
    user        = users.get_current_user()
    allroutines = getallroutines(request,user.email())

    for routine in allroutines:
        routinedata[routine.name] = {}
        for daterange in dateranges:
            routinedata[routine.name][daterange] = getroutinestatus(routine,daterange)
        
    rows = [headrow] + [[(routine.name,"scheduleroutinename"), (str(getroutinedayfrequency(routine)),"scheduleroutinefrequency")] + [(routinedata[routine.name][daterange],"scheduleroutine" + routinedata[routine.name][daterange]) for daterange in dateranges[:-1]] + [(htmlroutinetodaycheck(routine,dateranges[-1]),"scheduleroutinecheck")] for routine in allroutines]

    return htmltable(htmldivrows(rows))

def getndays(timetype):
    if timetype == "week":
        return 7
    if timetype == "month":
        return 31

def htmlschedule(request,timetype):
    ndays = getndays(timetype)
    result = tableschedule(request,ndays)
    return result



class MainHandler(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()

        if not user:
            self.response.write('<body><html>')
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            self.response.write(htmllink(url,url_linktext))
            self.response.write('</html></body>')
        else:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            self.response.write('<body><html>')
            self.response.write(headcss())
            self.response.write(html("h1","Goals"))
            self.response.write(htmltable(htmlrows([[goal.name,goal.description] for goal in getallgoals(self,user.email())])))
            self.response.write(htmltable(htmlrow([buttonformget("/listgoals","List"), buttonformget("/addgoal","Add")])))
            self.response.write("<hr>")
            self.response.write(html("h1","Schedule"))
            self.response.write("Now is " + date2string(localnow()))
            self.response.write(htmltable(htmlrow([buttonformget("/last/month","Month"), buttonformget("/last/week","Week")])))
            self.response.write(htmlschedule(self,"week"))
            self.response.write("<hr>")
            self.response.write(htmltable(htmlrow([buttonformget("/logs","Logs")])))
            self.response.write("<hr>")
            self.response.write(htmllink(url,url_linktext))
            self.response.write('</html></body>')

class ScheduleHandler(webapp2.RequestHandler):
    def get(self,timetype):
        self.response.write('<body><html>')
        self.response.write(headcss())
        self.response.write(html("h1","Schedule"))
        self.response.write("<hr>")
        self.response.write(htmltable(htmlrow([buttonformget("/last/month","Month"), buttonformget("/last/week","Week")])))
        self.response.write("<hr>")
        self.response.write(htmlschedule(self,timetype))
        self.response.write("<hr>")
        self.response.write(htmltable(htmlrow([buttonformget("/","Home")])))
        self.response.write('</html></body>')

def addroutinecheck(request,routinename):
    user = users.get_current_user()
    if user:
        dict_name = request.request.get('dict_name', USERDICT)
        oroutinecheck = RoutineCheck(parent=dict_key(dict_name))
        oroutinecheck.routinename        = routinename
        oroutinecheck.email              = user.email()
        oroutinecheck.put()
    return oroutinecheck

class AddRoutineCheck(webapp2.RequestHandler):
    def post(self,routineid):
        
        routine = ndb.Key(urlsafe=routineid).get()
        
        currentdaterange = utcnowdayrange()

        routinechecks = getdateroutinechecks(routine.name,currentdaterange)

        if len(routinechecks):
            for routinecheck in routinechecks:
                routinecheck.key.delete()
        else:
            addroutinecheck(self,routine.name)
        
        self.redirect("/")

class Logs(webapp2.RequestHandler):
    def get(self):
        self.response.write('<body><html>')
        self.response.write(headcss())
        self.response.write(html("h1","Logs"))
        self.response.write("<hr>")
        user = users.get_current_user()
        if user:
            rows = [[date2string(utc2local(routinecheck.date)),routinecheck.routinename,routinecheck.email] for routinecheck in getallroutinechecks(self,user.email())]
            # rows = [[date2string(utc2local(routinecheck.date)),routinecheck.routinename] for routinecheck in getallallroutinechecks(self)]
            self.response.write(htmltable(htmlrows(rows)))
        self.response.write("<hr>")
        self.response.write(htmltable(htmlrow([buttonformget("/","Home")])))
        self.response.write('</html></body>')



# class UpgradeData(webapp2.RequestHandler):
#     def get(self):
#         user = users.get_current_user()
#         if user:
#             for routinecheck in getallallroutinechecks(self):
#                 routinecheck.email = user.email()
#                 routinecheck.put()
#             self.response.write('<body><html>')
#             self.response.write("DONE")
#             self.response.write('</html></body>')
#         else:
#             self.response.write('<body><html>')
#             self.response.write("Please login")
#             self.response.write('</html></body>')


handlers = [('/', MainHandler),('/logs', Logs), ('/last/(.*)', ScheduleHandler),('/addroutinecheck/(.*)', AddRoutineCheck)] + goalhandlers() + routinehandlers()


app = webapp2.WSGIApplication(handlers, debug=True)
