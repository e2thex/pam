import re
import datetime
class Plugin(object):
  def __init__(self, pam):
    self.pam = pam
  def load(self): pass

  def add_listener(self, listener):
    self.pam.add_listener(listener)
  
  def relative_time(self, when, now=None):
    """ 
    take a struct time and compare it with now 
    if it is the same day give the time, 
    if the same week give the day of the week
    else give the time and date
    """
    now = now if now else datetime.datetime.now()
    if now.date()== when.date():
      return when.strftime("%H:%M")
    elif (now - when) > datetime.timedelta( days = 6):
      return when.strftime("%H:%M on %a") 
    else:
      return when.strftime("%H:%M on %m/%d") 
    
        
      

        
class Listener(object):
  def __init__(self,name, onMessage, for_me=None):
    self.name = name
    self.onMessage = onMessage

class RegexListener(Listener):
  def __init__(self, name, description=None, usage=None, regexes = [], on_match = None):
    self.name = name
    self.on_match = on_match
    self.regexes = regexes
    self.description = description if description else ""
    self._usage = usage if usage else ""

  def usage(self):
    r = []
    for (use, note) in self._usage:
      use = use.ljust(20)
      r.append("{0} - {1}".format(use, note))
    return r

  def onMessage(self, msg, data=None):
    if data:
      match = re.compile("had data").search("had data")
      return self.on_match(match, msg, data)
    else:
      for regex in self.regexes:
        match = regex.search(str(msg.body));
        if match:
          return self.on_match(match, msg, data)
  
    


    

