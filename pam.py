#!/usr/bin/python

from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from wokkel.xmppim import MessageProtocol, AvailablePresence
import os
import inspect 
import re
import sys

class PAM(MessageProtocol):
  def __init__(self):
    self.parent = None
    self.xmlstream = None
    self.load()

  def load(self):
    self._watchers = {}
    self.current = {}
    self.data = {}
    self.load_all_plugins_in_path(os.path.join(PAM.loc(),"plugins"))

  def load_plugin(self, path, plugin_name):
    # if there is no path make sure the plugin paths are load
    # incase we are loading a plugin from them
    if path not in sys.path:
      sys.path.append(path)
    try :
      p = __import__(plugin_name)
    except Exception as e:
      print plugin_name
      print e
    if 'Plugin' in p.__dict__ and callable(p.Plugin) :
      plugin = p.Plugin(self) 
      plugin.load()

  def find_plugins(self, path):
    return  [ 
       self._is_python_module(path,file) 
       for file in os.listdir(path) 
       if self._is_python_module(path,file) 
     ]

  def _is_python_module (self, path, name): 
    """ 
    this function returns if the name of the file if it is a dir
    or end in py
    """
    if os.path.isdir(os.path.join(path,name)) :
      if os.path.isfile(os.path.join(path, name, "__init__.py")):
        return name
    match = re.search("^(.*)\.py$", name)
    if match :
      return match.group(1)

  def load_all_plugins_in_path(self, path):
    if os.path.isdir(path):
      plugin_names = self.find_plugins(path)
      for name in (plugin_names):
        self.load_plugin(path, name)


  def connectionMade(self):
      print "Connected!"

      # send initial presence
      self.send(AvailablePresence())

  def connectionLost(self, reason):
      print "Disconnected!"

  def onMessage(self, msg):
    msg.pam = {}
    msg.pam['from'] = jid.parse(msg['from'])
    msg.pam['to'] = jid.parse(msg['to'])

      #if msg["type"] == 'chat' and hasattr(msg, "body"):
    if hasattr(msg, "body"):
      if msg['from'] in self.current:
        current = self.current[msg['from']]
        data = self._watchers[current['owner']].onMessage(msg, current['data'])
        if data:
          self.current[msg['from']] = {'owner':name, 'data':data }
        else:
          del self.current[msg['from']]
        
      else : 
        for (name,watcher) in self._watchers.iteritems():
          data = watcher.onMessage(msg)
          if data:
            self.current[msg['from']] = {'owner':name, 'data':data }
            break

  def add_watcher(self,watcher):
    self._watchers[watcher.name] = watcher

  def send_msg(self, froma, to, typea, body):
    reply = domish.Element((None, "message"))
    reply["to"] = to
    reply["from"] = froma
    reply["type"] = typea
    reply.addElement("body", content=body)
    self.send(reply)
  def reply_msg(self, msg, body):
    self.send_msg(msg['to'], msg['from'], 'chat', body)

  @classmethod
  def loc(cls):
    return os.path.dirname(os.path.realpath(inspect.getfile(cls)))

