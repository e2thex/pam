from twisted.application import service
from twisted.words.protocols.jabber import jid
from wokkel.client import XMPPClient

from pam import PAM

application = service.Application("pam")

xmppclient = XMPPClient(jid.internJID("pam@jabber2.fayze2.com"), "papa3")
xmppclient.logTraffic = False
pam = PAM()
pam.setHandlerParent(xmppclient)
xmppclient.setServiceParent(application)

