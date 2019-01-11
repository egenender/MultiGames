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

import JustOne.Controller as JustOneController
import SayAnything.Controller as SayAnythingController

from Utils.helpers import helper
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ForceReply
import MainController
import GamesController

from Constants.Config import STATS
from Boardgamebox.Board import Board

from Boardgamebox.Game import Game
from SayAnything.Boardgamebox.Game import Game as GameSayAnything
from Arcana.Boardgamebox.Game import Game as GameArcana
from Boardgamebox.Game import Game

from Boardgamebox.Player import Player
from Boardgamebox.State import State
from Constants.Config import ADMIN
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

# Secret Moon
secret_moon_cid = '-1001206290323'

def command_newgame_sql_command(bot, update, args):
	cid, uid = update.message.chat_id, update.message.from_user.id
	if uid in ADMIN:
		try:
			#Check if game is in DB first
			cursor = conn.cursor()			
			log.info("Executing in DB")
			#query = "select * from games;"
			query = " ".join(args)
			cursor.execute(query)
			#dbdata = cur.fetchone()
			if cursor.rowcount > 0:
				bot.send_message(cid, 'Resultado de la consulta:')
				for table in cursor.fetchall():
					#bot.send_message(cid, len(str(table)))
					tabla_str = str(table)
					# Si supera el maximo de caracteres lo parto
					max_length_msg = 3500
					if len(tabla_str) < max_length_msg:
						bot.send_message(cid, table)
					else:
						n = max_length_msg
						parts = [tabla_str[i:i+n] for i in range(0, len(tabla_str), n)]
						for part in parts:
							bot.send_message(cid, part)
			else:
				bot.send_message(cid, 'No se obtuvo nada de la consulta')
		except Exception as e:
			bot.send_message(cid, 'No se ejecuto el comando debido a: '+str(e))
			conn.rollback()

	
def save(bot, cid, newGroupName = ''):
	try:		
		#groupName = "Prueba"
		game = GamesController.games.get(cid, None)
		gameType = game.tipo
		save_game(cid, game.groupName if newGroupName == '' else newGroupName , game, gameType )
		#bot.send_message(cid, 'Se grabo correctamente.')
		#log.info('Se grabo correctamente.')
	except Exception as e:
		bot.send_message(cid, 'Error al grabar '+str(e))

def load(bot, update):
	cid = update.message.chat_id
	game = load_game(cid)			
	if game:
		GamesController.games[cid] = game
		bot.send_message(cid, "Juego Cargado exitosamente")				
		#bot.send_message(game.cid, game.board.print_board(game.playerlist))				
		# Remember the current player that he has to act
		#MainController.start_round(bot, game)
	else:
		bot.send_message(cid, "No existe juego")		

def get_game(cid):
	# Busco el juego actual
	game = GamesController.games.get(cid, None)	
	if game:
		# Si esta lo devuelvo.
		return game
	else:
		# Si no esta lo busco en BD y lo pongo en GamesController.games
		game = load_game(cid)
		if game:
			GamesController.games[cid] = game
			return game
		else:
			None

	
def command_hoja_ayuda(bot, update):
	cid = update.message.chat_id
	uid = update.message.from_user.id
	game = get_game(cid)	
	help_text = HOJAS_AYUDA.get(game.tipo)	
	chat_send = cid if game.modo == 'Solitario' else uid
	bot.send_message(chat_send, help_text, ParseMode.MARKDOWN)
	if game.tipo == 'LostExpedition':
		bot.send_photo(chat_send, photo=open('/app/img/LostExpedition/Ayuda01.jpg', 'rb'))
		bot.send_photo(chat_send, photo=open('/app/img/LostExpedition/Ayuda02.jpg', 'rb'))
		
def command_showstats(bot, update):
	log.info('command_showstats called')
	cid, uid = update.message.chat_id, update.message.from_user.id	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]		
		bot.send_message(cid, player.print_stats())

def command_help(bot, update):
	cid = update.message.chat_id
	'''
	help_text = "Eventos amarillos son obligatorios\n" + \
	"Eventos rojo son obligatorios pero tenes que elegir 1\n"  + \
	"Eventos Azules son opcionales\n"
	'''
	help_text = "\nLos siguientes comandos estan disponibles:\n"
	for i in commands:
		help_text += i + "\n"
	bot.send_message(cid, help_text)
		
def command_symbols(bot, update):
	cid = update.message.chat_id
	url_img = '/app/img/LostExpedition/Ayuda01.jpg'	
	img = Image.open(url_img)
	bot.send_photo(cid, photo=bio)
	url_img = '/app/img/LostExpedition/Ayuda02.jpg'	
	img = Image.open(url_img)
	bot.send_photo(cid, photo=bio)

