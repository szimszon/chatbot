# chatbot

This is a simple script to listen on a jabber server for messages from a specific JabberID (*BOSS*) and if the message matches a defined *REGEXP* (do:command::) it will execute a specific command.
Like:
```
  do:ls::
```
will execute the **ls** program placed in *SCRIPTDIR* (/usr/local/lib/chatbot/ls)

You can push arguments to this scripts with **;** *ARGSEP* like: do:command;arg1;arg2[,...]::

## help
<pre>
./chatbot.py --help
Usage: chatbot.py [options]

Options:
  -h, --help            show this help message and exit
  -q, --quiet           set logging to ERROR
  -d, --debug           set logging to DEBUG
  -v, --verbose         set logging to COMM
  -j JID, --jid=JID     JID to use
  -p PASSWORD, --password=PASSWORD
                        password to use
  -b BOSS, --boss=BOSS  The boss JID
  -s SCRIPTDIR, --scriptdir=SCRIPTDIR
                        directory of scripts
  -r REGEXP, --regexp=REGEXP
                        regexp to match the command
  -a ARGSEP, --argsep=ARGSEP
                        command argumentum separator
  -i INITTALKBACKTIMEOUT, --init-talkback-timeout=INITTALKBACKTIMEOUT
                        initial talkback timeout
  -t TALKBACKTIMEOUT, --talkback-timeout=TALKBACKTIMEOUT
                        talkback timeout
</pre>

## Requirements

- sleekxmpp python package (http://sleekxmpp.com/) [pip install sleekxmpp]
- you need to register a user for the bot on the jabber server
- allow the bot jabber user to receive messages from the boss user

## Install

1. copy the chatbot.py into /usr/local/bin directory
1. copy the files from lib/ directory to /usr/local/lib/chatbot/ directory
1. set up the sudoers file for the chatbot user so the user can run the requested scripts and commands
1. for systemd systems copy the systemd/chatbot.service file into /etc/systemd/system directory
1. change the bot user, bot password and the boss jabber account in the chatbot.service file
1. systemctl daemon-reload
1. systemctl enable chatbot
1. systemctl start chatbot

