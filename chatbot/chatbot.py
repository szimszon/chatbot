#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This chatbot is derived from SleekXMPP's example

      SleekXMPP: The Sleek XMPP Library
      Copyright (C) 2010  Nathanael C. Fritz
      This file is part of SleekXMPP.

      See the file LICENSE for copying permission.
    
    Author: Szabolcs Gyuris
    Date: 2016-12-19
"""

import sys
import re
import logging
import getpass
import datetime
import time
import subprocess
from optparse import OptionParser
import os

import sleekxmpp

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class ChatBot(sleekxmpp.ClientXMPP):

    def __init__(self, opts):
        jid=opts.jid
        password=opts.password

        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.opts=opts
        
        self.regexp=self.opts.regexp if self.opts.regexp else '^do:[ ]*(.*)::$'
        self.argsep=self.opts.argsep if self.opts.argsep else ';'
        self.inittalkbacktimeout=int(self.opts.inittalkbacktimeout) if self.opts.inittalkbacktimeout else 5
        self.talkbacktimeout=int(self.opts.talkbacktimeout) if self.opts.talkbacktimeout else 30

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The groupchat_message event is triggered whenever a message
        # stanza is received from any chat room. If you also also
        # register a handler for the 'message' event, MUC messages
        # will be processed by both handlers.
        self.add_event_handler("message", self.command)

    def command(self,msg):
      
      #
      # Check if the request is authentic
      # ######################################################
      if str(msg['from'].bare) != str(opts.boss):
        logging.info('Not a Boss is talking to us but '+msg['from'].bare)
        return True
      body=msg['body'].strip()
      cmd=re.compile(self.regexp).match(body)
      if not cmd:
        return True
      cmd=cmd.group(1).split(self.argsep)
      if '..' in cmd[0]:
        return True
      command=cmd[0]
      cmd[0]=os.path.join(self.opts.scriptdir,cmd[0])
      if not os.path.isfile(cmd[0]):
        return True

      #
      # Execute the script
      # ##################
      try:
        logging.info(str(opts.boss)+" asked us to do (("+str(cmd)+"))")
        w=datetime.datetime.now()+datetime.timedelta(seconds=self.inittalkbacktimeout)
        starttime=datetime.datetime.now()
        res=subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True,
                             bufsize=0,
                             )
        stdout="↶--------------- ["+str(command)+"] ("+str(datetime.datetime.now())+") ---------------↷\n"
        stderr=""
        #
        # Time to time put some feedback to the XMPP's chat
        # ##################################################
        while ( res.poll() == None ):
          time.sleep(1)
          stdout+=res.stdout.readline()
          if w<=datetime.datetime.now():
            if len(stdout)>0:
              self.send_message(mto=opts.boss,
                                mbody=str(stdout))
        
            w=datetime.datetime.now()+datetime.timedelta(seconds=self.talkbacktimeout)
            stdout=""

        (stdoutplus,stderrplus)=res.communicate()
        stdout+=stdoutplus
        stderr+=stderrplus

      except Exception,e:
        stderr="[%s]"%str(e)
        stdout=""
      #
      # Finally put the last messages to the chat
      # ##########################################
      if len(stderr)>0:
        stdout+="\n↓--------------- ["+str(command)+"] ---------------↓"
        stdout+="\n======= ERR =======\n"+str(stderr)+"\n======= ERR ======="
      self.send_message(mto=opts.boss,
                          mbody=str(stdout)+\
                                "\n↳--------------- ["+str(command)+\
                                "] {"+str(res.returncode)+"} ("+str(datetime.datetime.now())+\
                                ", "+str(datetime.datetime.now()-starttime)+") ---------------↲")
      return True


    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.get_roster()
        self.send_presence()


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)
    
    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-b", "--boss", dest="boss",
                    help="The boss JID")
    
    # command execution
    optp.add_option("-s", "--scriptdir", dest="scriptdir",
                    help="directory of scripts",
                    default="/usr/local/lib/chatbot/")
    optp.add_option("-r", "--regexp", dest="regexp",
                    help="regexp to match the command",
                    default="^do:[ ]*(.*)::$")
    optp.add_option("-a", "--argsep", dest="argsep",
                    help="command argumentum separator",
                    default=";")

    # timeouts for talking the stdout back to jabber user
    optp.add_option("-i", "--init-talkback-timeout", dest="inittalkbacktimeout",
                    help="initial talkback timeout",
                    default=5)
    optp.add_option("-t", "--talkback-timeout", dest="talkbacktimeout",
                    help="talkback timeout",
                    default=30)

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")

    # Setup the ChatBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = ChatBot(opts)
    xmpp.register_plugin('xep_0030') # Service Discovery
    #xmpp.register_plugin('xep_0045') # Multi-User Chat
    xmpp.register_plugin('xep_0199') # XMPP Ping
    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