def command_reglas(bot, update):
	cid = update.message.chat_id
	texto_reglas = "Solitario: \n" + \
			"*Dia*: Obten 6 cartas. 2 mazo, 2 mano, 1 mazo, 1 mano.\n*Se ordenan por número.*\nResuelve.\n*Pierde 1 comida.*\n" + \
			"*Noche*: Primera de la mano. Poner de mazo o mano hasta completar 6.\n*Se puede poner adelante o atras en la ruta.*\nResuelve.\n*Pierde 1 comida.* Ir a día."			
	
	bot.send_message(cid, texto_reglas, ParseMode.MARKDOWN)

def get_base_data2(cid, uid):
	if uid in ADMIN:		
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return None, None
		player = game.playerlist[uid]
		return game, player
	else:
		return None, None
		
def get_base_data(bot, update):	
	cid, uid = update.message.chat_id, update.message.from_user.id
	if uid in ADMIN:		
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return cid, uid, None, None
		player = game.playerlist[uid]
		return cid, uid, game, player
	else:
		return cid, uid, None, None		
		
def command_prueba(bot, update, args, chat_data, user_data):
	#log.info(update.message.from_user.id)
	#log.info(update.message.chat_id)
	cid, uid = update.message.chat_id, update.message.from_user.id
	groupType, groupName = update.message.chat.type, update.message.chat.title
	
	if uid in ADMIN:
		game = get_game(cid)
		
		#bot.send_message(cid, "Este es el grupo ({0}) - Cuyo nombre es {1} y tipo es {2}".format(cid, groupName, groupType))
		#bot.send_message(cid, chat_data)
		#bot.send_message(cid, user_data)
		
		SayAnythingController.call_players_to_vote(bot, game)
		
		'''
		
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		#bot.send_message(uid, "Respondeme", reply_markup=ForceReply())
		bot.send_message(uid, "/clue algo -312312312")
		'''

commands = [  # command description used in the "help" command
	'/help - Muestra ayuda sobre los comandos',
	'/newgamelostexpedition - Nuevo Juego de Lost Expedition',
	'/drawcard  - Obtiene X cartas, defecto 2',
	'/losebullet  - Resta 1 bala',
	'/gainbullet - Gana 1 bala',
	'/losefood - Pierde 1 comida',
	'/gainfood  - Gana 1 de comida',
	'/stats  - Status actual',
	'/campero - Quita/agrega vida explorador, defecto quita 1 vida. Ej: /campero -1 agrega 1 vida',
	'/brujula - Quita/agrega vida explorador, defecto quita 1 vida. Ej: /brujula -1 agrega 1 vida',
	'/hoja - Quita/agrega vida explorador, defecto quita 1 vida. Ej: /hoja -1 agrega 1 vida',
	'/addexplorationfromhand - Agrega carta a exploracion de la mano por defecto la primera',
	'/addexplorationfromdeck - Agrega carta a exploracion del mazo',
	'/swapexploration X Y- Intercambia dos cartas de exploracion Ej: /swapexploratio 2 4',
	'/removeexploration - remueve una carta de exploracion por defecto la primera. Ej: /removeexploration 2',
	'/showexploration - Muestra la exploracion actual',
	'/showhand - Muestra la mano actual',
	'/sortexploration - Ordena la exploracion actual de menor a mayor',
	'/sorthand - Ordena la mano del jugador de menor a mayor',
	'/save - Graba el juego',
	'/load - Obtiene el juego guardado',
	'/delete - Borra el juego actual'	
]

symbols = [
    u"\u25FB\uFE0F" + ' Empty field without special power',
    u"\u2716\uFE0F" + ' Field covered with a card',  # X
    u"\U0001F52E" + ' Presidential Power: Policy Peek',  # crystal
    u"\U0001F50E" + ' Presidential Power: Investigate Loyalty',  # inspection glass
    u"\U0001F5E1" + ' Presidential Power: Execution',  # knife
    u"\U0001F454" + ' Presidential Power: Call Special Election',  # tie
    u"\U0001F54A" + ' Liberals win',  # dove
    u"\u2620" + ' Fascists win'  # skull
]

def command_board(bot, update):
	cid = update.message.chat_id
	game = get_game(cid)
	if game.board:
		try:
			bot.send_message(cid, game.board.print_board(game), ParseMode.MARKDOWN)
		except Exception :
			game.board.print_board(bot, game)
	else:
		bot.send_message(cid, "There is no running game in this chat. Please start the game with /startgame")
	
def command_start(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid,"Bot para multiples juegos. Preguntar al ADMIN por los juegos disponibles")
    #command_help(bot, update)

def command_rules(bot, update):
    cid = update.message.chat_id
    btn = [[InlineKeyboardButton("Rules", url="http://www.secrethitler.com/assets/Secret_Hitler_Rules.pdf")]]
    rulesMarkup = InlineKeyboardMarkup(btn)
    bot.send_message(cid, "Read the official Secret Hitler rules:", reply_markup=rulesMarkup)

