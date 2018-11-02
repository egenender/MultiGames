import json
import logging as log
import datetime
#import ast
import jsonpickle
import os
import psycopg2
import urllib.parse
import sys
	
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

import MainController
import GamesController
from Constants.Config import STATS
from Boardgamebox.Board import Board
from Boardgamebox.Game import Game
from Boardgamebox.Player import Player
from Boardgamebox.State import State
from Constants.Config import ADMIN
from collections import namedtuple

from PIL import Image
from io import BytesIO

# Objetos que uso de prueba estaran en el state
from Constants.Cards import cartas_aventura
import random
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


def get_img_carta(num_carta):
	carta = cartas_aventura[num_carta]
	plastilla, fila, columna = carta["plastilla"], carta["fila"], carta["columna"]	
	url_img = '/app/img/LostExpedition/plastilla%s.jpg' % (plastilla)		
	img = Image.open(url_img)
	width, height = img.size
	widthCarta, heightCarta = width/3, height/3
	# Este switch se hace para corresponder al llamado del metodo, sino tendria que haber sido columna, fila.
	columna, fila = int(fila), int(columna)
	#log.info(img.size)
	x, y = (fila*widthCarta), (columna*heightCarta)
	#log.info(x)
	#log.info(y)
	left, top, right, bottom = x, y, widthCarta+x, heightCarta+y
	cropped = img.crop( ( left, top, right, bottom ) )
	return cropped

	

# The Lost Expedition
# Comando para mostrar la mano
# Conseguir que guarde en BD el juego actual y obtenerlo devuelta.
# Hacer comando para obtener X cantidad de cartas del mazo
# Hacer comando para ordenar las cartas obtenidas de la mano (Muestra la mano al finalizar)
# Hacer comando eliminar carta de la mano (Muestra la mano al finalizar)
# Crear Stats de la expedicion.
# Crear comando que disminuya los stats


# Generic commands for all games
def showImages(bot, cid, cartas):
	images = []
	for carta in cartas:
		images.append(get_img_carta(carta))

	widths, heights = zip(*(i.size for i in images))

	total_width = sum(widths)
	max_height = max(heights)

	new_im = Image.new('RGB', (total_width, max_height))

	x_offset = 0
	for im in images:
		new_im.paste(im, (x_offset,0))
		x_offset += im.size[0]

	bio = BytesIO()
	bio.name = 'image.jpeg'
	new_im.save(bio, 'JPEG')
	bio.seek(0)
	bot.send_photo(cid, photo=bio)
	
def save(bot, update):
	cid = update.message.chat_id
	groupName = update.message.chat.title
	game = GamesController.games.get(cid, None)
	gameType = 'LostExpedition'
	save_game(cid, groupName, gameType, game)

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
# Generic commands for all games

#Lost Expedition
def command_newgame_lost_expedition(bot, update):  
	cid = update.message.chat_id
	fname = update.message.from_user.first_name
	uid = update.message.from_user.id
	try:
		game = GamesController.games.get(cid, None)		
		if game:
			bot.send_message(cid, "There is currently a game running.")
		else:			
			#Search game in DB
			game = load_game(cid)			
			if game:
				GamesController.games[cid] = game
				bot.send_message(cid, "Hay un juego actualmente. Borralo para crear uno nuevo")				
				#bot.send_message(game.cid, game.board.print_board(game.playerlist))				      
				# Remember the current player that he has to act
				#MainController.start_round(bot, game)
			else:
				game = Game(cid, update.message.from_user.id)
				GamesController.games[cid] = game
				
				# Creo el jugador que creo el juego y lo agrego al juego
				player = Player(fname, uid)
				game.add_player(uid, player)				
				player_number = len(game.playerlist)
				bot.send_message(cid, "Se creo el juego y el usuario")
				game.board = Board(player_number, game)
				
				bot.send_message(cid, "Nuevo juego creado")						
	except Exception as e:
		bot.send_message(cid, 'Error '+str(e))

def command_drawcard(bot, update, args):
	cid = update.message.chat_id
	uid = update.message.from_user.id
	if uid == ADMIN:
		game = GamesController.games[cid]
		player = game.playerlist[uid]		
		cantidad = int(args[0])
		
		for i in range(cantidad):
			player.hand.append(game.board.cartasAventura.pop(0))		
		cid = '-1001206290323'
		showImages(bot, cid, player.hand)

