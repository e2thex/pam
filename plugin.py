import re
class Plugin(object):
  def __init__(self, pam):
    self.pam = pam
  def load(self): pass

  def add_watcher(self, watcher):
    self.pam.add_watcher(watcher)
  
class Watcher(object):
  def __init__(self,name, onMessage, for_me=None):
    self.name = name
    self.onMessage = onMessage

class RegexWatcher(Watcher):
  def __init__(self, name, regexes, on_match):
    self.name = name
    self.on_match = on_match
    self.regexes = regexes
  def onMessage(self, msg, data=None):
    if data:
      return self.on_match(None, msg, data)
    else:
      for regex in self.regexes:
        match = regex.search(str(msg.body));
        if match:
          return self.on_match(match, msg, data)
  
    


    