# prints statistics, only ADMIN
def command_stats(bot, update):
	cid = update.message.chat_id
	if cid == ADMIN:		
		bot.send_message(cid, "Estadisticas pronto...")
		
def command_cancelgame(bot, update):
	log.info('command_cancelgame called')
	cid = update.message.chat_id	
	#Always try to delete in DB
	try:
		delete_game(cid)
		if cid in GamesController.games.keys():
			del GamesController.games[cid]
		bot.send_message(cid, "Borrado exitoso.")
	except Exception as e:
		bot.send_message(cid, "El borrado ha fallado debido a: "+str(e))	

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

def command_call(bot, update):
	import JustOne.Commands as JustoneCommands
	import SayAnything.Commands as SayAnythingCommands
	import Arcana.Commands as ArcanaCommands
	
	try:
		#Send message of executing command   
		cid = update.message.chat_id
		#bot.send_message(cid, "Looking for history...")
		#Check if there is a current game 
		game = get_game(cid)
		
		if game:			
			if game.tipo == "JustOne":
				JustoneCommands.command_call(bot, game)
			elif game.tipo == "SayAnything":
				SayAnythingCommands.command_call(bot, game)
			elif game.tipo == "Arcana":
				ArcanaCommands.command_call(bot, game)
			else:
				bot.send_message(cid, "El juego no tiene el metodo /call")
		else:
			bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))

def command_pass(bot, update):
	import JustOne.Commands as JustoneCommands
	import SayAnything.Commands as SayAnythingCommands
	
	try:
		#Send message of executing command   
		cid = update.message.chat_id
		#bot.send_message(cid, "Looking for history...")
		#Check if there is a current game 
		game = get_game(cid)
		
		if game:			
			if game.tipo == "JustOne":
				JustoneCommands.command_pass(bot, update)
			elif game.tipo == "SayAnything":
				SayAnythingCommands.command_pass(bot, update)
			else:
				bot.send_message(cid, "El juego no tiene el metodo /call")
		else:
			bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))
		
def command_showhistory(bot, update):
	#game.pedrote = 3
	try:
		#Send message of executing command   
		cid = update.message.chat_id
		#Check if there is a current game 
		game = get_game(cid)
		if game:			
			#bot.send_message(cid, "Current round: " + str(game.board.state.currentround + 1))
			uid = update.message.from_user.id
			history_text = "History:\n\n" 
			for x in game.history:
				history_text += x + "\n\n"

			bot.send_message(uid, history_text, ParseMode.MARKDOWN)
			#bot.send_message(cid, "I sent you the history to our private chat")			
		else:
			bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))
		log.error("Unknown error: " + str(e))  
		
