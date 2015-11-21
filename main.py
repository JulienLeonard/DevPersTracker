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



def htmlroutinetodaycheck(routine,allroutinecheckdata,utcdaterange,routinename = False):
    status = getroutinestatus(routine,allroutinecheckdata,utcdaterange)
    if status == "KO" or status == "NA" or status == "COVER":
        checklabel = iff(routinename == False,"Check",routine.name)
        classbutton = iff(status == "KO","routinecheck","routinecheckoptional")
        return buttonformpost("/addroutinecheck/" + routine.key.urlsafe(), checklabel,classbutton)
    if status == "OK":
        checklabel = iff(routinename == False,"Uncheck",routine.name)
        return buttonformpost("/addroutinecheck/" + routine.key.urlsafe(), checklabel,"routineuncheck")
    return status

def htmlroutinetodaycheckform(routine,allroutinecheckdata,utcdaterange):
    if not(routine.intensity == "None" or routine.intensity == None):
        return htmlroutinetodaycheck(routine,allroutinecheckdata,utcdaterange)

    status = getroutinestatus(routine,allroutinecheckdata,utcdaterange)

    if status == "KO" or status == "NA" or status == "COVER":
        classbutton = iff(status == "KO","routinecheck","routinecheckoptional")
        checked     = "" 
    if status == "OK":
        classbutton = "routineuncheck"
        checked = "checked"
    return "<div class=\"" + classbutton + "\"><input type=\"checkbox\" class=\"" + classbutton + "\" name=\"check" + routine.name + "\" value=\"DONE\"" + checked + ">" + routine.name + "<br></div>"


def tableschedule(request,ndays):
    
    # first compute the last seven days
    dateranges = getlastdaymidnightrangesutc(localnow(),ndays)

    sdates = [sday(utc2local(daterange[0])) for daterange in dateranges]

    headrow = [("Date","scheduletitle"), ("Frequency","scheduletitle"), ("Intensity","scheduletitle"), ("+","scheduletitle")] + [(sdate,"scheduletitle") for sdate in sdates]

    routinedata = {}
    user        = users.get_current_user()
    allroutines         = getallroutines(request,user.email())
    allroutinechecks    = getallroutinechecksndays(request,user.email(),ndays)
    allroutinecheckdata = [(routinecheck.routinename,routinecheck.date) for routinecheck in allroutinechecks]
    

    for routine in allroutines:
        routinedata[routine.name] = {}
        for daterange in dateranges:
            routinedata[routine.name][daterange] = getroutinestatus(routine,allroutinecheckdata,daterange)
        
    rows = [headrow] + [[(routine.name,"scheduleroutinename"), (str(getroutinedayfrequency(routine)),"scheduleroutinefrequency"), (str(routine.intensity),"scheduleroutineintensity"),(buttonformget("/viewroutine/" + routine.key.urlsafe(),"+"),"scheduleroutineview")] + [(routinedata[routine.name][daterange],"scheduleroutine" + routinedata[routine.name][daterange]) for daterange in dateranges[:-1]] + [(htmlroutinetodaycheck(routine,allroutinecheckdata,dateranges[-1]),"scheduleroutinecheck")] for routine in allroutines]

    return htmltable(htmldivrows(rows))

def getndays(timetype):
    if timetype == "week":
        return 8
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
        url = users.create_login_url(self.request.uri)
        if not user:
            url_linktext = 'Login'
            content.append(htmllink(url,url_linktext))
        else:
            content.append(html("h1","Schedule"))
            content.append("Now is " + date2string(localnow()))
            content.append(htmltable(htmlrow([buttonformget("/dashboard","Dashboard"),buttonformget("/last/month","Month"), buttonformget("/last/week","Week")])))
            content.append(htmlschedule(self,"week"))
            content.append("<hr>")
            content.append(htmltable(htmlrow([buttonformget("/listgoals","Goals"), buttonformget("/listroutines","Routines"),buttonformget("/logs","Logs"),buttonformget("/export","Exports")])))
            content.append("<hr>")
            url_linktext = 'Logout'
            content.append(htmllink(url,url_linktext))
        
        content = htmlcenter(content)
        writehtmlresponse(self,content)

class ScheduleHandler(webapp2.RequestHandler):
    def get(self,timetype):
        content = []
        content.append(html("h1","Schedule"))
        content.append("<hr>")
        content.append(htmltable(htmlrow([buttonformget("/dashboard","Dashboard"),buttonformget("/last/month","Month"), buttonformget("/last/week","Week")])))
        content.append("<hr>")
        content.append(htmlschedule(self,timetype))
        content.append("<hr>")
        content.append(htmltable(htmlrow([buttonformget("/","Home")])))
        writehtmlresponse(self,content)

class Dashboard(webapp2.RequestHandler):
    def get(self):
        content = []
        content.append(html("h1","Dashboard"))
        content.append("<hr>")
        content.append(htmltable(htmlrow([buttonformget("/dashboard","Dashboard"),buttonformget("/last/month","Month"), buttonformget("/last/week","Week")])))
        content.append("<hr>")

        user        = users.get_current_user()
        allgoals            = getallgoals(self,user.email())
        allroutines         = getallroutines(self,user.email())
        allroutinechecks    = getallroutinecheckstoday(self,user.email())
        allroutinecheckdata = [(routinecheck.routinename,routinecheck.date) for routinecheck in allroutinechecks]
        
        dateranges = getlastdaymidnightrangesutc(localnow(),1)

        content.append(htmltable(htmldivrows([[(goal.name,"schedulegoal")] + [(htmlroutinetodaycheck(routine,allroutinecheckdata,dateranges[-1],True),"scheduleroutinecheck") for routine in getroutines(goal.name,user.email())]  for goal in allgoals])))

        content.append("<hr>")
        content.append(htmltable(htmlrow([buttonformget("/","Home")])))
        writehtmlresponse(self,content)

