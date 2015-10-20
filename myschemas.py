from google.appengine.api import users
from google.appengine.ext import ndb

class Goal(ndb.Model):
    """A main model for representing a goal."""
    email         = ndb.StringProperty(indexed=True)
    name          = ndb.StringProperty(indexed=True)
    description   = ndb.StringProperty(indexed=False)
    parentgoal    = ndb.StringProperty(indexed=True)
    status        = ndb.StringProperty(indexed=True)
    date          = ndb.DateTimeProperty(auto_now_add=True)

class Routine(ndb.Model):
    """A main model for representing a routine."""
    email         = ndb.StringProperty(indexed=True)
    name          = ndb.StringProperty(indexed=True)
    description   = ndb.StringProperty(indexed=False)
    goalname      = ndb.StringProperty(indexed=True)
    status        = ndb.StringProperty(indexed=True)
    date          = ndb.DateTimeProperty(auto_now_add=True)

class RoutineCheck(ndb.Model):
    """A main model for representing a routine done."""
    email         = ndb.StringProperty(indexed=True)
    date          = ndb.DateTimeProperty(auto_now_add=True)
    routinename   = ndb.StringProperty(indexed=True)
    

