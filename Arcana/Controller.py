#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Eduardo Peluffo"

import json
import logging as log
import re
from random import randrange, choice, shuffle
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
	game.board.state.arcanasOnTable.append(LASHORAS)
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
	
	# El jugador obtiene hasta 2 
	draw_tokens = 2-len(game.board.state.active_player.fateTokens)
	
	for i in range(draw_tokens):
		game.board.state.active_player.fateTokens.append(game.board.draw_fate_token())
	bot.send_message(cid, "El jugador activo ha robado {} tokens de destino".format(draw_tokens), parse_mode=ParseMode.MARKDOWN)

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
	mensaje = "Partida: {}\n*Los tokens que tiene en tu mano son (Has click sobre uno de ellos para agregarlo a una Arcana):*".format(game.groupName)
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
		
		uid = update.effective_user.id
		
		game = Commands.get_game(cid)
		
		if game.board.state.fase_actual != "Jugar Fate" or uid != game.board.state.active_player.uid:
			bot.send_message(cid, "No es el momento de jugar destino o no eres el que tiene que jugar el fate", ParseMode.MARKDOWN)
				
		active_player = game.board.state.active_player
		fate = active_player.fateTokens[index]
		user_data['fate'] = fate
		user_data['unchosen'] = active_player.fateTokens[1 if index == 0 else 0]
		
		texto = fate["Texto"]
		horas = fate["TimeSymbols"]			
		
		#update.callback_query.answer(text="{} ({})".format(texto, horas), show_alert=False)
		
		bot.edit_message_text("Has elegido el destino *{}*".format(texto), uid, callback.message.message_id, parse_mode=ParseMode.MARKDOWN)
		
		#"Elige en que Arcana quieres ponerlo."
		btns = []
		i = 0
		for arcana_on_table in game.board.state.arcanasOnTable:
			btns.append([game.board.create_arcana_button(game.cid, arcana_on_table, i, comando_callback = "chooseArcanaAR")])
			i += 1
		# Agrego boton cancelar
		datos = str(cid) + "*chooseArcanaAR*Cancelar*" + str(-1)
		btns.append([InlineKeyboardButton("Cancelar", callback_data=datos)])
		btnMarkup = InlineKeyboardMarkup(btns)
		bot.send_message(uid, "Partida {}\n*Elige en que Arcana quieres ponerlo.*:".format(game.groupName), parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup)
		
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
		
		uid = update.effective_user.id
		game = Commands.get_game(cid)
		
		if game.board.state.fase_actual != "Jugar Fate" or uid != game.board.state.active_player.uid:
			bot.send_message(cid, "No es el momento de jugar destino o no eres el que tiene que jugar el fate", ParseMode.MARKDOWN)
		
		if index == -1:
			bot.edit_message_text("Accion cancelada se vuelven a enviar destinos\n", uid, callback.message.message_id)
			show_fates_active_player(bot, game)
			return
		
		arcana = game.board.state.arcanasOnTable[index]
		texto = arcana["Texto"]
		titulo = arcana["Título"]
		chosen_fate = user_data['fate']
		unchosen_fate = user_data['unchosen']
		try:
			arcada_db = next((item for item in ARCANACARDS if item["Título"] == titulo), -1)
			if 'tokens' not in arcana:
				arcana['tokens'] = []
			arcada_db["tokens"] = arcana["tokens"]
			
			is_legal_arcana = arcada_db["Legal"](int(unchosen_fate["Texto"]), int(chosen_fate["Texto"]))#FIX
			
			
		except Exception as e:
			is_legal_arcana = True

		if not is_legal_arcana:
			bot.edit_message_text("No puedes jugar ese destino en esa arcana, se vuelven a enviar destinos\n", uid, callback.message.message_id)
			show_fates_active_player(bot, game)
			return

		if 'tokens' not in arcana:
			arcana['tokens'] = []		
		
		update.callback_query.answer(text="Se puso en la arcana {} el destino {}".format(arcana["Título"], chosen_fate["Texto"]), show_alert=False)
		
		bot.edit_message_text("Has elegido la Arcana *{}: {}*\n".format(titulo, texto), uid, callback.message.message_id, parse_mode=ParseMode.MARKDOWN)
		
		#bot.edit_message_text("Has elegido el destino {}\n".format(texto), uid, callback.message.message_id)
		#update.callback_query.answer(text="{}: {}".format(titulo, texto), show_alert=True)		
		
		
		
		mensaje_final = ""
		
		mensaje_final += "El jugador *{}* ha puesto el destino *{}* en la Arcana *{}*.".format(
			game.board.state.active_player.name, chosen_fate["Texto"], arcana["Título"])
					
		# Si es las horas el token va a la siguiente carta
		if arcana["Título"] == "Las horas":
			arcana = game.board.state.arcanasOnTable[index+1]
			texto = arcana["Texto"]
			titulo = arcana["Título"]
			mensaje_final += "\nComo se ha jugado en Las Horas el token pasa a la siguiente arcana *{}*".format(arcana["Título"])			
		
		mensaje_final += "\nHagan /guess N para adivinar destino o /pass para pasar!"
		
		arcana['tokens'].append(chosen_fate)		
		game.board.state.active_player.fateTokens.remove(chosen_fate)
		game.board.state.fase_actual = "Predecir"
		Commands.save(bot, game.cid)
		
		game.board.print_board(bot, game)		
		bot.send_message(cid, mensaje_final, ParseMode.MARKDOWN)		
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
	
