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

    # add a regex listener wut the where_is_match function as the on_match
    # callback
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
      """
      on update we will remove any old data on the user
      insert a new doc with current data
      and then let the user know that we heardthem
      """
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

      body = "Enjoy" if status == 'out' else ("Back to Work" if status == 'in' else "No one bug {0}".format(user))
      self.pam.reply_msg(msg, body)

    elif match.re == self.where_is_re:
      """
      find the matching user name retrive there info and reply with that info
      """
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
      """ find everyone and reply with that info"""
      body = "Status' \n"
      for info in self.pam.db.where_is.find():
        timestr = self.relative_time(time.localtime(info['when']))
        body = "{0}{1} is {2} {3} as of {4}\n".format(body, info['user'], info['status'], info['details'], timestr)
      self.pam.reply_msg(msg, body)

    elif match.re == self.who_is_re:
      """ find the user that are in/out/dnd and reply with there info"""
      status = match.group(1)
      body = "Currently {0} \n".format(status)
      for info in self.pam.db.where_is.find({"status":status}):
        timestr = self.relative_time(time.localtime(info['when']))
        body = "{0}{1} is {2} {3} as of {4}\n".format(body, info['user'], info['status'], info['details'], timestr)
      self.pam.reply_msg(msg, body)