def checkroutines(routines):
    result = []
    for routine in routines:
        if routine.intensity == "None" or routine.intensity == None:
            result.append(routine)
    return result

def valueroutines(routines):
    result = []
    for routine in routines:
        if not(routine.intensity == "None" or routine.intensity == None):
            result.append(routine)
    return result

class Dashboard2(webapp2.RequestHandler):
    def get(self):
        content = []
        content.append(html("h1","Dashboard"))
        content.append("<hr>")
        content.append(htmltable(htmlrow([buttonformget("/dashboard","Dashboard"),buttonformget("/last/month","Month"), buttonformget("/last/week","Week")])))
        content.append("<hr>")

        user                = users.get_current_user()
        allgoals            = getallgoals(self,user.email())
        allroutines         = getallroutines(self,user.email())
        allroutinechecks    = getallroutinecheckstoday(self,user.email())
        allroutinecheckdata = [(routinecheck.routinename,routinecheck.date) for routinecheck in allroutinechecks]
        
        dateranges = getlastdaymidnightrangesutc(localnow(),1)

        content.append(htmltable(htmldivrows([[(goal.name,"schedulegoal")] + [(htmlroutinetodaycheck(routine,allroutinecheckdata,dateranges[-1],True),"scheduleroutinecheck") for routine in valueroutines(getroutines(goal.name,user.email()))]  for goal in allgoals])))

        content.append("<hr>")

        content.append("<form action=\"postdashboard2\" method=\"post\">")
        content.append(htmltable(htmldivrows([[(goal.name,"schedulegoal")] + [(htmlroutinetodaycheckform(routine,allroutinecheckdata,dateranges[-1]),"scheduleroutinecheck") for routine in checkroutines(getroutines(goal.name,user.email()))]  for goal in allgoals])))
        content.append("<input type=\"submit\" class=\"formsubmit\" value=\"Submit\"></form>")

        content.append("<hr>")

        content.append(htmltable(htmlrow([buttonformget("/","Home")])))
        writehtmlresponse(self,content)

class PostDashboard2(webapp2.RequestHandler):
    def post(self):
        user                = users.get_current_user()
        allgoals            = getallgoals(self,user.email())
        allroutines         = getallroutines(self,user.email())
        dateranges          = getlastdaymidnightrangesutc(localnow(),1)
        allroutinechecks    = getallroutinecheckstoday(self,user.email())
        allroutinecheckdata = [(routinecheck.routinename,routinecheck.date,routinecheck) for routinecheck in allroutinechecks]
        
        content = ""
        for routine in allroutines:
            if routine.intensity == "None" or routine.intensity == None:
                routinenewstatus = self.request.get( "check" + routine.name)
                routinechecks    = getdateroutinechecks(routine.name,allroutinecheckdata,dateranges[-1])

                if len(routinenewstatus) == 0:
                    for routinecheck in routinechecks:
                        routinecheck[2].key.delete()
                else:
                    if routine.intensity == "None" or routine.intensity == None:
                        addroutinecheck(self,routine.name)

        self.redirect("/dashboard")

class AddRoutineCheck(webapp2.RequestHandler):
    def post(self,routineid):
        
        routine = ndb.Key(urlsafe=routineid).get()
        
        currentdaterange = utcnowdayrange()

        user = users.get_current_user()
        if user:
            allroutinechecks = getallroutinecheckstoday(self,user.email())
            allroutinecheckdata = [(routinecheck.routinename,routinecheck.date,routinecheck) for routinecheck in allroutinechecks]
            routinechecks       = getdateroutinechecks(routine.name,allroutinecheckdata,currentdaterange)

            if len(routinechecks):
                for routinecheck in routinechecks:
                    routinecheck[2].key.delete()
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

def serialize(ldata):
    return ";".join([str(data) for data in ldata])

class Export(webapp2.RequestHandler):
    def get(self):
        content = []
        content.append(html("h1","Export"))
        content.append("<hr>")
        user = users.get_current_user()
        if user:
            content.append(html("h2","Goals"))
            for goal in getallgoals(self,user.email()):
                content.append(htmldiv(serialize([goal.email,goal.name,goal.description,goal.parentgoal,goal.status,goal.date])))
            content.append(html("h2","Routines"))
            for routine in getallroutines(self,user.email()):
                content.append(htmldiv(serialize([routine.email,routine.name,routine.description,routine.goalname,routine.status,routine.intensity,routine.date])))
            content.append(html("h2","RoutineChecks"))
            for routinecheck in getallroutinechecks(self,user.email()):
                content.append(htmldiv(serialize([routinecheck.email,routinecheck.date,routinecheck.routinename,routinecheck.value])))
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


handlers = [('/', MainHandler),('/dashboard', Dashboard2),('/postdashboard2', PostDashboard2),('/logs', Logs),('/export', Export), ('/last/(.*)', ScheduleHandler),('/addroutinecheck/(.*)', AddRoutineCheck), ('/addroutinecheckintensity/(.*)', AddRoutineCheckIntensity), ('/doaddroutinecheckintensity/(.*)', DoAddRoutineCheckIntensity)] + goalhandlers() + routinehandlers()

app = webapp2.WSGIApplication(handlers, debug=True)
