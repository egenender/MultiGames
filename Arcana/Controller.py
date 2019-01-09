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

from Arcana.Constants.Config import DIFFICULTAD
from Arcana.Constants.Cards import FATETOKENS, LASHORAS, ARCANACARDS

from Arcana.Boardgamebox.Game import Game
from Arcana.Boardgamebox.Player import Player
from Arcana.Boardgamebox.Board import Board

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
		call_diff_buttons(bot, game)
	except Exception as e:
		bot.send_message(game.cid, 'No se ejecuto el comando debido a: '+str(e))

def call_diff_buttons(bot, game):
	#log.info('call_dicc_buttons called')
	opciones_botones = DIFFICULTAD
	Commands.simple_choose_buttons(bot, game.cid, 1234, game.cid, "choosediccAR", "Elija difficultad para jugar", opciones_botones)
		
def callback_finish_config(bot, update):
	log.info('callback_finish_config_sayanything called')
	callback = update.callback_query
	try:
		regex = re.search("(-[0-9]*)\*choosediccAR\*(.*)\*([0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
		mensaje_edit = "Por la difficultad el doom comienza en: {0}".format(opcion)
		
		#update.callback_query.answer(text="Si ningún destino visible es exactamente 1 más o 1 menos que cualquiera de tus destinos, jugá uno de ellos aquí.", show_alert=False)
		
		try:
			bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
		except Exception as e:
			bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)			
		game = Commands.get_game(cid)
		game.configs['difficultad'] = opcion
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
	# Seteo la difficultad
	game.board.state.doom = int(opcion)
	# Antes de comenzar la ronda saco 4 cartas de arca, en proximas rondas la cantidad se ajustara en la fase de Fade	
	for i in range(4):
		game.board.state.arcanasOnTable.append(game.board.arcanaCards.pop())
	# Siempre se ve la proxima carta de arcana		
	game.board.state.topArcana = game.board.arcanaCards[0]
	start_round(bot, game)

# Objetivo
# start_round / Draw Fates -> Play Fate -> Predict or Pass ->   Resolve  -> Fade
#  ---------------"Jugar Fate"---------     --Predecir ---     ----Resolver------
	
def start_round(bot, game):
	log.info('start_round_Arcana called')
	cid = game.cid	
	# Se marca al jugador activo
		
	active_player = game.player_sequence[game.board.state.player_counter]	
	game.board.state.active_player = active_player
	
	# El jugador obtiene hasta 2 fates
	for i in range(2-len(game.board.state.active_player.fateTokens)):
		game.board.state.active_player.fateTokens.append(game.board.draw_fate_token())
	
	show_fates_active_player(bot, game)	
	#send_buttons_active_player(bot, game)
	#bot.send_message(cid, game.board.print_board(game), ParseMode.MARKDOWN)
	game.board.print_board(bot, game)
	#print_board(bot, game)
	game.board.state.fase_actual = "Jugar Fate"
	Commands.save(bot, game.cid)
	
def show_fates_active_player(bot, game):
	cid = game.cid
	active_player = game.board.state.active_player
	mensaje = "*Los tokens que tiene en tu mano son (Has click sobre uno de ellos para agregarlo a una Arcana):*"
	btns = []
	index = 0
	for fate in active_player.fateTokens:
		btns.append([create_fate_button(fate, cid, active_player.uid, index)])
		index += 1
	btnMarkup = InlineKeyboardMarkup(btns)
	bot.send_message(active_player.uid, mensaje, parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup)

def callback_choose_fate(bot, update, user_data):
	callback = update.callback_query
	try:		
		#log.info('callback_finish_game_buttons called: %s' % callback.data)	
		regex = re.search("(-[0-9]*)\*chooseFateAR\*(.*)\*(-?[0-9]*)", callback.data)
		cid, strcid, opcion, index = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3))
		#bot.send_message(ADMIN[0], struid)
		game = Commands.get_game(cid)		
		active_player = game.board.state.active_player
		fate = active_player.fateTokens[index]
		user_data['fate'] = fate
		texto = fate["Texto"]
		horas = fate["TimeSymbols"]
		
		user_id2 = callback.from_user.id
		user_id = update.effective_user.id
		bot.send_message(ADMIN[0], "{} {}".format(user_id2, user_id))
		
		update.callback_query.answer(text="{} ({})".format(texto, horas), show_alert=False)
		bot.edit_message_text("Has elegido el destino {}\n".format(texto), uid, callback.message.message_id)
		#"Elige en que Arcana quieres ponerlo."
		btns = []
		i = 0
		for arcana_on_table in game.board.state.arcanasOnTable:
			btns.append([game.board.create_arcana_button(game.cid, arcana_on_table, i, comando_callback = "chooseArcanaAR")])
			i += 1
		btnMarkup = InlineKeyboardMarkup(btns)
		bot.send_message(game.cid, "*Elige en que Arcana quieres ponerlo.*:", parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup)
		
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando de callback_choose_fate debido a: '+str(e))
		bot.send_message(ADMIN[0], callback.data)

