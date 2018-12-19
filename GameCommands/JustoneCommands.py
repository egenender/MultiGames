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

import Controllers.JustOneController as JustOneController
import Commands

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ForceReply

import MainController
import GamesController
from Constants.Config import STATS
from Boardgamebox.Board import Board
from Boardgamebox.Game import Game
from Boardgamebox.Player import Player
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
	
def command_votes(bot, update):
	try:
		#Send message of executing command   
		cid = update.message.chat_id
		#bot.send_message(cid, "Looking for history...")
		#Check if there is a current game 
		if cid in GamesController.games.keys():
			game = GamesController.games.get(cid, None)
			if not game.dateinitvote:
				# If date of init vote is null, then the voting didnt start          
				bot.send_message(cid, "The voting didn't start yet.")
			else:
				#If there is a time, compare it and send history of votes.
				start = game.dateinitvote
				stop = datetime.datetime.now()
				elapsed = stop - start
				if elapsed > datetime.timedelta(minutes=1):
					history_text = "Vote history for President %s and Chancellor %s:\n\n" % (game.board.state.nominated_president.name, game.board.state.nominated_chancellor.name)
					for player in game.player_sequence:
						# If the player is in the last_votes (He voted), mark him as he registered a vote
						if player.uid in game.board.state.last_votes:
							history_text += "%s ha dado pista.\n" % (game.playerlist[player.uid].name)
						else:
							history_text += "%s *no* ha dado pista.\n" % (game.playerlist[player.uid].name)
					bot.send_message(cid, history_text, ParseMode.MARKDOWN)
					
				else:
					bot.send_message(cid, "Five minutes must pass to see the votes") 
		else:
			bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))

		
def command_call(bot, game):
	try:
		# Verifico en mi maquina de estados que comando deberia usar para el estado(fase) actual
		if game.board.state.fase_actual == "Proponiendo Pistas":
			call_proponiendo_pistas(bot, game)
		elif game.board.state.fase_actual == "Revisando Pistas":
			reviewer_player = game.board.state.reviewer_player
			bot.send_message(game.cid, "Revisor {0} recorda que tenes que verificar las pistas".format(helper.player_call(reviewer_player)), ParseMode.MARKDOWN)
		elif game.board.state.fase_actual == "Adivinando":
			active_player = game.board.state.active_player
			bot.send_message(game.cid, "{0} estamos esperando para que hagas /guess EJEMPLO o /pass".format(helper.player_call(active_player)), ParseMode.MARKDOWN)
	except Exception as e:
		bot.send_message(game.cid, str(e))

def call_proponiendo_pistas(bot, game):
	if not game.dateinitvote:
		# If date of init vote is null, then the voting didnt start          
		bot.send_message(game.cid, "No es momento de dar pista.")
	else:
		#If there is a time, compare it and send history of votes.
		start = game.dateinitvote
		stop = datetime.datetime.now()          
		elapsed = stop - start
		if elapsed > datetime.timedelta(minutes=1):
			# Only remember to vote to players that are still in the game
			history_text = ""
			for player in game.player_sequence:
				# If the player is not in last_votes send him reminder
				if player.uid not in game.board.state.last_votes and player.uid != game.board.state.active_player.uid:
					history_text += "Tienes que dar una pista {0}.\n".format(helper.player_call(player))
			bot.send_message(game.cid, history_text, ParseMode.MARKDOWN)
			if game.board.num_players != 3:
				if len(game.board.state.last_votes) == len(game.player_sequence)-1:
					JustOneController.review_clues(bot, game)
			else:
				# De a 3 jugadores exigo que pongan 2 pistas cada uno son 4 de a 3 jugadores
				if len(game.board.state.last_votes) == len(game.player_sequence)+1:
					JustOneController.review_clues(bot, game)
		else:
			bot.send_message(game.cid, "5 minutos deben pasar para llamar a call") 

		
