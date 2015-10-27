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

    headrow = [("Date","scheduletitle"), ("Frequency","scheduletitle"), ("Intensity","scheduletitle")] + [(sdate,"scheduletitle") for sdate in sdates]

    routinedata = {}
    user        = users.get_current_user()
    allroutines = getallroutines(request,user.email())

    for routine in allroutines:
        routinedata[routine.name] = {}
        for daterange in dateranges:
            routinedata[routine.name][daterange] = getroutinestatus(routine,daterange)
        
    rows = [headrow] + [[(routine.name,"scheduleroutinename"), (str(getroutinedayfrequency(routine)),"scheduleroutinefrequency"), (str(routine.intensity),"scheduleroutineintensity")] + [(routinedata[routine.name][daterange],"scheduleroutine" + routinedata[routine.name][daterange]) for daterange in dateranges[:-1]] + [(htmlroutinetodaycheck(routine,dateranges[-1]),"scheduleroutinecheck")] for routine in allroutines]

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

        content = []
        if not user:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            content.append(htmllink(url,url_linktext))
        else:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            content.append(html("h1","Goals"))
            content.append(htmltable(htmlrows([[goal.name,goal.description] for goal in getallgoals(self,user.email())])))
            content.append(htmltable(htmlrow([buttonformget("/listgoals","List"), buttonformget("/addgoal","Add")])))
            content.append("<hr>")
            content.append(html("h1","Schedule"))
            content.append("Now is " + date2string(localnow()))
            content.append(htmltable(htmlrow([buttonformget("/last/month","Month"), buttonformget("/last/week","Week")])))
            content.append(htmlschedule(self,"week"))
            content.append("<hr>")
            content.append(htmltable(htmlrow([buttonformget("/logs","Logs")])))
            content.append("<hr>")
            content.append(htmllink(url,url_linktext))

        writehtmlresponse(handler,content)

class ScheduleHandler(webapp2.RequestHandler):
    def get(self,timetype):
        content = []
        content.append(html("h1","Schedule"))
        content.append("<hr>")
        content.append(htmltable(htmlrow([buttonformget("/last/month","Month"), buttonformget("/last/week","Week")])))
        content.append("<hr>")
        content.append(htmlschedule(self,timetype))
        content.append("<hr>")
        content.append(htmltable(htmlrow([buttonformget("/","Home")])))
        writehtmlresponse(handler,content)


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

class AddRoutineCheck(webapp2.RequestHandler):
    def post(self,routineid):
        
        routine = ndb.Key(urlsafe=routineid).get()
        
        currentdaterange = utcnowdayrange()

        routinechecks = getdateroutinechecks(routine.name,currentdaterange)

        if len(routinechecks):
            for routinecheck in routinechecks:
                routinecheck.key.delete()
            self.redirect("/")
        else:
            if routine.intensity == "None" or routine.intensity == None:
                addroutinecheck(self,routine.name)
                self.redirect("/")
            else:
                self.redirect("/addroutinecheckintensity/" + routineid)


class AddRoutineCheckIntensity(webapp2.RequestHandler):
    def get(self,routineid):
        
        routine = ndb.Key(urlsafe=routineid).get()
        
        content = []
        content.append(html("h1","Add routine check for routine " + routine.name))
        content.append(htmlform("/doaddroutinecheckintensity/" + routine.key.urlsafe(), 
                                     [htmltextarea("routinecheckvalue",0)], 
                                     "Submit"))
        content.append("<hr>")
        content.append(htmltable(htmlrow([buttonformget("/","Home")])))
        writehtmlresponse(self,content)



class DoAddRoutineCheckIntensity(webapp2.RequestHandler):
    def post(self,routineid):
        
        routine = ndb.Key(urlsafe=routineid).get()
        addroutinecheck(self,routine.name,self.request.get("routinecheckvalue"))
        self.redirect("/")



class Logs(webapp2.RequestHandler):
    def get(self):
        content = []
        content.append(html("h1","Logs"))
        content.append("<hr>")
        user = users.get_current_user()
        if user:
            rows = [[date2string(utc2local(routinecheck.date)),routinecheck.routinename,routinecheck.email] for routinecheck in getallroutinechecks(self,user.email())]
            # rows = [[date2string(utc2local(routinecheck.date)),routinecheck.routinename] for routinecheck in getallallroutinechecks(self)]
            content.append(htmltable(htmlrows(rows)))
        content.append("<hr>")
        content.append(htmltable(htmlrow([buttonformget("/","Home")])))
        writehtmlresponse(self,content)



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


handlers = [('/', MainHandler),('/logs', Logs), ('/last/(.*)', ScheduleHandler),('/addroutinecheck/(.*)', AddRoutineCheck), ('/addroutinecheckintensity/(.*)', AddRoutineCheckIntensity), ('/doaddroutinecheckintensity/(.*)', DoAddRoutineCheckIntensity)] + goalhandlers() + routinehandlers()

app = webapp2.WSGIApplication(handlers, debug=True)
