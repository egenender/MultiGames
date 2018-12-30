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
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler)

import Commands
from Constants.Cards import playerSets, actions
from Constants.Config import TOKEN, STATS, ADMIN

from SayAnything.Boardgamebox.Game import Game
from SayAnything.Boardgamebox.Player import Player
from SayAnything.Boardgamebox.Board import Board

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

def init_game(bot, game):
	try:
		log.info('init_say_anything called')		
		game.shuffle_player_sequence()		
		# Seteo las palabras	
		call_dicc_buttons(bot, game)
	except Exception as e:
		bot.send_message(game.cid, 'No se ejecuto el comando debido a: '+str(e))

def call_dicc_buttons(bot, game):
	#log.info('call_dicc_buttons called')
	opciones_botones = { "preguntas" : "Español Ficus" }
	Commands.simple_choose_buttons(bot, game.cid, 1234, game.cid, "choosediccSA", "¿Elija un diccionario para jugar?", opciones_botones)
		
def callback_finish_config(bot, update):
	log.info('callback_finish_config_sayanything called')
	callback = update.callback_query
	try:
		regex = re.search("(-[0-9]*)\*choosediccSA\*(.*)\*([0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
		mensaje_edit = "Has elegido el diccionario: {0}".format(opcion)
		try:
			bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
		except Exception as e:
			bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)
			
		game = Commands.get_game(cid)
		game.configs['diccionario'] = opcion
		finish_config(bot, game, opcion)
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando debido a: '+str(e))
		bot.send_message(ADMIN[0], callback.data)

# list_total lista con todos los elementos
# list_a_restar Elementos a restar a list_total
def list_menos_list(list_total, list_a_restar):
	return [x for x in list_total if x not in list_a_restar]
		
def finish_config(bot, game, opcion):
	log.info('finish_config called')
	# Si vengo de un partido anterior agrego los descartes de la partida anterior.	
	if game.configs.get('discards', None):
		game.board.discards = game.configs.get('discards')
		del game.configs['discards']
	url_palabras_posibles = '/app/SayAnything/txt/spanish-{0}.txt'.format(opcion)	
	with open(url_palabras_posibles, 'r') as f:
		palabras_posibles = f.readlines()
		palabras_posibles_no_repetidas = list_menos_list(palabras_posibles, game.board.discards)
		# Si no hay palabra posible no repetidas para jugar mezclo todas las palabras posibles
		if len(palabras_posibles_no_repetidas) < 13:
		    # Quedo bien 
			game.board.discards = []
			palabras_posibles_no_repetidas = palabras_posibles
		
		random.shuffle(palabras_posibles_no_repetidas)		
		game.board.cartas = palabras_posibles_no_repetidas[0:13]
		game.board.cartas = [w.replace('\n', '') for w in game.board.cartas]
	game.board.state.progreso = 0
	start_round_say_anything(bot, game)
		
def start_round_say_anything(bot, game):
	log.info('start_round_say_anything called')
	cid = game.cid	
	# Se marca al jugador activo
	
	#Reseteo los votos	
	game.board.state.last_votes = {}
	game.board.state.removed_votes = {}
	
	active_player = game.player_sequence[game.board.state.player_counter]	
	game.board.state.active_player = active_player
	
	palabra_elegida = game.board.cartas.pop(0)
	game.board.state.acciones_carta_actual = palabra_elegida	
	
	Commands.save(bot, game.cid)
	bot.send_message(cid, game.board.print_board(game), ParseMode.MARKDOWN)
	game.dateinitvote = datetime.datetime.now()
	game.board.state.fase_actual = "Proponiendo Pistas"
	call_players_to_clue(bot, game)
	Commands.save(bot, game.cid)
	'''	
	game.dateinitvote = datetime.datetime.now()
	call_players_to_clue(bot, game)			
	game.dateinitvote = datetime.datetime.now()
	game.board.state.fase_actual = "Proponiendo Pistas"
	Commands.save(bot, game.cid)
	'''

def call_players_to_clue(bot, game):
	for uid in game.playerlist:
		if uid != game.board.state.active_player.uid:
			#bot.send_message(cid, "Enviando mensaje a: %s" % game.playerlist[uid].name)
			mensaje = "Nueva frase en el grupo *{1}*.\nEl jugado activo es: *{2}*\nLa frase es: *{0}*, propone tu respuesta!".format(game.board.state.acciones_carta_actual, game.groupName, game.board.state.active_player.name)
			bot.send_message(uid, mensaje, ParseMode.MARKDOWN)
			mensaje = "/prop Ejemplo" if game.board.num_players != 3 else "/prop Ejemplo Ejemplo2"
			bot.send_message(uid, mensaje)

