
import plugin
import re
import time
from dateutil.parser import *
from datetime import datetime, timedelta
import random

class Plugin(plugin.Plugin):
  def load(self):
    # Define regex as attr of self so we can see which one matched
    self.hi_re = re.compile("^([hH]i|[hH]ello|[hH]owdy|[Ww]ats up])$")

    # add a regex listener wut the where_is_match function as the on_match
    # callback
    self.add_listener(
      plugin.RegexListener(
        name="hi", 
        description="Return greetings",
        usage= [
          ("hi", 'if you are nice pam might say hi back'),
          ],
        regexes = [
          self.hi_re,
          ],
        on_match = self.hi_match
        )
      )
  def hi_match(self, match, msg, data=None):
    if match.re == self.hi_re:
      greetings = [
      'Hi',
      'Howdy',
      'Hello',
      'Whatz up!',
      ]
      body = random.choice(greetings) + ", fell free to ask for help."
      self.pam.reply_msg(msg, body)
