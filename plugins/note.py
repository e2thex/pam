
import plugin
import re
import time

class Plugin(plugin.Plugin):
  def load(self):
    self.note_clear_re = re.compile("^note clear$")
    self.note_re = re.compile("^note (.*)$")
    self.note_full_re = re.compile("^note$")
    self.recap_re = re.compile("^recap (all|today)$")
    self.add_listener(
      plugin.RegexListener(
        name="note", 
        description="Records and Returns User related Notes",
        usage=[
          ("note NOTE TEXT", "NOTE TEXT is saved as a note"),
          ("note", "the next message is saved a a note"),
          ("recap all", "List all current notes"),
          ("note clear", "Delete all current notes"),
          ],
        regexes = [
          self.note_clear_re,
          self.note_re,
          self.note_full_re,
          self.recap_re,
          ],
        on_match = self.note_match
        )
      )
  def note_match(self, match, msg, data=None):
    if data =='note' or match.re == self.note_re:
      note = msg.pam['body'] if data else match.group(1)
      when = time.localtime()
      user = msg.pam['from'][0]
      doc = {
        'user' : user,
        'note' : note,
        'when' : time.mktime(when)
      }
      self.pam.db.note.insert(doc)
      self.pam.reply_msg(msg, "Note Logged")
    elif match.re == self.note_full_re:
      self.pam.reply_msg(msg, "Start")
      return "note"
      
    if match.re == self.recap_re:
      user = msg.pam['from'][0]
      notes = self.pam.db.note.find({'user': user})
      body = "Notes\n"
      for note in notes:
        timestr = self.relative_time(time.localtime(note['when']))
        body = "{0}{1}: {2}\n".format(body, timestr, note['note'])
      self.pam.reply_msg(msg, body)
    if match.re == self.note_clear_re:
      user = msg.pam['from'][0]
      self.pam.db.note.remove({'user':user})
      self.pam.reply_msg(msg, "Deleted Notes")