def send_prop(bot, game):
	text = ""
	i = 1
	for key, value in game.board.state.last_votes.items():		
		try:
			player = game.playerlist[key]
		except Exception as e:
			player = game.playerlist[key-1]
		text += "*{1}: {0}*\n".format(value, i)
		i += 1
	mensaje_final = "[{0}](tg://user?id={1}) es hora de elegir! Elige con /pick NUMERO\nLas frases son: \n{2}\n*NO SE PUEDE HABLAR*".format(game.board.state.active_player.name, game.board.state.active_player.uid, text)	
	game.board.state.fase_actual = "Adivinando"
	Commands.save(bot, game.cid)
	
	bot.send_message(game.cid, mensaje_final, ParseMode.MARKDOWN)

def pass_say_anything(bot, game):
	bot.send_message(game.cid, "La frase era: *{0}*. El jugador activo no le gusto ninguna respuesta.".format(game.board.state.acciones_carta_actual), ParseMode.MARKDOWN)
	start_next_round(bot, game)

def start_next_round(bot, game):
	log.info('Verifing End_Game called')
	if not game.board.cartas:
		# Si no quedan cartas se termina el juego y se muestra el puntaje.
		mensaje = "Juego finalizado! El puntaje final es: *{0}*".format(game.board.print_puntaje(game))		
		game.board.state.fase_actual = "Finalizado"
		Commands.save(bot, game.cid)
		bot.send_message(game.cid, mensaje, ParseMode.MARKDOWN)
		continue_playing(bot, game)
		#bot.send_message(game.cid, "Para comenzar un juego nuevo pon el comando /delete y luego /newgame", ParseMode.MARKDOWN)
		return
	helper.increment_player_counter(game)
	start_round_say_anything(bot, game)

def continue_playing(bot, game):
	opciones_botones = { "Nuevo" : "(Beta) Nuevo Partido", "Mismo Diccionario" : "(Beta) Nuevo Partido, mismos jugadores, mismo diccionario", "Otro Diccionario" : "(Beta) Nuevo Partido, mismos jugadores, diferente diccionario"}
	Commands.simple_choose_buttons(bot, game.cid, 1, game.cid, "chooseend", "¿Quieres continuar jugando?", opciones_botones)
	
def callback_finish_game_buttons(bot, update):
	callback = update.callback_query
	try:		
		#log.info('callback_finish_game_buttons called: %s' % callback.data)	
		regex = re.search("(-[0-9]*)\*chooseend\*(.*)\*([0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
		mensaje_edit = "Has elegido el diccionario: {0}".format(opcion)
		try:
			bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
		except Exception as e:
			bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)				
		game = Commands.get_game(cid)
		
		# Obtengo el diccionario actual, primero casos no tendre el config y pondre el community
		try:
			dicc = game.configs.get('diccionario','community')
		except Exception as e:
			dicc = 'community'
		
		# Obtengo datos de juego anterior		
		groupName = game.groupName
		tipojuego = game.tipo
		modo = game.modo
		descarte = game.board.discards
		# Dependiendo de la opcion veo que como lo inicio
		players = game.playerlist.copy()
		# Creo nuevo juego
		game = Game(cid, uid, groupName, tipojuego, modo)
		GamesController.games[cid] = game
		# Guarda los descartes en configs para asi puedo recuperarlos
		game.configs['discards'] = descarte
		if opcion == "Nuevo":
			bot.send_message(cid, "Cada jugador puede unirse al juego con el comando /join.\nEl iniciador del juego (o el administrador) pueden unirse tambien y escribir /startgame cuando todos se hayan unido al juego!")			
			return
		#log.info('Llego hasta la creacion')		
		game.playerlist = players
		# StartGame
		player_number = len(game.playerlist)
		game.board = Board(player_number, game)		
		game.player_sequence = []
		game.shuffle_player_sequence()
					
		if opcion == "Mismo Diccionario":
			#(Beta) Nuevo Partido, mismos jugadores, mismo diccionario
			#log.info('Llego hasta el new2')
			game.configs['diccionario'] = dicc
			finish_config(bot, game, dicc)
		if opcion == "Otro Diccionario":
			#(Beta) Nuevo Partido, mismos jugadores, diferente diccionario
			call_dicc_buttons(bot, game)				
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando debido a: '+str(e))
		bot.send_message(ADMIN[0], callback.data)
	
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