def resolve(bot, game, prediccion = "0"):	
	# Si los jugadores hicieron una prediccion (se pasa el argumento como string)
	good_prediction = False
	prediccion = int(prediccion)
	if prediccion > 0:
		fate_quedaba = game.board.state.active_player.fateTokens.pop()		
		if prediccion == int(fate_quedaba["Texto"]):
			# Si predicen bien el faden no aumenta el doom.
			game.board.state.score += 1
			good_prediction = True
			bot.send_message(game.cid, "*Correcto!* El destino que tenia el jugador era {}, se gana 1 punto!"
					 .format(fate_quedaba["Texto"]), ParseMode.MARKDOWN)
		else:			
			game.board.state.doom  += 1
			bot.send_message(game.cid, "*Incorrecto!* El destino que tenia el jugador era {}"
					 .format(fate_quedaba["Texto"]), ParseMode.MARKDOWN)	
		# TODO: reseteo los ayuda memoria del jugador activo
	
	# Fading phase
	arcanasOnTable = game.board.state.arcanasOnTable	
	for arcana_on_table in arcanasOnTable:
		#print(arcana_on_table)
		if 'tokens' not in arcana_on_table:
			arcana_on_table['tokens'] = []
		if game.board.count_fate_tokens(arcana_on_table) >= int(arcana_on_table["Lunas"]):
			fadding_arcana(arcanasOnTable, arcana_on_table, game, good_prediction)
			bot.send_message(game.cid, "La Arcana *{}* se ha desvanecido".format(arcana_on_table["Título"]), ParseMode.MARKDOWN)
	start_next_round(bot, game)			
	
def fadding_arcana(arcanasOnTable, arcana_on_table, game, good_prediction):
	indice = arcanasOnTable.index(arcana_on_table)
	# Regreso los tokens de destino a la bolsa
	game.board.fateTokens.extend(arcana_on_table['tokens'])
	# La doy vuelta y la pongo en la "faded area"
	arcana_on_table["faded"] = True
	arcana_on_table['tokens'] = []
	game.board.state.fadedarcanasOnTable.append(arcana_on_table)
	# Si no hubo buena prediccion avanzo doom 2, a menos que la arcana sea Libre.
	if not good_prediction and arcana_on_table["Título"] != "Libre":
		game.board.state.doom  += 2
	# Reemplazo arcana
	arcanasOnTable[indice] = game.board.arcanaCards.pop()	
		
def start_next_round(bot, game):
	log.info('Verifing End_Game called')
	if game.board.state.score > 6 or game.board.state.doom > 6:
		# Si no quedan cartas se termina el juego y se muestra el puntaje.
		mensaje = "Juego finalizado!:\n*{0}*".format(game.board.print_result(game))		
		game.board.state.fase_actual = "Finalizado"
		Commands.save(bot, game.cid)
		bot.send_message(game.cid, mensaje, ParseMode.MARKDOWN)
		continue_playing(bot, game)
		return
	helper.increment_player_counter(game)
	start_round(bot, game)

def continue_playing(bot, game):
	opciones_botones = { "Nuevo" : "(Beta) Nuevo Partido", "Misma Dificultad" : "Misma Dificultad", "Diferente Dificultad" : "Diferente Dificultad"}
	Commands.simple_choose_buttons(bot, game.cid, 1, game.cid, "chooseendAR", "¿Quieres continuar jugando?", opciones_botones)
	
def callback_finish_game_buttons(bot, update):
	callback = update.callback_query
	try:		
		#log.info('callback_finish_game_buttons called: %s' % callback.data)	
		regex = re.search("(-[0-9]*)\*chooseendAR\*(.*)\*([0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
		mensaje_edit = "Has elegido: {0}".format(opcion)
		try:
			bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
		except Exception as e:
			bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)				
		game = Commands.get_game(cid)
		
		# Obtengo el diccionario actual, primero casos no tendre el config y pondre el community
		try:
			diff = game.configs.get('difficultad', 0)
		except Exception as e:
			diff = 0
		
		# Obtengo datos de juego anterior		
		groupName = game.groupName
		tipojuego = game.tipo
		modo = game.modo
		
		# Dependiendo de la opcion veo que como lo inicio
		players = game.playerlist.copy()
		# Creo nuevo juego
		game = Game(cid, uid, groupName, tipojuego, modo)
		GamesController.games[cid] = game
		
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
			game.configs['difficultad'] = diff
			finish_config(bot, game, diff)
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
	
def callback_txt_arcana(bot, update):
	callback = update.callback_query
	try:		
		log.info('callback_txt_arcana called: %s' % callback.data)
		regex = re.search("(-[0-9]*)\*txtArcanaAR\*(.*)\*(-?[0-9]*)", callback.data)
		cid, strcid, opcion, index = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3))
		#bot.send_message(ADMIN[0], struid)
		faded = False
		if opcion == "Las horas":
			arcana = LASHORAS
		else:
			arcana = next((item for item in ARCANACARDS if item["Título"] == opcion), -1)
			if arcana == -1 or index == -2:
				arcana = next(item for item in ARCANACARDS if item["Título reverso"] == opcion)
				faded = True
		#log.info((arcana, faded))
		if faded:
			texto = arcana["Texto reverso"]
			titulo = arcana["Título reverso"]
		else:
			texto = arcana["Texto"]
			titulo = arcana["Título"]
		update.callback_query.answer(text="{}: {}".format(titulo, texto), show_alert=True)
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando de callback_txt_arcana debido a: '+str(e))
		bot.send_message(ADMIN[0], callback.data)
		
		
