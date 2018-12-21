#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Eduardo Peluffo"

import json
import logging as log
import random
import re
from random import randrange, choice
from time import sleep

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ForceReply
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters)

import Commands

# Importo los controladores de todos los juegos que vaya agregando
import Controllers.JustOneController as JustOneController

# Importo los comandos de los juegos que vaya agregando
import GameCommands.JustoneCommands as JustoneCommands
import GameCommands.LostExpeditionCommands as LostExpeditionCommands

from Constants.Cards import playerSets, actions
from Constants.Config import TOKEN, STATS, ADMIN
from Boardgamebox.Game import Game
from Boardgamebox.Player import Player
from Boardgamebox.Board import Board

from Utils.helpers import helper

import GamesController
import datetime

import os
import psycopg2
import urllib.parse

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
'''
cur = conn.cursor()
query = "SELECT ...."
cur.execute(query)
'''

debugging = False

def player_call(player):
	return "[{0}](tg://user?id={1})".format(player.name, player.uid)

def init_game(bot, game):
	log.info('Game Init called')
	player_number = len(game.playerlist)
	game.board = Board(player_number, game)	
	bot.send_message(game.cid, "Juego iniciado")
	if game.tipo == "LostExpedition":
		init_lost_expedition(bot, game, player_number)
	elif game.tipo == "JustOne":
		JustOneController.init_game(bot, game)


def init_lost_expedition(bot, game, player_number):
	log.info('Game init_lost_expedition called')	
	
	if player_number == 1:		
		bot.send_message(game.cid, "Vamos a llegar al dorado. Es un hermoso /dia!")
		# Aca deberia preguntar dificultad y modulos a usar.
		# Eso setearia la vida inicial y los personajes que tendria.
	else:
		# Se mezcla el orden de los jugadores.
		game.shuffle_player_sequence()
		# TODO Se deberia decir quien es el lider actual 
		bot.send_message(game.cid, "Vamos a llegar al dorado. Es un hermoso /dia!")
	
def call_to_action(bot, game):
        log.info('call_to_action called')
        #When voting starts we start the counter to see later with the vote command if we can see you voted.
        game.dateinitvote = datetime.datetime.now()

        strcid = str(game.cid)        
        btns = []        
        for actionid in actions:
                costo = actions[actionid]["costo"]
                comando = actions[actionid]["comando"]
                btns.append([InlineKeyboardButton("%s (%s)" % (actionid, costo), callback_data=strcid + "_action_" + comando)])        
        
        voteMarkup = InlineKeyboardMarkup(btns)
        for uid in game.playerlist:
                if not debugging:
                        bot.send_message(uid, "¿Cuál acción desea realizar?", reply_markup=voteMarkup)
                else:
                        bot.send_message(ADMIN, "¿Cuál acción desea realizar?", reply_markup=voteMarkup)

def handle_action(bot, update):
    callback = update.callback_query
    log.info('handle_action called: %s' % callback.data)
    regex = re.search("(-[0-9]*)_action_(.*)", callback.data)
    cid = int(regex.group(1))
    answer = regex.group(2)
    strcid = regex.group(1)
    try:
        game = GamesController.games[cid]
        uid = callback.from_user.id
        
        bot.edit_message_text("Has elegido la accion %s" % (answer), uid, callback.message.message_id)
        log.info("El jugador %s (%d) eligio la acción %s" % (callback.from_user.first_name, uid, answer))
        
        #if uid not in game.board.state.last_votes:
        game.board.state.last_votes[uid] = answer
        
        #Allow player to change his vote
        btns = []        
        for actionid in actions:
                costo = actions[actionid]["costo"]
                comando = actions[actionid]["comando"]
                btns.append([InlineKeyboardButton("%s (%s)" % (actionid, costo), callback_data=strcid + "_action_" + comando)])        
        
        voteMarkup = InlineKeyboardMarkup(btns)
                
        if not debugging:
                bot.send_message(uid, "Podes cambiar tu accion aca.\n¿Cuál acción desea realizar?", reply_markup=voteMarkup)
        else:
                bot.send_message(ADMIN, "Podes cambiar tu accion aca.\n¿Cuál acción desea realizar?", reply_markup=voteMarkup)
        
        #Commands.save_game(game.cid, "Saved Round %d" % (game.board.state.currentround), game)
        if len(game.board.state.last_votes) == len(game.player_sequence):
                count_votes(bot, game)
    except Exception as e:
        log.error(str(e))
                        
