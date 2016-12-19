# chatbot

## Requirements

- sleekxmpp python package (http://sleekxmpp.com/) [pip install sleekxmpp]
- you need to register a user for the bot on the jabber server
- allow the bot jabber user to receive messages from the boss user

## Install

1. copy the chatbot.py into /usr/local/bin directory
1. copy the files from lib/ directory to /usr/local/lib/chatbot/ directory
1. for systemd systems copy the systemd/chatbot.service file into /etc/systemd/system directory
1. change the bot user, bot password and the boss jabber account in the chatbot.service file
1. systemctl daemon-reload
1. systemctl enable chatbot
1. systemctl start chatbot
