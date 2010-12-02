import plugin
import re
import time

class Plugin(plugin.Plugin):
  def load(self):
    self.help_re = re.compile("help$")
    self.help_topic_re = re.compile("help (.*)$")
    self.add_listener(
      plugin.RegexListener(  
        name="help",  
        description="Return PAM Help",
        usage=[
          ("help TOPIC", "reply with usage on a TOPIC"),
          ("help", "List all Topics with a description"),
          ],
        regexes = [
          self.help_re,
          self.help_topic_re
          ],
        on_match = self.help_match
        )
      )
  def help_match(self, match, msg, data=None):
    if data =="topic" or match.re == self.help_topic_re:
      topic = msg.pam['body'] if data else match.group(1)
      if topic in self.pam._listeners:
        usage = self.pam._listeners[topic].usage()
        body = "{0} has the following usage:\n".format(topic)
        for line in usage:
          body = "{0}{1}\n".format(body, line)
        self.pam.reply_msg(msg, body)
      else :
        self.pam.reply_msg(msg, "Not topic {0}".format(topic))

    elif match.re == self.help_re:
      body = "Topics:\n"
      for listener in self.pam._listeners.itervalues():
        name = listener.name.ljust(20)
        body = "{0}{1} {2}\n".format(body, name, listener.description)
      body = "{0}Which Topic?".format(body)
      self.pam.reply_msg(msg, body)
      return "topic"
  