def count_actions(bot, game):
        # La votacion ha finalizado.
        game.dateinitvote = None
        # La votacion ha finalizado.
        log.info('count_actions called')
        action_text = ""        
        for player in game.player_sequence:                
                action_text += "%s eligio la accion: %s\n" % (game.playerlist[player.uid].name, game.board.state.last_votes[player.uid])                
        game.history.append("Round %d\n\n" % (game.board.state.currentround + 1) + action_text)
        bot.send_message(game.cid, "%s\nAhora planifiquen el uso de sus acciones." % (action_text))                    


		
##
#
# End of round
#
##

def end_game(bot, game, game_endcode):
        log.info('end_game called')
        ##
        # game_endcode:
        #   -2  fascists win by electing Hitler as chancellor
        #   -1  fascists win with 6 fascist policies
        #   0   not ended
        #   1   liberals win with 5 liberal policies
        #   2   liberals win by killing Hitler
        #   99  game cancelled
        #
        '''
        if game_endcode == 99:
                if GamesController.games[game.cid].board is not None:
                        bot.send_message(game.cid, "Game cancelled!\n\n%s" % game.print_roles())
                else:
                        bot.send_message(game.cid, "Game cancelled!")
        else:
                if game_endcode == -2:
                        bot.send_message(game.cid, "Game over! The fascists win by electing Hitler as Chancellor!\n\n%s" % game.print_roles())
                if game_endcode == -1:
                        bot.send_message(game.cid, "Game over! The fascists win by enacting 6 fascist policies!\n\n%s" % game.print_roles())
                if game_endcode == 1:
                        bot.send_message(game.cid, "Game over! The liberals win by enacting 5 liberal policies!\n\n%s" % game.print_roles())
                if game_endcode == 2:
                        bot.send_message(game.cid, "Game over! The liberals win by killing Hitler!\n\n%s" % game.print_roles())
        '''
        del GamesController.games[game.cid]
        Commands.delete_game(game.cid)
        
def increment_player_counter(game):
    log.info('increment_player_counter called')
    if game.board.state.player_counter < len(game.player_sequence) - 1:
        game.board.state.player_counter += 1
    else:
        game.board.state.player_counter = 0

def callback_announce(bot, update):	
	callback = update.callback_query
	log.info('callback_announce called: %s' % callback.data)
	try:		
		#log.info('callback_finish_game_buttons called: %s' % callback.data)	
		regex = re.search("(-?[0-9]*)\*announce\*(.*)\*(-?[0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
		
		mensaje_edit = "Has elegido anunciar en partidos de: {0}".format(opcion)
		try:
			bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
		except Exception as e:
			bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)				
		
		games = getGamesByTipo(opcion)
		
		
		
		mensaje = '‼️Anuncio cambios en {0}‼️\n\n{1}'.format(opcion, GamesController.announce_text)
		
		players = {}
		# Pongo a todos los jugadores en partidos de tal tipo
		for game_chat_id, game in games.items():
			players.update(game.playerlist)
			
		for uid, player in players.items():
			bot.send_message(uid, mensaje, ParseMode.MARKDOWN)
		
		# Mensajes a todos los juegos con el tipo de juego		
		#for game_chat_id, game in games.items():
		#	bot.send_message(game_chat_id, GamesController.announce_text, ParseMode.MARKDOWN)
		
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando debido a: '+str(e))
		bot.send_message(ADMIN[0], callback.data)

def getGamesByTipo(opcion):
	games = None
	cursor = conn.cursor()			
	log.info("Executing in DB")
	if opcion != "Todos":
		query = "select * from games g where g.tipojuego = '{0}'".format(opcion)
	else:
		query = "select * from games g"
	
	cursor.execute(query)
	if cursor.rowcount > 0:
		# Si encuentro juegos los busco a todos y los cargo en memoria
		for table in cursor.fetchall():
			if table[0] not in GamesController.games.keys():
				Commands.get_game(table[0])
		# En el futuro hacer que pueda hacer anuncios globales a todos los juegos ?
		games_restriction = [opcion]
		#bot.send_message(uid, "Obtuvo esta cantidad de juegos: {0}".format(len(GamesController.games)))
		# Luego aplico
		if opcion != "Todos":
			games = {key:val for key, val in GamesController.games.items() if val.tipo in games_restriction}
		else:
			games = GamesController.games		
	return games
		