def command_showhand(bot, update):
	
	cid = update.message.chat_id
	uid = update.message.from_user.id
	if uid == ADMIN:
		game = GamesController.games[cid]
		player = game.playerlist[uid]		
		cid = '-1001206290323'		
		showImages(bot, cid, player.hand)
		
def command_prueba(bot, update, args):
	#log.info(update.message.from_user.id)
	#log.info(update.message.chat_id)
	uid = update.message.from_user.id
	if uid == ADMIN:
		cid = '-1001206290323'
		#update.message.chat_id
		game = GamesController.games.get(cid, None)		
		cartas_juego_actual =  random.sample([*cartas_aventura], len([*cartas_aventura]))		
		cartas_mañana = []		
		for i in range(6):
			cartas_mañana.append(cartas_juego_actual.pop(0))				
		cartas_mañana.sort()
		showImages(bot, cid, cartas_mañana)		

commands = [  # command description used in the "help" command
    '/help - Gives you information about the available commands',
    '/start - Gives you a short piece of information about Secret Hitler',
    '/symbols - Shows you all possible symbols of the board',
    '/rules - Gives you a link to the official Secret Hitler rules',
    '/newgame - Creates a new game or Loads a previous game',
    '/join - Joins an existing game',
    '/startgame - Starts an existing game when all players have joined',
    '/cancelgame - Cancels an existing game. All data of the game will be lost',
    '/board - Prints the current board with fascist and liberals tracks, presidential order and election counter',
    '/history - Prints a History of the current game',
    '/votes - Prints who voted',
    '/calltovote - Calls the players to vote'    
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


		
		
def command_symbols(bot, update):
    cid = update.message.chat_id
    symbol_text = "The following symbols can appear on the board: \n"
    for i in symbols:
        symbol_text += i + "\n"
    bot.send_message(cid, symbol_text)


def command_board(bot, update):
	cid = update.message.chat_id
	if cid in GamesController.games.keys():
		game = GamesController.games[cid]
		if game.board:			
			bot.send_message(cid, game.board.print_board(game.playerlist))
		else:
			bot.send_message(cid, "There is no running game in this chat. Please start the game with /startgame")
	else:
		bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")

def command_start(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid,
                     "\"Secret Hitler is a social deduction game for 5-10 people about finding and stopping the Secret Hitler."
                     " The majority of players are liberals. If they can learn to trust each other, they have enough "
                     "votes to control the table and win the game. But some players are fascists. They will say whatever "
                     "it takes to get elected, enact their agenda, and blame others for the fallout. The liberals must "
                     "work together to discover the truth before the fascists install their cold-blooded leader and win "
                     "the game.\"\n- official description of Secret Hitler\n\nAdd me to a group and type /newgame to create a game!")
    command_help(bot, update)


def command_rules(bot, update):
    cid = update.message.chat_id
    btn = [[InlineKeyboardButton("Rules", url="http://www.secrethitler.com/assets/Secret_Hitler_Rules.pdf")]]
    rulesMarkup = InlineKeyboardMarkup(btn)
    bot.send_message(cid, "Read the official Secret Hitler rules:", reply_markup=rulesMarkup)


# pings the bot
def command_ping(bot, update):
    cid = update.message.chat_id
    bot.send_message(cid, 'pong - v0.3')


# prints statistics, only ADMIN
def command_stats(bot, update):
    cid = update.message.chat_id
    if cid == ADMIN:
        with open(STATS, 'r') as f:
            stats = json.load(f)
        stattext = "+++ Statistics +++\n" + \
                    "Liberal Wins (policies): " + str(stats.get("libwin_policies")) + "\n" + \
                    "Liberal Wins (killed Hitler): " + str(stats.get("libwin_kill")) + "\n" + \
                    "Fascist Wins (policies): " + str(stats.get("fascwin_policies")) + "\n" + \
                    "Fascist Wins (Hitler chancellor): " + str(stats.get("fascwin_hitler")) + "\n" + \
                    "Games cancelled: " + str(stats.get("cancelled")) + "\n\n" + \
                    "Total amount of groups: " + str(len(stats.get("groups"))) + "\n" + \
                    "Games running right now: "
        bot.send_message(cid, stattext)       


# help page
def command_help(bot, update):
    cid = update.message.chat_id
    help_text = "The following commands are available:\n"
    for i in commands:
        help_text += i + "\n"
    bot.send_message(cid, help_text)




def command_join(bot, update, args):
	# I use args for testing. // Remove after?
	groupName = update.message.chat.title
	cid = update.message.chat_id
	groupType = update.message.chat.type
	game = GamesController.games.get(cid, None)
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
				player = Player(fname, uid)
				game.add_player(uid, player)
				log.info("%s (%d) joined a game in %d" % (fname, uid, game.cid))
	
	if groupType not in ['group', 'supergroup']:
		bot.send_message(cid, "You have to add me to a group first and type /newgame there!")
	elif not game:
		bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	elif game.board:
		bot.send_message(cid, "The game has started. Please wait for the next game!")
	elif uid in game.playerlist:
		bot.send_message(game.cid, "You already joined the game, %s!" % fname)
	elif len(game.playerlist) >= 9:
		bot.send_message(game.cid, "You have reached the maximum amount of players. Please start the game with /startgame!")
	else:
		#uid = update.message.from_user.id
		player = Player(fname, uid)
		try:
			#Commented to dont disturb player during testing uncomment in production
			bot.send_message(uid, "You joined a game in %s. I will soon tell you your secret role." % groupName)			 
			game.add_player(uid, player)
			log.info("%s (%d) joined a game in %d" % (fname, uid, game.cid))
			if len(game.playerlist) > 4:
				bot.send_message(game.cid, fname + " has joined the game. Type /startgame if this was the last player and you want to start with %d players!" % len(game.playerlist))
			elif len(game.playerlist) == 1:
				bot.send_message(game.cid, "%s has joined the game. There is currently %d player in the game and you need 5-10 players." % (fname, len(game.playerlist)))
			else:
				bot.send_message(game.cid, "%s has joined the game. There are currently %d players in the game and you need 5-10 players." % (fname, len(game.playerlist)))
		except Exception:
			bot.send_message(game.cid,
				fname + ", I can\'t send you a private message. Please go to @xapi_prototype_bot and click \"Start\".\nYou then need to send /join again.")


def command_startgame(bot, update):
	log.info('command_startgame called')
	groupName = update.message.chat.title
	cid = update.message.chat_id
	game = GamesController.games.get(cid, None)
	if not game:
		bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	elif game.board:
		bot.send_message(cid, "The game is already running!")
	elif update.message.from_user.id != game.initiator and bot.getChatMember(cid, update.message.from_user.id).status not in ("administrator", "creator"):
		bot.send_message(game.cid, "Only the initiator of the game or a group admin can start the game with /startgame")
	elif len(game.playerlist) < 5:
		bot.send_message(game.cid, "There are not enough players (min. 5, max. 10). Join the game with /join")
	else:
		player_number = len(game.playerlist)
		MainController.init_game(bot, game, game.cid, player_number)		
		game.board = Board(player_number, game)
		log.info(game.board)
		log.info("len(games) Command_startgame: " + str(len(GamesController.games)))
		game.shuffle_player_sequence()
		game.board.state.player_counter = 0
		bot.send_message(game.cid, game.board.print_board(game.playerlist))
		#group_name = update.message.chat.title
		#bot.send_message(ADMIN, "Game of Secret Hitler started in group %s (%d)" % (group_name, cid))		
		#MainController.start_round(bot, game)
		#save_game(cid, groupName, game)

def command_cancelgame(bot, update):
	log.info('command_cancelgame called')
	cid = update.message.chat_id	
	#Always try to delete in DB
	delete_game(cid)
	if cid in GamesController.games.keys():
		game = GamesController.games[cid]
		status = bot.getChatMember(cid, update.message.from_user.id).status
		if update.message.from_user.id == game.initiator or status in ("administrator", "creator"):
			MainController.end_game(bot, game, 99)
		else:
			bot.send_message(cid, "Only the initiator of the game or a group admin can cancel the game with /cancelgame")
	else:
		bot.send_message(cid, "There is no game in this chat. Create a new game with /newgamelostexpedition")

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
							history_text += "%s registered a vote.\n" % (game.playerlist[player.uid].name)
						else:
							history_text += "%s didn't register a vote.\n" % (game.playerlist[player.uid].name)
					bot.send_message(cid, history_text)
				else:
					bot.send_message(cid, "Five minutes must pass to see the votes") 
		else:
			bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))