def command_clue(bot, update, args):
	try:		
		#Send message of executing command   
		try:			
			cid = update.message.chat_id
			uid = update.message.from_user.id
		except Exception as e:
			cid = args[1]
			uid = args[2]
		
		# Para simplificar mando el CHAT_ID del partido junto con la pista
		# Permito las dos formas de gregar pistas
		if len(args) > 2:			
			game = Commands.get_game(int(args[1]))
			
			if uid in game.playerlist:
				#Check if there is a current game
				if game.board == None:
					bot.send_message(game.cid, "El juego no ha comenzado!")
					return					
				if uid != game.board.state.active_player.uid and game.board.state.fase_actual == "Proponiendo Pistas":
					#Data is being claimed
					# TODO Verificar que el usuario no mande pistas con espacios.
					claimtext = args[0]
					#claimtexttohistory = "El jugador %s declara: %s" % (game.playerlist[uid].name, claimtext)
					bot.send_message(uid, "Tu pista: %s fue agregada a las pistas." % (claimtext))
					
					# Si son 3 jugadores se agregan dos pistas 
					if game.board.num_players == 3:
						claimtext_pistas = claimtext.split(' ')
						i = 0
						for claimtext_pista in claimtext_pistas:
							game.board.state.last_votes[uid + i] = claimtext_pista
							i += 1
					else:
						game.board.state.last_votes[uid] = claimtext
					
					Commands.save(bot, game.cid)
					# Verifico si todos los jugadores -1 pusieron pista
					bot.send_message(game.cid, "El jugador *%s* ha puesto una pista." % game.playerlist[uid].name, ParseMode.MARKDOWN)
					
					if game.board.num_players != 3:
						if len(game.board.state.last_votes) == len(game.player_sequence)-1:
							JustOneController.review_clues(bot, game)
					else:
						# De a 3 jugadores exigo que pongan 2 pistas cada uno son 4 de a 3 jugadores
						if len(game.board.state.last_votes) == len(game.player_sequence)+1:
							JustOneController.review_clues(bot, game)
				else:
					bot.send_message(uid, "No puedes hacer dar clue si vos tenes que adivinar o ya ha pasado la fase de poner pistas.")
			else:
				bot.send_message(uid, "No puedes hacer clue si no estas en ningun partido.")
			
		else:
			if len(args) > 0:
				# Obtengo todos los juegos de base de datos de los que usan clue
				mensaje_error = ""
				cursor = conn.cursor()			
				log.info("Executing in DB")
				query = "select * from games g where g.tipojuego = 'JustOne'"
				cursor.execute(query)
				# Si encuentra partida...
				if cursor.rowcount > 0:					
					for table in cursor.fetchall():
						# Por cada partida encontrada la cargo en games si no esta en el controller.
						#bot.send_message(uid, table[0])
						if table[0] not in GamesController.games.keys():
							#bot.send_message(uid, "Cargando el juego {0}".format(table[0]))
							Commands.get_game(table[0])
					clue_games_restriction = ['JustOne']
					#bot.send_message(uid, "Obtuvo esta cantidad de juegos: {0}".format(len(GamesController.games)))
					clue_games = {key:val for key, val in GamesController.games.items() if val.tipo in clue_games_restriction}
					btns = []
					#bot.send_message(uid, len(clue_games))rdd
					
					for game_chat_id, game in clue_games.items():
						#bot.send_message(uid, "Creando boton para el juego {0}".format(game_chat_id))
						if uid in game.playerlist and game.board != None:
							if uid != game.board.state.active_player.uid and game.board.state.fase_actual == "Proponiendo Pistas":
								clue_text = ' '.join(args)
								cid = game_chat_id
								# Creo el boton el cual eligirá el jugador
								txtBoton = game.groupName
								comando_callback = "choosegameclue"
								datos = str(game_chat_id) + "*" + comando_callback + "*" + clue_text + "*" + str(uid)
								btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])
					#bot.send_message(uid, "Llego a botones")
					# Despues de recorrer los partidos y verificar si el usuario puede poner pista le pregunto
					if len(btns) != 0:
						if len(btns) == 1:
							#Si es solo 1 juego lo hago automatico
							command_clue(bot, update, [' '.join(args), cid, uid])
							
						else:
							btnMarkup = InlineKeyboardMarkup(btns)
							bot.send_message(uid, "En cual de estos grupos queres mandar la pista?", reply_markup=btnMarkup)
					else:
						mensaje_error = "No hay partidas en las que puedas hacer /clue"
						bot.send_message(uid, mensaje_error)
							
				else:
					mensaje_error = "No hay partidas vivas en las que puedas hacer /clue"
					bot.send_message(cid, mensaje_error)					
			else:
				bot.send_message(cid, "Le faltan/sobran argumentos recuerde que es /clue [PISTA]. Ej: /clue Alto")
	except Exception as e:
		bot.send_message(uid, str(e))
		log.error("Unknown error: " + str(e))

