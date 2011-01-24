import plugin
import re
import time
from dateutil.parser import *
from datetime import datetime, timedelta

class Plugin(plugin.Plugin):
  def load(self):
    # Define regex as attr of self so we can see which one matched
    self.update_re = re.compile("^[Ii] am (out|in|dnd) ?(.*)$")
    self.where_is_re = re.compile("^[Ww]here is (.*)$")
    self.who_is_re = re.compile("^[Ww]ho is (out|in|dnd)$")
    self.where_is_everyone_re = re.compile("^[Ww]here is everyone$")
    self.where_was_i_re = re.compile("^[wW]here was [iI] ?(.*)$")
    self.track_re = re.compile("^[Tt]rack (.*)$")
    self.track_stop_re = re.compile("^[Ss]top [Tt]racking (.*)$")
    self.track_stop_all_re = re.compile("^[Ss]top [Tt]racking [Aa]ll$")
    self.track_who_re = re.compile("^([Ww]ho am [iI] tracking|tracking)\??$")

    # add a regex listener wut the where_is_match function as the on_match
    # callback
    self.add_listener(
      plugin.RegexListener(
        name="where is", 
        description="You can ask me what other people are doing, also tell me what you are up to, then I can tell others.",
        usage= [
          ("i am in / out / dnd MESSAGE", 'For example try saying: "i am in working on wilson center" Also, dnd means "do not disturb".'),
          ("where is PERSON", "I can tell you where a certain person is"),
          ("who is in / out / dnd", "I'll tell you statuses for everyone with a certain status"),
          ("where is everyone", "I'll tell you what everyone is doing"),
          ("where was i", "I'll tell you all of your previous status")
          ],
        regexes = [
          self.update_re,
          self.where_is_everyone_re,
          self.where_is_re,
          self.who_is_re,
          self.where_was_i_re,
          self.track_who_re,
          self.track_re,
          self.track_stop_all_re,
          self.track_stop_re
          ],
        on_match = self.where_is_match
        )
      )
  def where_is_match(self, match, msg, data=None):
    if match.re == self.update_re:
      """ on update we will remove any old data on the user
      insert a new doc with current data
      and then let the user know that we heardthem
      """
      (status, details) = match.groups()
      user = msg.pam['from'][0]
      doc = {
        'user' : user,
        'status' : status,
        'details' : details,
        'when' : datetime.now(),
        'current' : True
      }
      self.pam.db.where_is.update({"user": user}, {'$set':{'current':False}}, multi=True)
      self.pam.db.where_is.insert(doc)

      body = "Enjoy" if status == 'out' else ("Back to Work" if status == 'in' else "No one bug {0}".format(user))

      for info in self.pam.db.where_is_track.find({"trackee":user}):
        timestr = self.relative_time(doc['when'])
        notify_body = "{0} is {1} {2} as of {3}".format(user, doc['status'], doc['details'], timestr)
        self.pam.send_msg(msg['to'], info['notify_jid'], 'chat', notify_body)
        body = "{0}\nnotifed {1}".format(body, info['tracker'])

      self.pam.reply_msg(msg, body)

    elif match.re == self.where_is_re:
      """ find the matching user name retrive there info and reply with that info
      """
      user = match.group(1)
      print user
      info = self.pam.db.where_is.find_one({"user": user, 'current':True})
      if info:
        timestr = self.relative_time(info['when'])
        body = "{0} is {1} {2} as of {3}".format(user, info['status'], info['details'], timestr)
        self.pam.reply_msg(msg, body)
      else:
        self.pam.reply_msg(msg, "Sorry I don't know where {0} is.".format(user))

    elif match.re == self.where_is_everyone_re:
      """ find everyone and reply with that info"""
      body = "Status' \n"
      for info in self.pam.db.where_is.find({'current':True}):
        timestr = self.relative_time(info['when'])
        body = "{0}{1} is {2} {3} as of {4}\n".format(body, info['user'], info['status'], info['details'], timestr)
      self.pam.reply_msg(msg, body)

    elif match.re == self.where_was_i_re:
      user = msg.pam['from'][0]
      if match.group(1):
       print match.group(1)
       try:
         day = parse(match.group(1))
       except Exception as e:
         pass
       else:
         end = day + timedelta(days=1)
         infos = self.pam.db.where_is.find({"user": user, "when":{'$gte':day, '$lt': end}})
      else :
        infos = self.pam.db.where_is.find({"user": user})
      body = "You have:\n"
      for info in infos:
        timestr = self.relative_time(info['when'])
        body = "{0}I {1} {2} {3} as of {4}\n".format(body, "am" if info['current'] else "was", info['status'], info['details'], timestr)
      self.pam.reply_msg(msg, body)
      
    elif match.re == self.who_is_re:
      """ find the user that are in/out/dnd and r eply with there info"""
      status = match.group(1)
      body = "Currently {0} \n".format(status)
      for info in self.pam.db.where_is.find({"status":status}):
        timestr = self.relative_time(info['when'])
        body = "{0}{1} is {2} {3} as of {4}\n".format(body, info['user'], info['status'], info['details'], timestr)
      self.pam.reply_msg(msg, body)
    elif match.re == self.track_re:
      trackee = match.group(1)
      tracker = msg.pam['from'][0]
      doc = {
        'trackee' : trackee,
        'tracker' : tracker,
        'notify_jid': msg['from']
      }
      self.pam.db.where_is_track.remove(doc)
      self.pam.db.where_is_track.insert(doc)
      body = "Now Traking {0}".format(trackee)
      self.pam.reply_msg(msg, body)
    elif match.re == self.track_who_re:
      tracker = msg.pam['from'][0]
      body = " You are tracking:\n"
      for info in self.pam.db.where_is_track.find({"tracker":tracker}):
        body = "{0}{1}\n".format(body, info['trackee'])
      self.pam.reply_msg(msg, body)
      
    elif match.re == self.track_stop_re:
      trackee = match.group(1)
      tracker = msg.pam['from'][0]
      doc = {
        'trackee' : trackee,
        'tracker' : tracker
      }
      self.pam.db.where_is_track.remove(doc)
      body = "Not traking {0}".format(trackee)
      self.pam.reply_msg(msg, body)
    elif match.re == self.track_stop_all_re:
      tracker = msg.pam['from'][0]
      self.pam.db.where_is_track.remove({'tracker':tracker})
      body = "Tracking no one"
      self.pam.reply_msg(msg, body)