def command_calltovote(bot, update):
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
					# Only remember to vote to players that are still in the game
					history_text = ""
					for player in game.player_sequence:
						# If the player is not in last_votes send him reminder
						if player.uid not in game.board.state.last_votes:
							history_text += "It's time to vote [%s](tg://user?id=%d).\n" % (game.playerlist[player.uid].name, player.uid)
					bot.send_message(cid, text=history_text, parse_mode=ParseMode.MARKDOWN)
				else:
					bot.send_message(cid, "Five minutes must pass to see call to vote") 
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
		if cid in GamesController.games.keys():
			game = GamesController.games.get(cid, None)  
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
		if cid in GamesController.games.keys():
			uid = update.message.from_user.id
			game = GamesController.games.get(cid, None)			
			if uid in game.playerlist:				
				if game.board.state.currentround != 0:
					if len(args) > 0:
						#Data is being claimed
						claimtext = ' '.join(args)
						claimtexttohistory = "Player %s claims: %s" % (game.playerlist[uid].name, claimtext)
						bot.send_message(cid, "Your claim: %s was added to the history." % (claimtext))
						game.history[game.board.state.currentround - 1] += "\n\n%s" % (claimtexttohistory)
					else:					
						bot.send_message(cid, "You have to send a message to claim.")

				else:
					bot.send_message(cid, "You can't claim in the first round")
			else:
				bot.send_message(cid, "You must be a player to claim something in the game.")
				
		else:
			bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))
		log.error("Unknown error: " + str(e))    
		