def command_claim(bot, update, args):
	#game.pedrote = 3
	try:
		#Send message of executing command   
		cid = update.message.chat_id
		#Check if there is a current game 
		game = get_game(cid)
		if game:
			uid = update.message.from_user.id
			if uid in game.playerlist:								
				if len(args) > 0:
					#Data is being claimed
					claimtext = ' '.join(args)
					claimtexttohistory = "El jugador %s declara: %s" % (game.playerlist[uid].name, claimtext)
					bot.send_message(cid, "Tu declaración: %s fue agregada al historial." % (claimtext))
					game.history.append("%s" % (claimtexttohistory))
				else:					
					bot.send_message(cid, "Debes mandar un mensaje para hacer una declaración.")

			else:
				bot.send_message(cid, "Debes ser un jugador del partido para declarar algo.")				
		else:
			bot.send_message(cid, "No hay juego en este chat. Crea un nuevo juego con /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))
		log.error("Unknown error: " + str(e))    
		
def save_game(cid, groupName, game, gameType):
	try:
		#Check if game is in DB first
		cur = conn.cursor()			
		#log.info("Searching Game in DB")
		query = "select * from games where id = %s;"
		cur.execute(query, [cid])
		dbdata = cur.fetchone()
		if cur.rowcount > 0:
			#log.info('Updating Game')
			gamejson = jsonpickle.encode(game)
			#log.info(gamejson)
			#query = "UPDATE games SET groupName = %s, data = %s WHERE id = %s RETURNING data;"
			query = "UPDATE games SET groupName = %s, tipojuego = %s, data = %s WHERE id = %s;"
			cur.execute(query, (groupName, gameType, gamejson, cid))
			#log.info(cur.fetchone()[0])
			conn.commit()		
		else:
			#log.info('Saving Game in DB')
			gamejson = jsonpickle.encode(game)
			#log.info(gamejson)
			query = "INSERT INTO games(id, groupName, tipojuego, data) VALUES (%s, %s, %s, %s) RETURNING data;"
			#query = "INSERT INTO games(id , groupName  , data) VALUES (%s, %s, %s) RETURNING data;"
			cur.execute(query, (cid, groupName, gameType, gamejson))
			#log.info(cur.fetchone()[0])
			conn.commit()
	except Exception as e:
		log.info('No se grabo debido al siguiente error: '+str(e))
		conn.rollback()

def load_game(cid):
	cur = conn.cursor()			
	#log.info("Searching Game in DB")
	query = "SELECT * FROM games WHERE id = %s;"
	cur.execute(query, [cid])
	dbdata = cur.fetchone()

	if cur.rowcount > 0:
		#log.info("Game Found")
		jsdata = dbdata[3]
		
		#log.info(dbdata[0])
		#log.info(dbdata[1])
		#log.info(dbdata[2])
		#log.info(dbdata[3])
		#log.info("jsdata = %s" % (jsdata))				
		game = jsonpickle.decode(jsdata)
		
		# For some reason the decoding fails when bringing the dict playerlist and it changes it id from int to string.
		# So I have to change it back the ID to int.				
		temp_player_list = {}		
		for uid in game.playerlist:
			temp_player_list[int(uid)] = game.playerlist[uid]
		game.playerlist = temp_player_list
		
		if game.board is not None and game.board.state is not None:
			temp_last_votes = {}
			for uid in game.board.state.last_votes:
				temp_last_votes[int(uid)] = game.board.state.last_votes[uid]
			game.board.state.last_votes = temp_last_votes	
		#bot.send_message(cid, game.print_roles())
		return game
	else:
		#log.info("Game Not Found")
		return None

def delete_game(cid):
	cur = conn.cursor()
	#log.info("Deleting Game in DB")
	query = "DELETE FROM games WHERE id = %s;"
	cur.execute(query, [cid])
	conn.commit()
	
def command_choose_posible_role(bot, update):
	cid, uid = update.message.chat_id, update.message.from_user.id
	choose_posible_role(bot, cid, uid)
def choose_posible_role(bot, cid, uid):
	frase_regex = "chooserole"
	pregunta_arriba_botones = "¿Qué rol quisieras ser?"
	chat_donde_se_pregunta = uid
	multipurpose_choose_buttons(bot, cid, uid, chat_donde_se_pregunta, frase_regex, pregunta_arriba_botones, opciones_choose_posible_role)
def callback_choose_posible_role(bot, update):
	callback = update.callback_query
	log.info('callback_choose_posible_role called: %s' % callback.data)	
	regex = re.search("(-[0-9]*)\*chooserole\*(.*)\*([0-9]*)", callback.data)
	cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
	bot.edit_message_text("Mensaje Editado: Has elegido el Rol: %s" % opcion, cid, callback.message.message_id)
	bot.send_message(cid, "Ventana Juego: Has elegido el Rol %s" % opcion)
	bot.send_message(uid, "Ventana Usuario: Has elegido el Rol %s" % opcion)	


def multipurpose_choose_buttons(bot, cid, uid, chat_donde_se_pregunta, comando_callback, mensaje_pregunta, opciones_botones):
	#sleep(3)
	btns = []
	# Creo los botones para elegir al usuario
	for opcion in opciones_botones:
		txtBoton = ""
		comando_op = opciones_botones[opcion]								
		for comando in comando_op["comandos"]:
			txtBoton += comando_op["comandos"][comando] + " "			
		txtBoton = txtBoton[:-1]
		datos = str(cid) + "*" + comando_callback + "*" + str(opcion) + "*" + str(uid)
		if "restriccion" in comando_op:
			if comando_op["restriccion"] == "admin" and uid in ADMIN:
				btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])
		else:
			btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])
	btnMarkup = InlineKeyboardMarkup(btns)
	#for uid in game.playerlist:
	bot.send_message(chat_donde_se_pregunta, mensaje_pregunta, reply_markup=btnMarkup)

# Comando para elegir el juego
#Se crea metodo general para crear jeugos
def command_newgame(bot, update):
	cid = update.message.chat_id
	uid = update.message.from_user.id
	try:
		game = GamesController.games.get(cid, None)
		groupType = update.message.chat.type
		groupName = update.message.chat.title
		if groupType not in ['group', 'supergroup']:
			bot.send_message(cid, "Tienes que agregarme a un grupo primero y escribir /newgame allá!")
		elif game:
			bot.send_message(cid, "Hay un juego comenzado en este chat. Si quieres terminarlo escribe /delete!")
		else:			
			# Busco si hay un juego ya creado
			game = get_game(cid)
			if game:
				bot.send_message(cid, "Hay un juego ya creado, borralo con /delete.")
			else:
								
				bot.send_message(cid, "Comenzamos eligiendo el juego a jugar")
				configurarpartida(bot, cid, uid)
	except Exception as e:
		bot.send_message(cid, str(e))

