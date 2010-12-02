import plugin
import re
import time

class Plugin(plugin.Plugin):
  def load(self):
    self.update_re = re.compile("^[Ii] am (out|in|dnd) ?(.*)$")
    self.where_is_re = re.compile("^[Ww]here is (.*)$")
    self.who_is_re = re.compile("^[Ww]ho is (out|in|dnd)$")
    self.where_is_everyone_re = re.compile("^[Ww]here is everyone$")
    self.add_watcher(
      plugin.RegexWatcher(
        name="repeat", 
        regexes = [
          self.update_re,
          self.where_is_everyone_re,
          self.where_is_re,
          self.who_is_re
          ],
        on_match = self.where_is_match
        )
      )
  def where_is_match(self, match, msg, data=None):
    if match.re == self.update_re:
      print match.groups
      (status, details) = match.groups()
      when = time.localtime()
      user = msg.pam['from'][0]
      if 'status' not in self.pam.data:
        self.pam.data['status'] = {}
      self.pam.data['status'][user] = (status, details, when)
      if status == 'out':
        self.pam.reply_msg(msg, "Enjoy")
      elif status == 'in':
        self.pam.reply_msg(msg, "Back to work")
      elif status == 'dnd':
        self.pam.reply_msg(msg, "No one bug {0}".format(user))
    if match.re == self.where_is_re:
      user = match.group(1)
      print user
      print self.pam.data
      if ('status' in self.pam.data) and (user in self.pam.data['status']):
        (status, details, when) = self.pam.data['status'][user]
        timestr = self.relative_time(when)
        body = "{0} is {1} {2} as of {3}".format(user, status, details, timestr)
        self.pam.reply_msg(msg, body)
    if match.re == self.where_is_everyone_re:
      body = "Status' \n"
      for (user, (status, details, when)) in self.pam.data['status'].iteritems():
        timestr = self.relative_time(when)
        body = "{0}{1} is {2} {3} as of {4}\n".format(body, user, status, details, timestr)
      self.pam.reply_msg(msg, body)
  def relative_time(self, when):
    now = time.localtime()
    if when[7] == now[7] :
      return time.strftime("%H:%M", when)
    elif when[7] > now[7] - 6:
      return time.strftime("%H:%M on %a", when) 
    else:
      return time.strftime("%H:%M on %m/%d", when) 
    
        
      

        