def save_game(cid, groupName, game, gameType):
	#Check if game is in DB first
	cur = conn.cursor()			
	log.info("Searching Game in DB")
	query = "select * from games where id = %s;"
	cur.execute(query, [cid])
	dbdata = cur.fetchone()
	if cur.rowcount > 0:
		log.info('Updating Game')
		gamejson = jsonpickle.encode(game)
		#query = "UPDATE games SET groupName = %s, data = %s WHERE id = %s RETURNING data;"
		query = "UPDATE games_xapi_bot SET groupName = %s, tipojuego = %s, data = %s WHERE id = %s;"
		cur.execute(query, (groupName, gameType, gamejson, cid))
		#log.info(cur.fetchone()[0])
		conn.commit()		
	else:
		log.info('Saving Game in DB')
		gamejson = jsonpickle.encode(game)
		query = "INSERT INTO games_xapi_bot(id, groupName, tipojuego, data) VALUES (%s, %s, %s, %s);"
		#query = "INSERT INTO games(id , groupName  , data) VALUES (%s, %s, %s) RETURNING data;"
		cur.execute(query, (cid, groupName, gameType, gamejson))
		#log.info(cur.fetchone()[0])
		conn.commit()

def load_game(cid):
	cur = conn.cursor()			
	log.info("Searching Game in DB")
	query = "SELECT * FROM games WHERE id = %s;"
	cur.execute(query, [cid])
	dbdata = cur.fetchone()

	if cur.rowcount > 0:
		log.info("Game Found")
		jsdata = dbdata[3]
		#log.info("jsdata = %s" % (jsdata))				
		game = jsonpickle.decode(jsdata)
		
		# For some reason the decoding fails when bringing the dict playerlist and it changes it id from int to string.
		# So I have to change it back the ID to int.				
		temp_player_list = {}		
		for uid in game.playerlist:
			temp_player_list[int(uid)] = game.playerlist[uid]
		game.playerlist = temp_player_list		
		#bot.send_message(cid, game.print_roles())
		return game
	else:
		log.info("Game Not Found")
		return None

def delete_game(cid):
	cur = conn.cursor()
	log.info("Deleting Game in DB")
	query = "DELETE FROM games WHERE id = %s;"
	cur.execute(query, [cid])
	conn.commit()
	