def command_configurar_partida(bot, update):
	cid, uid = update.message.chat_id, update.message.from_user.id
	configurarpartida(bot, cid, uid)
		
def configurarpartida(bot, cid, uid):
	frase_regex = "choosegame"
	pregunta_arriba_botones = "¿Qué juego quieres jugar?"
	chat_donde_se_pregunta = cid
	multipurpose_choose_buttons(bot, cid, uid, chat_donde_se_pregunta, frase_regex, pregunta_arriba_botones, JUEGOS_DISPONIBLES)
	
def callback_choose_game(bot, update):
	callback = update.callback_query
	log.info('callback_choose_game called: %s' % callback.data)	
	regex = re.search("(-[0-9]*)\*choosegame\*(.*)\*([0-9]*)", callback.data)
	cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
	bot.edit_message_text("Has elegido el juego: %s" % opcion, cid, callback.message.message_id)
	
	# Inicio el juego con los valores iniciales, el chat en que se va a jugar, el iniciador y el nombre del chat
	groupName = update.effective_chat.title
	
	game = CreateGame(cid, uid, opcion, groupName)
	
	modulos_disponibles_juego = MODULOS_DISPONIBES[opcion]
	
	# Si hay solo un modo de juego, lo pongo. Sino pregunto cual se quiere jugar
	if len(modulos_disponibles_juego) == 1:	
		game.modo = next(iter(modulos_disponibles_juego))
		bot.send_message(cid, "Solo hay un modulo y se pone ese %s" % game.modo)
		bot.send_message(cid, "Cada jugador puede unirse al juego con el comando /join.\nEl iniciador del juego (o el administrador) pueden unirse tambien y escribir /startgame cuando todos se hayan unido al juego!")
		save_game(cid, groupName, game, game.tipo)
		#save(bot, game.cid)
	else:
		frase_regex = "choosemode"
		pregunta_arriba_botones = "¿Qué modo de juego quieres jugar?"
		chat_donde_se_pregunta = cid
		multipurpose_choose_buttons(bot, cid, uid, chat_donde_se_pregunta, frase_regex, pregunta_arriba_botones, modulos_disponibles_juego)


def CreateGame(cid, uid, tipo, groupName):
	# Al momento solo SayAnything y Arcana tienen game custom
	if tipo == 'SayAnything':
		GamesController.games[cid] = GameSayAnything(cid, uid, groupName, tipo)	
	elif tipo == 'Arcana':
		GamesController.games[cid] = GameArcana(cid, uid, groupName, tipo)
	else:
		GamesController.games[cid] = Game(cid, uid, groupName, tipo)		
	return GamesController.games[cid]

def callback_choose_mode(bot, update):
	callback = update.callback_query
	log.info('callback_choose_mode called: %s' % callback.data)	
	regex = re.search("(-[0-9]*)\*choosemode\*(.*)\*([0-9]*)", callback.data)
	cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
	bot.edit_message_text("Has elegido el modo: %s" % opcion, cid, callback.message.message_id)
	game = get_game(cid)
	game.modo = opcion
	bot.send_message(cid, "Cada jugador puede unirse al juego con el comando /join.\nEl iniciador del juego (o el administrador) pueden unirse tambien y escribir /startgame cuando todos se hayan unido al juego!")
	save(bot, game.cid)
	
