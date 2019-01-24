import json
import logging as log
import datetime
#import ast
import jsonpickle
import os
import psycopg2
import urllib.parse
import sys
from time import sleep

import Arcana.Controller as ArcanaController
import Commands

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ForceReply

import MainController
import GamesController
from Constants.Config import STATS
from SayAnything.Boardgamebox.Board import Board
from SayAnything.Boardgamebox.Game import Game
from SayAnything.Boardgamebox.Player import Player
from Boardgamebox.State import State

from Constants.Config import ADMIN

from Utils.helpers import helper

from collections import namedtuple

from PIL import Image
from io import BytesIO

# Objetos que uso de prueba estaran en el state
from Constants.Cards import cartas_aventura
from Constants.Cards import opciones_opcional
from Constants.Cards import opciones_choose_posible_role
from Constants.Cards import modos_juego

from Constants.Config import JUEGOS_DISPONIBLES
from Constants.Config import MODULOS_DISPONIBES
from Constants.Config import HOJAS_AYUDA

from Constants.Cards import comandos
import random
import re
# Objetos que uso de prueba estaran en el state

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

def check_invalid_pick(args):
	return ((not args[0].isdigit()) or (args[0] == '0'))

def command_guess(bot, update, args):
	cid = update.message.chat_id
	uid = update.message.from_user.id
	game = Commands.get_game(cid)
	
	# Remover luego de que pase por start.
	if game.board.state.extraGuess == False:
		game.board.state.extraGuess = 0
	
	if game.board.state.fase_actual != "Predecir" or uid == game.board.state.active_player.uid:	
		bot.send_message(game.cid, "Fase actual *{}*".format(game.board.state.fase_actual), ParseMode.MARKDOWN)
		bot.send_message(game.cid, "No es el momento de adivinar o no eres el que tiene que adivinar", ParseMode.MARKDOWN)
		return
	
	# Acepto 1 o 2 guess
	continue_resolve = 1 <= len(args) <= (game.board.state.extraGuess+1)
	# Verifico si todos los numero para adivinar son validos		
	for arg in args:
		if check_invalid_pick(arg) or not (1 <= int(arg) <= 7):
			continue_resolve = False			
	
	if continue_resolve:
		if (game.board.state.extraGuess+1) != len(args):
			bot.send_message(game.cid, "Tienes que poner {} numero/s para adivinar."
					 .format(2 if game.board.state.extraGuess else 1), ParseMode.MARKDOWN)		
		ArcanaController.resolve(bot, game, [int(s) for s in args])
	else:
		bot.send_message(game.cid, "El número debe ser entre 1 y 7", ParseMode.MARKDOWN)
	
def command_pass(bot, update):
	log.info('command_pass called')
	uid = update.message.from_user.id
	cid = update.message.chat_id
	game = Commands.get_game(cid)
	
	# TODO poner restriccion del jugador activo
	if game.board.state.fase_actual != "Predecir" or uid == game.board.state.active_player.uid:	
		bot.send_message(game.cid, "Fase actual *{}*".format(game.board.state.fase_actual), ParseMode.MARKDOWN)
		bot.send_message(game.cid, "No es el momento de adivinar o no eres el que tiene que adivinar", ParseMode.MARKDOWN)
		return
	ArcanaController.resolve(bot, game)

def command_remove(bot, update, args):
	log.info('command_pass called')
	uid = update.message.from_user.id
	cid = update.message.chat_id
	game = Commands.get_game(cid)
	
	elegido = -1 if (check_invalid_pick(args) or len(args) != 1) else int(args[0])
	
	#bot.send_message(game.cid, "{} {}".format(elegido, len(game.board.state.fadedarcanasOnTable)+1))
	fadeded_on_table = len(game.board.state.fadedarcanasOnTable)+1
	if (elegido > 0) and (elegido < fadeded_on_table):
		ArcanaController.use_fadded_action(bot, game, uid, elegido-1)		
	else:
		bot.send_message(game.cid, "Debes ingresar un numero del 1 a {} (incluido)".format(fadeded_on_table-1), ParseMode.MARKDOWN)

def command_call(bot, game):
	try:
		# Verifico en mi maquina de estados que comando deberia usar para el estado(fase) actual
		if game.board.state.fase_actual == "Jugar Fate":
			msg = "{} tienes que poner un destino sobre alguna Arcana!".format(helper.player_call(game.board.state.active_player))
			bot.send_message(game.cid, msg, ParseMode.MARKDOWN)
			ArcanaController.show_fates_active_player(bot, game)
		elif game.board.state.fase_actual == "Predecir":
			call_other_players = ""
			for uid, player in game.playerlist.items():
				call_other_players += "{} ".format(helper.player_call(player)) if uid != game.board.state.active_player.uid else ""
			mensaje_final = "\n{}Hagan /guess N para adivinar destino o /pass para pasar!".format(call_other_players)			
			bot.send_message(game.cid, mensaje_final, ParseMode.MARKDOWN)
	except Exception as e:
		bot.send_message(game.cid, str(e))		
		
def command_continue(bot, game, uid):
	try:
		
		# Verifico en mi maquina de estados que comando deberia usar para el estado(fase) actual
		if game.board.state.fase_actual == "Proponiendo Pistas":
			# Vuelvo a mandar la pista
			SayAnythingController.call_players_to_clue(bot, game)
		elif game.board.state.fase_actual == "Revisando Pistas":
			SayAnythingController.review_clues(bot, game)
		elif game.board.state.fase_actual == "Adivinando":
			active_player = game.board.state.active_player
			bot.send_message(game.cid, "{0} estamos esperando para que hagas /guess EJEMPLO o /pass".format(helper.player_call(active_player)), ParseMode.MARKDOWN)
		elif game.board.state.fase_actual == "Finalizado":
			SayAnythingController.continue_playing(bot, game)
	except Exception as e:
		bot.send_message(game.cid, str(e))

def command_discard(bot, update):
	log.info('command_pass called')
	uid = update.message.from_user.id
	cid = update.message.chat_id
	game = Commands.get_game(cid)
	
	all_tokens = [int(item['Texto']) 
		      for sublist in [arcana['tokens'] 
				      for arcana in game.board.state.arcanasOnTable ] for item in sublist]
	
	# Verify if user is in the game and has only fate token
	if uid in game.playerlist and len(game.playerlist[uid].playerFateTokens) == 1 and all_tokens.count(int(game.playerlist[uid].playerFateTokens[0]['Texto'])) == 2:
		discarded_fate = game.playerlist[uid].playerFateTokens.pop()
		game.board.fateTokens.append(discarded_fate)
		bot.send_message(game.cid, "El jugador se ha descartado del token: {} ({})."
				 .format(discarded_fate["Texto"]), ParseMode.MARKDOWN)
	else:
		bot.send_message(game.cid, "No estas en esta partida o tienes más de un token o no tienes tokens en la mano.", ParseMode.MARKDOWN)	
	