def callback_choose_arcana(bot, update, user_data):
	callback = update.callback_query
	
	try:		
		#log.info('callback_finish_game_buttons called: %s' % callback.data)	
		regex = re.search("(-[0-9]*)\*chooseArcanaAR\*(.*)\*(-?[0-9]*)", callback.data)
		cid, strcid, opcion, index = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3))
		#bot.send_message(ADMIN[0], struid)
		
		user_id2 = callback.from_user.id
		user_id = update.effective_user.id
		bot.send_message(ADMIN[0], "{} {}".format(user_id2, user_id))
		
		arcana = game.board.state.arcanasOnTable[index]
		texto = arcana["Texto"]
		titulo = arcana["Título"]
		
		choosen_fate = user_data['fate']
		
		if 'tokens' in arcana:
			tokens = arcana['tokens']
		else:
			arcana['tokens'] = []
		tokens.append(choosen_fate)	
		
		#bot.edit_message_text("Has elegido el destino {}\n".format(texto), uid, callback.message.message_id)
		#update.callback_query.answer(text="{}: {}".format(titulo, texto), show_alert=True)
		
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando de callback_choose_arcana debido a: '+str(e))
		bot.send_message(ADMIN[0], callback.data)
	
def create_fate_button(fate, cid, uid, index, comando_callback = "chooseFateAR"):
	texto = fate["Texto"]
	horas = fate["TimeSymbols"]
	txtBoton = "{} (Horas: {})".format(texto, horas)
	comando_callback = comando_callback
	uid = cid # Solo se va a usar para mostrar en pantallas de juego
	datos = str(cid) + "*" + comando_callback + "*" + str(texto) + "*" + str(index)
	return InlineKeyboardButton(txtBoton, callback_data=datos)
	
def call_players_to_clue(bot, game):
	for uid in game.playerlist:
		if uid != game.board.state.active_player.uid:
			#bot.send_message(cid, "Enviando mensaje a: %s" % game.playerlist[uid].name)
			mensaje = "Nueva frase en el grupo *{1}*.\nEl jugado activo es: *{2}*\nLa frase es: *{0}*, propone tu respuesta!".format(game.board.state.acciones_carta_actual, game.groupName, game.board.state.active_player.name)
			bot.send_message(uid, mensaje, ParseMode.MARKDOWN)
			mensaje = "/resp Ejemplo" if game.board.num_players != 3 else "/resp Ejemplo Ejemplo2"
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
	mensaje_final = "[{0}](tg://user?id={1}) es hora de elegir! Elige con /pick NUMERO\n*{3}*\nLas respuestas son:\n{2}\n*NO SE PUEDE HABLAR*".format(game.board.state.active_player.name, game.board.state.active_player.uid, text, game.board.state.acciones_carta_actual)	
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
		mensaje = "Juego finalizado!:\n*{0}*".format(game.board.print_puntaje(game))		
		game.board.state.fase_actual = "Finalizado"
		Commands.save(bot, game.cid)
		bot.send_message(game.cid, mensaje, ParseMode.MARKDOWN)
		continue_playing(bot, game)
		#bot.send_message(game.cid, "Para comenzar un juego nuevo pon el comando /delete y luego /newgame", ParseMode.MARKDOWN)
		return
	helper.increment_player_counter(game)
	start_round(bot, game)

def continue_playing(bot, game):
	opciones_botones = { "Nuevo" : "(Beta) Nuevo Partido", "Misma Dificultad" : "Misma Dificultad", "Diferente Dificultad" : "Diferente Dificultad"}
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
					
		if opcion == "Misma Dificultad":
			#(Beta) Nuevo Partido, mismos jugadores, mismo diccionario
			#log.info('Llego hasta el new2')
			game.configs['difficultad'] = dicc
			finish_config(bot, game, dicc)
		if opcion == "Diferente Dificultad":
			#(Beta) Nuevo Partido, mismos jugadores, diferente diccionario
			call_diff_buttons(bot, game)				
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando debido a: '+str(e))
		bot.send_message(ADMIN[0], callback.data)

def create_arcana_button(cid, arcana, tokens = []):
	titulo = arcana["Título"]	
	texto = arcana["Texto"]
	lunas = arcana["Lunas"]
	txtBoton = "{}".format(titulo)
	comando_callback = "txtArcanaAR"
	uid = cid # Solo se va a usar para mostrar en pantallas de juego
	datos = str(cid) + "*" + comando_callback + "*" + str(titulo) + "*" + str(uid)
	return InlineKeyboardButton(txtBoton, callback_data=datos)
		
def print_board(bot, game):
	bot.send_message(game.cid, "--- *Estado de Partida* ---\n")
	btns = []
	btns.append([create_arcana_button(game.cid, game.board.state.topArcana)])
	btnMarkup = InlineKeyboardMarkup(btns)
	bot.send_message(game.cid, "*Arcana de arriba del mazo:*", parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup)
	board = "*Arcanas Activas*:\n"
	btns = []
	for arcana_on_table in game.board.state.arcanasOnTable:
		btns.append([create_arcana_button(game.cid, arcana_on_table)])
	btnMarkup = InlineKeyboardMarkup(btns)
	bot.send_message(game.cid, "*Arcanas Activas*:", parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup)
	
def callback_txt_arcana(bot, update):
	callback = update.callback_query
	try:		
		#log.info('callback_finish_game_buttons called: %s' % callback.data)	
		regex = re.search("(-[0-9]*)\*txtArcanaAR\*(.*)\*(-?[0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
		#bot.send_message(ADMIN[0], struid)
		arcana = next(item for item in ARCANACARDS if item["Título"] == opcion)
		texto = arcana["Texto"]
		titulo = arcana["Título"]
		update.callback_query.answer(text="{}: {}".format(titulo, texto), show_alert=True)
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando de callback_txt_arcana debido a: '+str(e))
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