def error(bot, update, error):
        #bot.send_message(387393551, 'Update "%s" caused error "%s"' % (update, error) ) 
        # Voy a re intentar automaticamente hasta X cantidad de veces
	if str(error) == "Timed out":
		try:
			logger.warning("El chat es: %s del usuario %s" % (update.effective_chat.id, update.effective_user.id))
			#"%s" por el usuario "%s"' % (update.message.chat.id, update.message.from.id))
			#bot.send_message(update.effective_chat.id, "Debido a Time Out se recomienda seguis con /continue si esto no responde probar /dia /noche o /resolve")
			# Obtengo el juego actual
			'''game = Commands.get_game(update.effective_chat.id)
			uid = update.effective_user.id
			if game is not None:
				recover(bot, update, game, uid)
			'''
			#Commands.command_continue(bot, update, [None, update.message.chat.id, update.effective_user.id])
		except Exception as e:
			logger.warning('Error al tratar de obtener cid y uid. Error: %s' % str(e))                

	logger.warning('Update "%s" caused error "%s"' % (update, error))
        
# Metodo para recuperarse despues de un error de time out	
def recover(bot, update, game, uid):
	if game.tipo == "LostExpedition":
		recover_lost_expedition(bot, update, game, uid)
		
def recover_lost_expedition(bot, update, game, uid):
	# Si el juego no esta empezado, o no esta en ninguna fase. No hago nada.
	if game.board != None:		
		if game.board.state.fase_actual != None:
			if game.board.state.fase_actual == "resolve":
				# Si estaba en resolve quiere decir que hay que hacer el resolve.
				Commands.resolve(bot, game.cid, uid, game, game.playerlist[uid])
			elif game.board.state.fase_actual == "execute_actions":
				Commands.command_continue(bot, update, [None, game.cid, uid])

def echo(bot, update):
	if update.effective_user.id == ADMIN[0]:
		#bot.send_message(chat_id=ADMIN[0], text=update.message.text)
		# update.effective_chat.id
		#bot.send_message(ADMIN[0], text=update.message.text)
		mensaje = update.message.text.replace("Leviatas", "Levi")
		bot.send_message(update.effective_chat.id, text=mensaje)
		bot.edit_message_text(mensaje, update.effective_chat.id, update.message.message_id)
	#bot.send_message(chat_id=update.message.chat_id, text="Eco!")
	#logger.warning("El chat es: %s del usuario %s" % (update.effective_chat.id, update.effective_user.id))
	#Solo hace echo si soy yo.
	#log.info('Echo called')
	#if update.effective_user.id == ADMIN[0]:
	#	bot.send_message(chat_id=ADMIN[0], text=update.message.text)
	#	#bot.send_message(ADMIN[0], text=update.message.text)

def unknown(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="No conozco ese comando")

def add_group(bot, update):
	bot.send_message(ADMIN[0], "Entro en add new member")
	groupname = update.message.chat.title
	for members in update.message.new_chat_members:
        	bot.send_message(ADMIN[0], text="{username} {id} add group".format(username=members.username, id=member.id, groupname = groupname))
		
def remove_group(bot, update):
	bot.send_message(ADMIN[0], "Entro en remove member")
	member = update.message.left_chat_member
	groupname = update.message.chat.title
	bot.send_message(ADMIN[0], text="{username} {id} left group {groupname}".format(username=member.username, id=member.id, groupname = groupname))
	#for members in update.message.left_chat_member:
        #	bot.send_message(ADMIN[0], text="{username} {id} add group".format(username=members.username, id=member.id))
	