def command_join(bot, update, args):
	# I use args for testing. // Remove after?
	groupName = update.message.chat.title
	cid = update.message.chat_id
	groupType = update.message.chat.type
	game = get_game(cid)
	if len(args) <= 0:
		# if not args, use normal behaviour
		fname = update.message.from_user.first_name
		uid = update.message.from_user.id
	else:
		uid = update.message.from_user.id
		if uid == ADMIN:
			for i,k in zip(args[0::2], args[1::2]):
				fname = i
				uid = int(k)				
				game.add_player(uid, fname)
				log.info("%s (%d) joined a game in %d of type %s" % (fname, uid, game.cid, game.tipo))
	
	if groupType not in ['group', 'supergroup']:
		bot.send_message(cid, "Tienes que agregarme a un grupo primero y escribir /newgame allá!")
	elif not game:
		bot.send_message(cid, "No hay juego en este chat. Crea un nuevo juego con /newgame")
	elif game.board and not "permitir_ingreso_tardio" in JUEGOS_DISPONIBLES[game.tipo]:
		# Si el juego se ha comenzado, y no permite ingreso tardio...
		bot.send_message(cid, "El juego ha comenzado. Por favor espera el proximo juego!")
	elif uid in game.playerlist:
		bot.send_message(game.cid, "Ya te has unido al juego, %s!" % fname)
	else:
		#uid = update.message.from_user.id
		try:
			max_jugadores = MODULOS_DISPONIBES[game.tipo][game.modo]["max_jugadores"]
			min_jugadores = MODULOS_DISPONIBES[game.tipo][game.modo]["min_jugadores"]
			
			# Si se ha alcanzado el maximo de jugadores no te puedes unir.
			if len(game.playerlist) == max_jugadores:
				bot.send_message(game.cid, "Se ha alcanzado previamente el maximo de jugadores. Espera el proximo juego!")
			else:
				# Uno al jugador a la partida
				bot.send_message(uid, "Te has unido a un juego en %s." % groupName)
				player = game.add_player(uid, fname)
				log.info("%s (%d) joined a game in %s (%d) of type %s" % (fname, uid, groupName, game.cid, game.tipo))
				save(bot, game.cid)
				
				# Si se ha alcanzado el minimo o superado, y no esta ya empezado
				if len(game.playerlist) == max_jugadores and not game.board:
					command_startgame(bot, update)
				elif len(game.playerlist) >= min_jugadores:
					bot.send_message(game.cid, fname + " se ha unido al juego. Hay %s/%s jugadores.\nPueden poner /startgame para comenzar" % (str(len(game.playerlist)), max_jugadores))
				else:
					bot.send_message(game.cid, fname + " se ha unido al juego. Todavia no se ha llegado al minimo de jugadores. Faltan: %s " % (str(min_jugadores - len(game.playerlist))))
					
				# Si es un ingreso tardio ingreso al jugador en la player secuence
				if game.board:
					game.player_sequence.append(player)
					
		except Exception as e:
			bot.send_message(game.cid,
				fname + ", no puedo mandarte mensajes privados. Por favor anda a @MultiGamesByLevibot y hace click en \"Start\".\nLuego tiene que hacer /join de nuevo." + str(e))

def command_startgame(bot, update):
	log.info('command_startgame called')
	groupName = update.message.chat.title
	cid = update.message.chat_id
	game = get_game(cid)
	if not game:
		bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	#elif game.board:
	#	bot.send_message(cid, "The game is already running!")
	elif update.message.from_user.id not in ADMIN and update.message.from_user.id != game.initiator and bot.getChatMember(cid, update.message.from_user.id).status not in ("administrator", "creator"):
		bot.send_message(game.cid, "Solo el creador del juego o un admin puede iniciar con /startgame")	
	elif game.board:
		bot.send_message(cid, "El juego ya empezo!")
		
	else:
		
		# Verifico si la configuracion ha terminado y se han unido los jugadores necesarios		
		min_jugadores = MODULOS_DISPONIBES[game.tipo][game.modo]["min_jugadores"]
		
		if len(game.playerlist) >= min_jugadores:
			save(bot, game.cid)
			MainController.init_game(bot, game)
		else:
			bot.send_message(game.cid, "Falta el numero mínimo de jugadores. Faltan: %s " % (str(min_jugadores - len(game.playerlist))))
			
def command_roll(bot, update, args):	
	import GameCommands.SistemaD100Commands as SistemaD100Commands
	import GameCommands.HarryPotterCommands as HarryPotterCommands

	cid = update.message.chat_id
	uid = update.message.from_user.id
	# Me fijo si hay una partida, sino por defecto es D100
	game = get_game(cid)
	if game and uid in game.playerlist:
		#bot.send_message(cid, "*Juego encontrado*", ParseMode.MARKDOWN)
		if game.tipo == "SistemaD100":
			SistemaD100Commands.command_roll(bot, update, args)
		elif game.tipo == "HarryPotter":
			HarryPotterCommands.command_roll(bot, update, args)
		else:
			bot.send_message(cid, "*El juego no tiene commando roll*", ParseMode.MARKDOWN)
	else:
		SistemaD100Commands.command_roll(bot, update, args)

def simple_choose_buttons(bot, cid, uid, chat_donde_se_pregunta, comando_callback, mensaje_pregunta, opciones_botones):
	#sleep(3)
	btns = []
	# Creo los botones para elegir al usuario
	for key, value in opciones_botones.items():
		txtBoton = value
		datos = str(cid) + "*" + comando_callback + "*" + str(key) + "*" + str(uid)
		#if comando_callback == "announce":
		#	bot.send_message(ADMIN[0], datos)
		btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])
	btnMarkup = InlineKeyboardMarkup(btns)
	
	#for uid in game.playerlist:
	bot.send_message(chat_donde_se_pregunta, mensaje_pregunta, reply_markup=btnMarkup)		

def simple_choose_buttons_only_buttons(bot, cid, uid, comando_callback, opciones_botones):
	#sleep(3)
	btns = []
	# Creo los botones para elegir al usuario
	for key, value in opciones_botones.items():
		txtBoton = value
		datos = str(cid) + "*" + comando_callback + "*" + str(key) + "*" + str(uid)
		#if comando_callback == "announce":
		#	bot.send_message(ADMIN[0], datos)
		btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])
	return InlineKeyboardMarkup(btns)
	
	
