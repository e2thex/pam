import plugin
import re
import time

class Plugin(plugin.Plugin):
  def load(self):
    # Define regex as attr of self so we can see which one matched
    self.update_re = re.compile("^[Ii] am (out|in|dnd) ?(.*)$")
    self.where_is_re = re.compile("^[Ww]here is (.*)$")
    self.who_is_re = re.compile("^[Ww]ho is (out|in|dnd)$")
    self.where_is_everyone_re = re.compile("^[Ww]here is everyone$")
    self.add_listener(
      plugin.RegexListener(
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
      doc = {
        'user' : user,
        'status' : status,
        'details' : details,
        'when' : time.mktime(when)
      }
      self.pam.db.where_is.remove("user", user)
      self.pam.db.where_is.insert(doc)

      if status == 'out':
        self.pam.reply_msg(msg, "Enjoy")
      elif status == 'in':
        self.pam.reply_msg(msg, "Back to work")
      elif status == 'dnd':
        self.pam.reply_msg(msg, "No one bug {0}".format(user))
    elif match.re == self.where_is_re:
      user = match.group(1)
      print user
      info = self.pam.db.where_is.find_one({"user": user})
      if info:
        timestr = self.relative_time(time.localtime(info['when']))
        body = "{0} is {1} {2} as of {3}".format(user, info['status'], info['details'], timestr)
        self.pam.reply_msg(msg, body)
      else:
        self.pam.reply_msg(msg, "Sorry I don't know where {0} is.".format(user))
    elif match.re == self.where_is_everyone_re:
      body = "Status' \n"
      for info in self.pam.db.where_is.find():
        timestr = self.relative_time(time.localtime(info['when']))
        body = "{0}{1} is {2} {3} as of {4}\n".format(body, info['user'], info['status'], info['details'], timestr)
      self.pam.reply_msg(msg, body)
    elif match.re == self.who_is_re:
      status = match.group(1)
      body = "Currently {0} \n".format(status)
      for info in self.pam.db.where_is.find({"status":status}):
        timestr = self.relative_time(time.localtime(info['when']))
        body = "{0}{1} is {2} {3} as of {4}\n".format(body, info['user'], info['status'], info['details'], timestr)
      self.pam.reply_msg(msg, body)


  def relative_time(self, when):
    """ 
    take a struct time and compare it with now 
    if it is the same day give the time, 
    if the same week give the day of the week
    else give the time and date
    """
    now = time.localtime()
    if when[7] == now[7] :
      return time.strftime("%H:%M", when)
    elif when[7] > now[7] - 6:
      return time.strftime("%H:%M on %a", when) 
    else:
      return time.strftime("%H:%M on %m/%d", when) 
    
        
      

        