def command_ver(bot, update, args):
	try:
		#Send message of executing command   
		cid = update.message.chat_id
		#bot.send_message(cid, "Looking for history...")
		#Check if there is a current game 
		if cid in GamesController.games.keys():
			game = GamesController.games.get(cid, None)
			uid = update.message.from_user.id
			if len(args) > 0:
				player = game.find_player(args[0])
				if player:
					bot.send_message(uid, "El jugador %s %s esta poseido" % (player.name, "" if player.poseido else "no")) 
				else:
					bot.send_message(cid, "El jugador no existe en esta partida") 
			else:					
				bot.send_message(cid, "Se tiene que pasar un jugador para ver.") 
		else:
			bot.send_message(cid, "No hay juego en este chat. Crea un juego con /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))
		
def command_otra(bot, update, args):
	try:
		#Send message of executing command   
		cid = update.message.chat_id
		#bot.send_message(cid, "Looking for history...")
		#Check if there is a current game 
		if cid in GamesController.games.keys():
			game = GamesController.games.get(cid, None)
			uid = update.message.from_user.id
			if len(args) > 0:
				player = game.find_player(args[0])
				if player:
					bot.send_message(uid, "El jugador '%s ha sido afectado por acción 'otra" % (player.name)) 
				else:
					bot.send_message(cid, "El jugador no existe en esta partida") 
			else:					
				bot.send_message(cid, "Se tiene que pasar un jugador para ver.") 
		else:
			bot.send_message(cid, "No hay juego en este chat. Crea un juego con /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))

def command_limpiar(bot, update, args):
	try:
		#Send message of executing command   
		cid = update.message.chat_id
		#bot.send_message(cid, "Looking for history...")
		#Check if there is a current game 
		if cid in GamesController.games.keys():
			game = GamesController.games.get(cid, None)
			
			if len(args) > 0:
				player = game.find_player(args[0])
				if player:
					if len(args) > 1:
						try:							
							player.tokens_posesion -= int(args[1])
							bot.send_message(cid, "El jugador %s ha perdido %s %s de posesión" % (args[0], args[1], "tokens" if int(args[1]) > 1 else "token"))								
							bot.send_message(game.cid, game.board.print_board(game.playerlist))
						except Exception as e:
							bot.send_message(cid, str(e))
					else:
						player.tokens_posesion -= 1
						bot.send_message(cid, "El jugador %s ha perdido un token de posesión" % (args[0]))
						bot.send_message(game.cid, game.board.print_board(game.playerlist))
				else:
					bot.send_message(cid, "El jugador no existe en esta partida") 
			else:				
				'''
				for player in game.player_sequence:
					player.tokens_posesion -= 1							
				bot.send_message(cid, "Todos los jugadores han ganado un token de posesión") 
				bot.send_message(game.cid, game.board.print_board(game.playerlist))
				'''
				bot.send_message(cid, "Se debe elegir a un jugador") 
		else:
			bot.send_message(cid, "No hay juego en este chat. Crea un juego con /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))
		
def command_infect(bot, update, args):
	try:
		#Send message of executing command   
		cid = update.message.chat_id
		#bot.send_message(cid, "Looking for history...")
		#Check if there is a current game 
		if cid in GamesController.games.keys():
			game = GamesController.games.get(cid, None)
			
			if len(args) > 0:
				player = game.find_player(args[0])
				if player:
					if len(args) > 1:
						try:							
							player.tokens_posesion += int(args[1])
							bot.send_message(cid, "El jugador %s ha ganado %s %s de posesión" % (args[0], args[1], "tokens" if int(args[1]) > 1 else "token"))								
							bot.send_message(game.cid, game.board.print_board(game.playerlist))
						except Exception as e:
							bot.send_message(cid, str(e))
					else:
						player.tokens_posesion += 1
						bot.send_message(cid, "El jugador %s ha ganado un token de posesión" % (args[0]))
						bot.send_message(game.cid, game.board.print_board(game.playerlist))
				else:
					bot.send_message(cid, "El jugador no existe en esta partida") 
			else:				
				for player in game.player_sequence:
					player.tokens_posesion += 1							
				bot.send_message(cid, "Todos los jugadores han ganado un token de posesión") 
				bot.send_message(game.cid, game.board.print_board(game.playerlist))
		else:
			bot.send_message(cid, "No hay juego en este chat. Crea un juego con /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))
		
def call_to_action(bot, update):
	try:
		#Send message of executing command   
		cid = update.message.chat_id
		#bot.send_message(cid, "Looking for history...")
		#Check if there is a current game 
		if cid in GamesController.games.keys():
			game = GamesController.games.get(cid, None)
			MainController.start_round(bot, game)		
		else:
			bot.send_message(cid, "No hay juego en este chat. Crea un juego con /newgame")
	except Exception as e:
		bot.send_message(cid, str(e))
		
#Testing commands
def command_ja(bot, update):
	uid = update.message.from_user.id
	if uid == ADMIN:
		cid = update.message.chat_id
		game = GamesController.games.get(cid, None)
		answer = "Ja"
		for uid in game.playerlist:
			game.board.state.last_votes[uid] = answer
		MainController.count_votes(bot, game)
	

def command_nein(bot, update):	
	uid = update.message.from_user.id
	if uid == ADMIN:
		cid = update.message.chat_id
		game = GamesController.games.get(cid, None)
		answer = "Nein"
		for uid in game.playerlist:
			game.board.state.last_votes[uid] = answer
		MainController.count_votes(bot, game)

def command_elegimos(bot, update, args):
	uid = update.message.from_user.id
	if uid == ADMIN:
		if len(args) > 0:
			cid = update.message.chat_id
			game = GamesController.games.get(cid, None)		
			for uid in game.playerlist:
				game.board.state.last_votes[uid] = args[0]
			MainController.count_actions(bot, game)
		

# Secret Moon

secret_moon_cid = '-1001206290323'

def command_newgame_secret_moon(bot, update, args):  
	cid = update.message.chat_id
	
	try:
		game = GamesController.games.get(secret_moon_cid, None)		
		if game:
			bot.send_message(cid, "There is currently a game running.")
		else:			
			#Search game in DB
			game = load_game(cid)			
			if game:
				GamesController.games[cid] = game
				bot.send_message(cid, "There is currently a game running. If you want to end it please type /cancelgame!")				
				bot.send_message(game.cid, game.board.print_board(game.playerlist))				
				# Remember the current player that he has to act
				MainController.start_round(bot, game)
			else:
				GamesController.games[cid] = Game(secret_moon_cid, update.message.from_user.id)
				bot.send_message(secret_moon_cid, "New game created! Each player has to /joinsecretmoon in my private chat.\nThe initiator of this game (or the admin) can /join too and type /startgamesecretmoon when everyone has joined the game!")
						
	except Exception as e:
		bot.send_message(cid, str(e))
		
def command_join_secret_moon(bot, update):
	# I use args for testing. // Remove after?
	groupName = update.message.chat.title
	cid = update.message.chat_id
	groupType = update.message.chat.type
	game = GamesController.games.get(cid, None)
	
	if not game:
		bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	elif game.board:
		bot.send_message(cid, "The game has started. Please wait for the next game!")
	elif uid in game.playerlist:
		bot.send_message(game.cid, "You already joined the game, %s!" % fname)
	elif len(game.playerlist) >= 7:
		bot.send_message(game.cid, "You have reached the maximum amount of players. Please start the game with /startgame!")
	else:
		#uid = update.message.from_user.id
		player = Player(fname, uid)
		try:
			#Commented to dont disturb player during testing uncomment in production
			bot.send_message(uid, "You joined a game in %s. I will soon tell you your secret role." % groupName)			 
			game.add_player(uid, player)
			log.info("%s (%d) joined a game in %d" % (fname, uid, game.cid))
			if len(game.playerlist) > 4:
				bot.send_message(game.cid, fname + " has joined the game. Type /startgame if this was the last player and you want to start with %d players!" % len(game.playerlist))
			elif len(game.playerlist) == 1:
				bot.send_message(game.cid, "%s has joined the game. There is currently %d player in the game and you need 5-8 players." % (fname, len(game.playerlist)))
			else:
				bot.send_message(game.cid, "%s has joined the game. There are currently %d players in the game and you need 5-8 players." % (fname, len(game.playerlist)))
		except Exception:
			bot.send_message(game.cid,
				fname + ", I can\'t send you a private message. Please go to @xapi_prototype_bot and click \"Start\".\nYou then need to send /join again.")

			
def command_startgame_secret_moon(bot, update):
	log.info('command_startgame called')
	groupName = update.message.chat.title
	cid = update.message.chat_id
	game = GamesController.games.get(secret_moon_cid, None)
	if not game:
		bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	elif game.board:
		bot.send_message(cid, "The game is already running!")
	elif uid != ADMIN:
		bot.send_message(game.cid, "Only the Master Administrator can start the game")
	elif len(game.playerlist) < 4:
		bot.send_message(game.cid, "There are not enough players (min. 5, max. 8). Join the game with /join")
	else:
		player_number = len(game.playerlist)
		MainController.init_game(bot, game, game.cid, player_number)		
		game.board = Board(player_number, game)
		log.info(game.board)
		log.info("len(games) Command_startgame: " + str(len(GamesController.games)))
		game.shuffle_player_sequence()
		game.board.state.player_counter = 0
		bot.send_message(game.cid, game.board.print_board(game.playerlist))
		#group_name = update.message.chat.title
		#bot.send_message(ADMIN, "Game of Secret Hitler started in group %s (%d)" % (group_name, cid))		
		#MainController.start_round(bot, game)
		#save_game(cid, groupName, game)

# End Secret Moon