def callback_choose_game_clue(bot, update):
	callback = update.callback_query
	log.info('callback_choose_mode called: %s' % callback.data)	
	regex = re.search("(-[0-9]*)\*choosegameclue\*(.*)\*([0-9]*)", callback.data)
	cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)	
		
	game = Commands.get_game(cid)
	mensaje_edit = "Has elegido el grupo {0}".format(game.groupName)
	
	try:
		bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
	except Exception as e:
		bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)
	
	command_clue(bot, update, [opcion, cid, uid])
	
def command_forced_clue(bot, update):
	uid = update.message.from_user.id	
	cid = update.message.chat_id
	game = get_game(cid)
	'''
	answer = "Pista "
	i = 1
	for uid in game.playerlist:
		if uid != game.board.state.active_player.uid:
			game.board.state.last_votes[uid] = answer + str(i)
			i += 1
	'''
	#game.board.state.reviewer_player = game.playerlist[387393551]
	JustOneController.review_clues(bot, game)
		

def command_next_turn(bot, update):
	uid = update.message.from_user.id
	cid = update.message.chat_id
	game = Commands.get_game(cid)	
	MainController.start_next_round(bot, game)

def command_pass(bot, update):
	log.info('command_pass called')
	uid = update.message.from_user.id
	cid = update.message.chat_id
	game = Commands.get_game(cid)
	
	if game.board.state.fase_actual != "Adivinando" or uid != game.board.state.active_player.uid:
		bot.send_message(game.cid, "No es el momento de adivinar o no eres el que tiene que adivinar", ParseMode.MARKDOWN)
		return
	
	
	JustOneController.pass_just_one(bot, game)

def command_guess(bot, update, args):
	try:
		log.info('command_guess called')
		#Send message of executing command   
		cid = update.message.chat_id
		uid = update.message.from_user.id
		game = Commands.get_game(cid)
		if (len(args) < 1 or game.board.state.fase_actual != "Adivinando" or uid != game.board.state.active_player.uid):# and uid not in ADMIN:
			bot.send_message(game.cid, "No es el momento de adivinar, no eres el que tiene que adivinar o no has ingresado algo para adivinar", ParseMode.MARKDOWN)
			return
		args_text = ' '.join(args)
		
		if args_text.lower() == game.board.state.acciones_carta_actual.lower():
			#Adivino correctamente! Aumento el puntaje
			game.board.state.progreso += 1
			bot.send_message(game.cid, "*CORRECTO!!!*", ParseMode.MARKDOWN)			
			game.board.discards.append(game.board.state.acciones_carta_actual)			
			JustOneController.start_next_round(bot, game)			
		else:
			#Preguntar al revisor
			mensaje = "*Revisor* {0} confirme por favor!".format(helper.player_call(game.board.state.reviewer_player))
			bot.send_message(game.cid, mensaje, ParseMode.MARKDOWN)
			chat_donde_se_pregunta = uid
			opciones_botones = {
				"correcto" : "Si",
				"incorrecto" : "No"
			}
			helper.simple_choose_buttons(bot, cid, game.board.state.reviewer_player.uid, game.board.state.reviewer_player.uid, "reviewerconfirm", "¿Es correcto lo que se adivinó ({1})? Palabra: {0}".format(game.board.state.acciones_carta_actual, args_text), opciones_botones)
			
	except Exception as e:
		bot.send_message(uid, str(e))
		log.error("Unknown error: " + str(e))

def command_continue(bot, game, uid):
	try:
		
		# Verifico en mi maquina de estados que comando deberia usar para el estado(fase) actual
		if game.board.state.fase_actual == "Proponiendo Pistas":
			# Vuelvo a mandar la pista
			JustOneController.call_players_to_clue(bot, game)
		elif game.board.state.fase_actual == "Revisando Pistas":
			JustOneController.review_clues(bot, game)
		elif game.board.state.fase_actual == "Adivinando":
			active_player = game.board.state.active_player
			bot.send_message(game.cid, "{0} estamos esperando para que hagas /guess EJEMPLO o /pass".format(helper.player_call(active_player)), ParseMode.MARKDOWN)
		elif game.board.state.fase_actual == "Finalizado":
			JustOneController.continue_playing(bot, game)
	except Exception as e:
		bot.send_message(game.cid, str(e))
	
