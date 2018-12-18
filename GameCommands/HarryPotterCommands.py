import json
import logging as log
import datetime
import jsonpickle
import os
import psycopg2
import urllib.parse
import sys
from time import sleep

from Utils.helpers import helper
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ForceReply

import random
import re

# Enable logging

log.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=log.INFO)
logger = log.getLogger(__name__)

#DB Connection I made a Haroku Postgres database first
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

def command_roll(bot, update, args):	
	if args:
		text_tirada = '¡Tu tirada de ' + ' '.join(args)
	else:
		text_tirada = '¡Tu tirada'
	
	cid = update.message.chat_id
	uid = update.message.from_user.id
	
	tirada = random.randint(1,101)	
	if tirada > 97:
		tirada2 = random.randint(1,101)
		text_tirada +=  ' es *%s!*' % (str(tirada+tirada2))
	elif tirada < 4:
		tirada2 = random.randint(1,101)
		text_tirada +=  ' es *%s!*' % (str(tirada-tirada2))
	elif tirada == 27:
		text_tirada +=  ' es *Épico*!' % (str(tirada+tirada2))		
	else:
		text_tirada +=  ' es *%s!*' % (str(tirada))
		
	bot.send_message(cid, "%s" % (text_tirada), ParseMode.MARKDOWN)
	
	# Si hay un juego creado guardo en el historial
	game = get_game(cid)
	if game and uid in game.playerlist:
		player = game.playerlist[uid]
		texthistory = "Jugador *%s* - %s" % (player.name, text_tirada)
		game.history.append("%s" % (texthistory))