def main():
	GamesController.init() #Call only once
	#initialize_testdata()

	#Init DB Create tables if they don't exist   
	log.info('Init DB in MultiGames Bot')
	conn.autocommit = True
	cur = conn.cursor()
	cur.execute(open("DBCreate.sql", "r").read())
	log.info('DB Created/Updated')
	conn.autocommit = False
	'''
	log.info('Insertando')
	query = "INSERT INTO users(facebook_id, name , access_token , created) values ('2','3','4',1) RETURNING id;"
	log.info('Por ejecutar')
	cur.execute(query)       
	user_id = cur.fetchone()[0]        
	log.info(user_id)


	query = "SELECT ...."
	cur.execute(query)
	'''

	#PORT = int(os.environ.get('PORT', '8443'))
	updater = Updater(TOKEN)

	# DEscomentar para Webhook acordarse de cambiar el tipo de bot a web
	'''
	updater.start_webhook(listen="0.0.0.0",
		      port=PORT,
		      url_path=TOKEN,
		      key='8ca9c17937b0699c7643b1084d97d2b40a4ceadc75f32d9914ceffcff873')
	updater.bot.set_webhook("https://multigames.herokuapp.com/" + TOKEN)
	'''              

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", Commands.command_start))
	dp.add_handler(CommandHandler("help", Commands.command_help))
	dp.add_handler(CommandHandler("board", Commands.command_board))
	dp.add_handler(CommandHandler("rules", Commands.command_rules))
	dp.add_handler(CommandHandler("symbols", Commands.command_symbols))
	dp.add_handler(CommandHandler("players", Commands.command_jugadores))
	dp.add_handler(CommandHandler("newgame", Commands.command_newgame))
	dp.add_handler(CommandHandler("startgame", Commands.command_startgame))
	dp.add_handler(CommandHandler("delete", Commands.command_cancelgame))
	dp.add_handler(CommandHandler("join", Commands.command_join, pass_args = True))
	dp.add_handler(CommandHandler("history", Commands.command_showhistory))
	dp.add_handler(CommandHandler("votes", Commands.command_votes))
	dp.add_handler(CommandHandler("call", Commands.command_call))
	dp.add_handler(CommandHandler("claim", Commands.command_claim, pass_args = True))	
	dp.add_handler(CommandHandler("prueba", Commands.command_prueba, pass_args = True))	
	# Comando para hacer comandos sql desde el chat
	dp.add_handler(CommandHandler("comando", Commands.command_newgame_sql_command, pass_args = True))
	dp.add_handler(CommandHandler("hojaayuda", Commands.command_hoja_ayuda))
	dp.add_handler(CommandHandler("reglas", Commands.command_reglas))	
	dp.add_handler(CommandHandler("save", Commands.save))
	dp.add_handler(CommandHandler("load", Commands.load))
	# Comando para preguntar los juegos que esperan mi accion.
	dp.add_handler(CommandHandler("myturn", Commands.command_myturn, pass_args = True))
	dp.add_handler(CommandHandler("myturns", Commands.command_myturns))
	
	# Configuracion de cualquier partida
	dp.add_handler(CommandHandler("config", Commands.command_configurar_partida))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*choosegame\*(.*)\*([0-9]*)", callback=Commands.callback_choose_game))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*choosemode\*(.*)\*([0-9]*)", callback=Commands.callback_choose_mode))
	
	# Herramientas de ADMIN
	dp.add_handler(CommandHandler("ann", Commands.command_announce, pass_args = True))
	dp.add_handler(CallbackQueryHandler(pattern="(-?[0-9]*)\*announce\*(.*)\*(-?[0-9]*)", callback=callback_announce))
	
	# Lost Expedition Commands
	dp.add_handler(CommandHandler("newgamelostexpedition", LostExpeditionCommands.command_newgame_lost_expedition))
	dp.add_handler(CommandHandler("drawcard", LostExpeditionCommands.command_drawcard, pass_args = True))
	dp.add_handler(CommandHandler("showhand", LostExpeditionCommands.command_showhand, pass_args = True))
	dp.add_handler(CommandHandler("losebullet", LostExpeditionCommands.command_losebullet, pass_args = True))
	dp.add_handler(CommandHandler("gainbullet", LostExpeditionCommands.command_gainbullet, pass_args = True))
	dp.add_handler(CommandHandler("losefood", LostExpeditionCommands.command_losefood, pass_args = True))
	dp.add_handler(CommandHandler("gainfood", LostExpeditionCommands.command_gainfood, pass_args = True))        
	dp.add_handler(CommandHandler("stats", LostExpeditionCommands.command_showstats))
	dp.add_handler(CommandHandler("campero", LostExpeditionCommands.command_vida_explorador_campero, pass_args = True))
	dp.add_handler(CommandHandler("brujula", LostExpeditionCommands.command_vida_explorador_brujula, pass_args = True))
	dp.add_handler(CommandHandler("hoja", LostExpeditionCommands.command_vida_explorador_hoja, pass_args = True))
	dp.add_handler(CommandHandler("addrutefromhand", LostExpeditionCommands.command_add_exploration, pass_args = True))
	dp.add_handler(CommandHandler("addrutefromdeck", LostExpeditionCommands.command_add_exploration_deck, pass_args = True))
	dp.add_handler(CommandHandler("addrutefromhandfirst", LostExpeditionCommands.command_add_exploration_first, pass_args = True))
	dp.add_handler(CommandHandler("moverutefirst", LostExpeditionCommands.command_add_exploration_deck_first, pass_args = True))
	dp.add_handler(CommandHandler("swaprute", LostExpeditionCommands.command_swap_exploration, pass_args = True))
	dp.add_handler(CommandHandler("removerute", LostExpeditionCommands.command_remove_exploration, pass_args = True))
	dp.add_handler(CommandHandler("removelastrute", LostExpeditionCommands.command_remove_last_exploration, pass_args = True))
	dp.add_handler(CommandHandler("showrute", LostExpeditionCommands.command_show_exploration, pass_args = True))
	dp.add_handler(CommandHandler("sortrute", LostExpeditionCommands.command_sort_exploration_rute, pass_args = True))
	dp.add_handler(CommandHandler("sorthand", LostExpeditionCommands.command_sort_hand, pass_args = True))
	dp.add_handler(CommandHandler("showskills", LostExpeditionCommands.command_showskills))
	dp.add_handler(CommandHandler("gainprogreso", LostExpeditionCommands.command_increase_progreso, pass_args = True))
	dp.add_handler(CommandHandler("removefirstrute", LostExpeditionCommands.command_resolve_exploration))
	dp.add_handler(CommandHandler("gainskill", LostExpeditionCommands.command_gain_skill, pass_args = True))
	dp.add_handler(CommandHandler("useskill", LostExpeditionCommands.command_use_skill, pass_args = True))
	dp.add_handler(CommandHandler("losecamp", LostExpeditionCommands.command_lose_camp, pass_args = True))
	dp.add_handler(CommandHandler("losecompass", LostExpeditionCommands.command_lose_compass, pass_args = True))
	dp.add_handler(CommandHandler("loseleaf", LostExpeditionCommands.command_lose_leaf, pass_args = True))
	dp.add_handler(CommandHandler("loseexplorer", LostExpeditionCommands.command_lose_explorer, pass_args = True))
	dp.add_handler(CommandHandler("resolve", LostExpeditionCommands.command_resolve_exploration2))
	dp.add_handler(CommandHandler("continue", Commands.command_continue, pass_args = True))
	dp.add_handler(CommandHandler("dia", LostExpeditionCommands.command_worflow, pass_args = True))
	dp.add_handler(CommandHandler("noche", LostExpeditionCommands.command_worflow, pass_args = True))
	# Lost Expedition Callbacks de botones
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*exe\*([^_]*)\*(.*)\*([0-9]*)", callback=LostExpeditionCommands.execute_command))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*opcioncomandos\*(.*)\*([0-9]*)", callback=LostExpeditionCommands.elegir_opcion_comando))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*opcionskill\*(.*)\*([0-9]*)", callback=LostExpeditionCommands.elegir_opcion_skill))	
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*commando\*([^_]*)\*swap\*([0-9]*)", callback=LostExpeditionCommands.callback_choose_swap))
			
	# Handlers de JustOne
	dp.add_handler(CommandHandler("sendclues", JustoneCommands.command_forced_clue))
	dp.add_handler(CommandHandler("nextturn", JustoneCommands.command_next_turn))
	dp.add_handler(CommandHandler("guess", JustoneCommands.command_guess, pass_args = True))
	dp.add_handler(CommandHandler("pass", JustoneCommands.command_pass))	
	dp.add_handler(CommandHandler("clue", JustoneCommands.command_clue, pass_args = True))
	# Just One Callbacks de botones
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*choosedicc\*(.*)\*([0-9]*)", callback=JustOneController.callback_finish_config_justone))	
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*rechazar\*(.*)\*([0-9]*)", callback=JustOneController.callback_review_clues))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*finalizar\*(.*)\*([0-9]*)", callback=JustOneController.callback_review_clues_finalizado))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*reviewerconfirm\*(.*)\*([0-9]*)", callback=JustOneController.callback_reviewer_confirm))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*choosegameclue\*(.*)\*([0-9]*)", callback=JustoneCommands.callback_choose_game_clue))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*chooseend\*(.*)\*([0-9]*)", callback=JustOneController.callback_finish_game_buttons))
	
	# Handlers de D100
	dp.add_handler(CommandHandler("tirada", Commands.command_roll, pass_args = True))
		
	dp.add_handler(MessageHandler(Filters.command, unknown))
	
	# Handler cuando se una una persona al chat.
	dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, add_group))
	
	# Handler cuando se va una persona del chat.
	dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, remove_group))
	
	#dp.add_handler(MessageHandler(Filters.text, echo))
		
	# log all errors
	dp.add_error_handler(error)

	# Start the Bot (Usar si no es WebHook)
	updater.start_polling()

	# Run the bot until the you presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()



if __name__ == '__main__':
    main()