def command_continue(bot, update, args):
	import JustOne.Commands as JustoneCommands
	import LostExpedition.Commands as LostExpeditionCommands
	
	log.info('command_continue called')
	
	try:
		cid, uid = update.effective_chat.id, update.effective_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	
	game = load_game(cid)
	if game:
		GamesController.games[cid] = game		
		if game.tipo == 'LostExpedition':
			LostExpeditionCommands.command_continue(bot, game, uid)
		elif game.tipo == 'JustOne':
			log.info('continue Just One Game called')
			JustoneCommands.command_continue(bot, game, uid)
		else:
			bot.send_message(cid, "El juego no tiene comando continue")			
	else:
		bot.send_message(cid, "No hay juego que continuar")
	
def command_jugadores(bot, update):	
	uid = update.message.from_user.id
	cid = update.message.chat_id
	
	game = get_game(cid)
	jugadoresActuales = "Los jugadores que se han unido al momento son:\n"
	for uid in game.playerlist:
		jugadoresActuales += "{}\n".format(helper.player_call(game.playerlist[uid]))
					
	bot.send_message(game.cid, jugadoresActuales, ParseMode.MARKDOWN)
	
def command_next_turn(bot, update):
	uid = update.message.from_user.id
	cid = update.message.chat_id
	game = get_game(cid)	
	MainController.start_next_round(bot, game)
	
def command_announce(bot, update, args):
	uid = update.message.from_user.id
	cid = update.message.chat_id
	# Solo Edu puede anunciar
	if uid == ADMIN[0]:
		# Lo pongo estatico ya que no anunciare en todos los tipos de juegos.
		opciones_botones = { "LostExpedition" : "Lost Expedition", "JustOne" : "Just One", "Todos" : "Todos" }
		if len(args) < 1:
			bot.send_message(game.cid, "Edu, tenes que poner un mensaje", ParseMode.MARKDOWN)
			return
		GamesController.announce_text = ' '.join(args)
		simple_choose_buttons(bot, cid, 1234, uid, "announce", "En que juegos queres anunciar", opciones_botones)

# Comando para que el bot nos recuerde los partidos que tenemos 	
def command_myturn(bot, update, args):
	uid = update.message.from_user.id
	cid = update.message.chat_id
	
	# Independeinte de si pide todos, tengo que obtenerlos a todos para saber cual es el de menos tiempo.
	all_games_unfiltered = MainController.getGamesByTipo("Todos")	
	# Me improtan los juegos que; Este el jugador, hayan sido iniciados, datinivote no sea null y que cumpla reglas del tipo de juego en particular
	all_games = {key:game for key, game in all_games_unfiltered.items() if uid in game.playerlist and game.board != None and verify_my_turn(game, uid) }
	
	# Le recuerdo solo el juego que mas tiempo lo viene esperando		
	#chat_id = min(all_games, key=lambda key: all_games[key].dateinitvote)
	try:
		chat_id = min(all_games, key=lambda key: datetime.datetime.now() if all_games[key].dateinitvote == None else all_games[key].dateinitvote)
		game_pendiente = all_games[chat_id]
		bot.send_message(uid, myturn_message(bot, game_pendiente , uid), ParseMode.MARKDOWN)
	except Exception as e:
		bot.send_message(uid, "*NO* tienes partidos pendientes", ParseMode.MARKDOWN)
		#ot.send_message(ADMIN[0], str(e))

def command_myturns(bot, update):
	uid = update.message.from_user.id
	cid = update.message.chat_id
	
	# Independeinte de si pide todos, tengo que obtenerlos a todos para saber cual es el de menos tiempo.
	all_games_unfiltered = MainController.getGamesByTipo("Todos")	
	# Me improtan los juegos que; Este el jugador, hayan sido iniciados, datinivote no sea null y que cumpla reglas del tipo de juego en particular
	all_games = {key:game for key, game in all_games_unfiltered.items() if uid in game.playerlist and game.board != None and verify_my_turn(game, uid) }
	for game_chat_id, game in all_games.items():		
		bot.send_message(uid, myturn_message(bot, game, uid), ParseMode.MARKDOWN)			
	if len(all_games) == 0:
		bot.send_message(uid, "*NO* tienes partidos pendientes", ParseMode.MARKDOWN)

def command_set_config_data(bot, update, args):
	uid = update.message.from_user.id
	cid = update.message.chat_id	
	if uid == ADMIN[0]:
		game = get_game(cid)
		try:
			game.configs[args[0]] = args[1]
		except Exception as e:
			# Si hay excepcion es que configs no existe
			game.configs = {}
			game.configs[args[0]] = args[1]
			log.info('command_set_config_data successfull: {}{}'.format(args[0], args[1]))
		save(bot, cid)
# TODO Poner estos metodos en helpers o usar los de cada juego en particular en su controller
def verify_my_turn(game, uid):
	import SayAnything.Commands as SayAnythingCommands
	
	if game.tipo == 'JustOne' or game.tipo == 'SayAnything':
		if game.tipo == 'JustOne' and game.board.state.fase_actual == "Proponiendo Pistas":
			return uid not in game.board.state.last_votes and uid != game.board.state.active_player.uid
		if game.tipo == 'SayAnything' and game.board.state.fase_actual == "Proponiendo Pistas":
			voto_jugador = next((x for x in game.board.state.ordered_votes if x.player.uid == uid), None)
			return (not voto_jugador) and uid != game.board.state.active_player.uid		
		elif game.board.state.fase_actual == "Revisando Pistas":
			return game.board.state.reviewer_player.uid == uid
		elif game.board.state.fase_actual == "Adivinando":
			return game.board.state.active_player.uid == uid
		elif game.board.state.fase_actual == "Votando Frases":
			return SayAnythingCommands.verify_missing_votes_user(game, uid)			
	return False

def myturn_message(bot, game, uid):
	try:
		if game.tipo == 'JustOne':
			return JustOneController.myturn_message(game, uid)
		elif game.tipo == 'SayAnything':
			if game.board.state.fase_actual == "Votando Frases":
				log.info("Fase: {} Grupo {}".format(game.board.state.fase_actual, game.groupName)
				SayAnythingController.send_vote_buttons(bot, game, uid)
				return "Te faltan votos"							
			log.info(game.groupName)
			return SayAnythingController.myturn_message(game, uid)			
	except Exception as e:
		return str(e)


def get_config_data(game, config_name):
	# Si por algun motivo tira excepcion siempre se devuelve None
	try:
		
		return game.configs.get(config_name, None)				
	except Exception as e:
		return None

def command_guess(bot, update, args):	
	import JustOne.Commands as JustoneCommands
	import SayAnything.Commands as SayAnythingCommands
	import Arcana.Commands as ArcanaCommands

	cid = update.message.chat_id
	uid = update.message.from_user.id
	# Me fijo si hay una partida, sino por defecto es D100
	game = get_game(cid)
	if game and uid in game.playerlist:
		#bot.send_message(cid, "*Juego encontrado*", ParseMode.MARKDOWN)
		if game.tipo == "JustOne":
			JustoneCommands.command_guess(bot, update, args)
		elif game.tipo == "Arcana":
			ArcanaCommands.command_guess(bot, update, args)
		else:
			bot.send_message(cid, "*El juego no tiene commando guess*", ParseMode.MARKDOWN)
	else:
		bot.send_message(cid, "*No estas en ninguna partida en la que puedas hacer guess*", ParseMode.MARKDOWN)

def command_pass(bot, update):	
	import JustOne.Commands as JustoneCommands
	import SayAnything.Commands as SayAnythingCommands
	import Arcana.Commands as ArcanaCommands

	cid = update.message.chat_id
	uid = update.message.from_user.id
	# Me fijo si hay una partida, sino por defecto es D100
	game = get_game(cid)
	if game and uid in game.playerlist:
		#bot.send_message(cid, "*Juego encontrado*", ParseMode.MARKDOWN)
		if game.tipo == "JustOne":
			JustoneCommands.command_pass(bot, update)
		elif game.tipo == "Arcana":
			ArcanaCommands.command_pass(bot, update)
		else:
			bot.send_message(cid, "*El juego no tiene commando pass*", ParseMode.MARKDOWN)
	else:
		bot.send_message(cid, "*No estas en ninguna partida en la que puedas hacer pass*", ParseMode.MARKDOWN)
	
'''
def command_addplayer(bot, update, args):	
	cid = update.message.chat_id
	uid = update.message.from_user.id
	groupName = update.message.chat.title
	groupType = update.message.chat.type
	
	game = get_game(cid)
	
	if game.tipo == 'JustOne':
		JustoneCommands.command_addplayer(bot, game, uid, args)
	
	
		

def command_removeplayer(bot, update, args):
	uid = update.message.from_user.id
	cid = update.message.chat_id
	# Solo Edu puede anunciar
	if update.message.from_user.id not in ADMIN and update.message.from_user.id != game.initiator and bot.getChatMember(cid, update.message.from_user.id).status not in ("administrator", "creator"):
		
		# Lo pongo estatico ya que no anunciare en todos los tipos de juegos.
		opciones_botones = { "LostExpedition" : "Lost Expedition", "JustOne" : "Just One", "Todos" : "Todos" }
		if len(args) < 1:
			bot.send_message(game.cid, "Edu, tenes que poner un mensaje", ParseMode.MARKDOWN)
			return
		GamesController.announce_text = ' '.join(args)
		simple_choose_buttons(bot, cid, 1234, uid, "announce", "En que juegos queres anunciar", opciones_botones)
'''
