#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Eduardo Peluffo"

import copy
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
	
	start_round(bot, game)

# Objetivo
# start_round / Draw Fates -> Play Fate -> Predict or Pass ->   Resolve  -> Fade
#  ---------------"Jugar Fate"---------     --Predecir ---     ----Resolver------
	
def start_round(bot, game):
	log.info('start_round_Arcana called')
	cid = game.cid	
	# Se marca al jugador activo
	
	# Se resetean marcas del turno
	game.board.state.plusOneEnable = False
	game.board.state.used_sacar = False
	game.board.state.extraGuess = False
	
	active_player = game.player_sequence[game.board.state.player_counter]	
	game.board.state.active_player = active_player
	
	draw_fates_player(bot, game, game.board.state.active_player)
	
	show_fates_active_player(bot, game)	
	#send_buttons_active_player(bot, game)
	#bot.send_message(cid, game.board.print_board(game), ParseMode.MARKDOWN)
	game.board.print_board(bot, game)
	#print_board(bot, game)
	game.board.state.fase_actual = "Jugar Fate"
	Commands.save(bot, game.cid)

def draw_fates_player(bot, game, player):
	# El jugador obtiene hasta 2 
	draw_tokens = 2-len(player.fateTokens)	
	for i in range(draw_tokens):
		player.fateTokens.append(game.board.draw_fate_token())
	bot.send_message(game.cid, "El jugador {} ha robado {} tokens de destino".format(player.name, draw_tokens), parse_mode=ParseMode.MARKDOWN)	
	
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
	
			
	#log.info('callback_finish_game_buttons called: %s' % callback.data)	
	regex = re.search("(-[0-9]*)\*chooseArcanaAR\*(.*)\*(-?[0-9]*)", callback.data)
	cid, strcid, opcion, index = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3))
	#bot.send_message(ADMIN[0], struid)

	uid = update.effective_user.id
	game = Commands.get_game(cid)
	try:	
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

		# Caso particular de elegir +1
		if game.board.state.plusOneEnable:
			unchosen_fate = copy.deepcopy(user_data['unchosen'])
			unchosen_fate["Texto"] = "{}".format(int(unchosen_fate["Texto"])+1)
			
		is_legal_arcana = game.board.is_legal_arcana(arcana, chosen_fate, unchosen_fate)
		
		if game.board.state.used_sacar and texto == "Sacar":
			is_legal_arcana = False

		# Verifico que no haya posibles arcanas si se elija a "Las Horas"
		if titulo == "Las horas":
			log.info('get_valid_arcanas called')
			valid_arcanas_fates = game.board.get_valid_arcanas(chosen_fate, unchosen_fate)
			log.info('get_valid_arcanas finished')
			if len(valid_arcanas_fates) > 0:
				msg = "Puedes usar estas arcanas y combinaciones (Choose fate / unchoose fate)\n"
				for valid_arcana_fates in valid_arcanas_fates:
					msg += "Arcana: *{}*, Poner fate: *{}*.\n".format(
						valid_arcana_fates[0]["Título"], valid_arcana_fates[1]["Texto"])									
				bot.send_message(uid, msg, ParseMode.MARKDOWN)
				is_legal_arcana = False
				
		if not is_legal_arcana:
			bot.edit_message_text("No puedes jugar ese destino en esa arcana, se vuelven a enviar destinos\n", uid, callback.message.message_id)
			show_fates_active_player(bot, game)
			return

		if 'tokens' not in arcana:
			arcana['tokens'] = []		

		update.callback_query.answer(text="Se puso en la arcana {} el destino {}".format(arcana["Título"], chosen_fate["Texto"]), show_alert=False)

		bot.edit_message_text("Has elegido la Arcana *{}: {}*.\nTe queda en la mano el token *{}*\n".format(titulo, texto, user_data['unchosen']["Texto"]), uid, callback.message.message_id, parse_mode=ParseMode.MARKDOWN)

		mensaje_final = "El jugador *{}* ha puesto el destino *{}* en la Arcana *{}*.".format(
			game.board.state.active_player.name, chosen_fate["Texto"], arcana["Título"])

		# Caminos alternativo si elige una arcana especial. Y si detiende la ejecucion del metodo.
		if(aditional_actions_arcanas(bot, game, index, arcana, titulo, texto, uid, callback, mensaje_final, chosen_fate)):
			return

		if titulo == "Las horas":
			arcana = game.board.state.arcanasOnTable[index+1]
			texto = arcana["Texto"]
			mensaje_final += "\nComo se ha jugado en Las Horas el token pasa a la siguiente arcana *{}*".format(arcana["Título"])			

		call_other_players = ""
		for uid, player in game.playerlist.items():
			call_other_players += "{} ".format(helper.player_call(player)) if uid != game.board.state.active_player.uid else ""

		mensaje_final += "\n{}Hagan /guess N para adivinar destino o /pass para pasar!".format(call_other_players)	
		arcana['tokens'].append(chosen_fate)		
		game.board.state.active_player.fateTokens.remove(chosen_fate)
		game.board.state.fase_actual = "Predecir"
		Commands.save(bot, game.cid)

		game.board.print_board(bot, game)		
		bot.send_message(cid, mensaje_final, ParseMode.MARKDOWN)		
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando de callback_choose_arcana debido a: '+str(e))
		bot.send_message(ADMIN[0], callback.data)

# Acciones particulares de la Arcana Sacar.
def aditional_actions_arcanas(bot, game, index, arcana, titulo, texto, uid, callback, mensaje, chosen_fate):
	stop_flow = False
	if arcana["Título"] == "Sacar":	
		arcana['tokens'].append(chosen_fate)		
		game.board.state.active_player.fateTokens.remove(chosen_fate)
		bot.send_message(game.cid, mensaje, ParseMode.MARKDOWN)
		game.board.state.used_sacar = True
		draw_fates_player(bot, game, game.board.state.active_player)
		show_fates_active_player(bot, game)
		Commands.save(bot, game.cid)
		stop_flow = True
	if arcana["Título"] == "Adivinar":
		game.board.state.extraGuess = True
		
	return stop_flow
	
def create_fate_button(fate, cid, uid, index, comando_callback = "chooseFateAR"):
	texto = fate["Texto"]
	horas = fate["TimeSymbols"]
	txtBoton = "{} (Horas: {})".format(texto, horas)
	comando_callback = comando_callback
	uid = cid # Solo se va a usar para mostrar en pantallas de juego
	datos = str(cid) + "*" + comando_callback + "*" + str(texto) + "*" + str(index)
	return InlineKeyboardButton(txtBoton, callback_data=datos)
	
def resolve(bot, game, prediccion = []):	
	# Si los jugadores hicieron una prediccion (se pasa el argumento como string)
	good_prediction = False
	
	if len(prediccion) > 0:
		fate_quedaba = game.board.state.active_player.fateTokens.pop()		
		if int(fate_quedaba["Texto"]) in prediccion:
			# Si predicen bien el faden no aumenta el doom.
			game.board.state.score += 1
			good_prediction = True
			bot.send_message(game.cid, "*Correcto!* El destino que tenia el jugador era {}, se gana 1 punto!"
					 .format(fate_quedaba["Texto"]), ParseMode.MARKDOWN)
		else:			
			game.board.state.doom  += 1
			bot.send_message(game.cid, "*Incorrecto!* El destino que tenia el jugador era {}"
					 .format(fate_quedaba["Texto"]), ParseMode.MARKDOWN)	
		game.board.fateTokens.append(fate_quedaba)
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

# Si se usa la accion se descarta al final.
def use_fadded_action(bot, game, uid, elegido):
	arcana = game.board.state.fadedarcanasOnTable[elegido]
	if can_use_fadded(bot, game, uid, arcana):
		# 3 acciones que cambian cartas en arcanas Reubicar Ciclar Descartar menor
		titulo = arcana["Título reverso"]
		accion = {"+1" : plusOneAction, "Reubicar": reubicar_action, "Ciclar": ciclar_action, "Descartar menor": descartarmenor_action}.get(titulo)
		if accion:
			done = accion(bot, game, uid)
			if done:
				game.board.state.fadedarcanasOnTable.remove(arcana)
				bot.send_message(game.cid, "Se ha removido la arcana *{}* con habilidad *{}*".format(arcana["Título reverso"], arcana["Texto reverso"]), ParseMode.MARKDOWN)						
			else:
				bot.send_message(game.cid, "Funcionalidad de *{}* en *Construcción*".format(arcana["Título reverso"]), ParseMode.MARKDOWN)
		else:
			# Por el momento el resto se ejecutaran directamente.
			game.board.state.fadedarcanasOnTable.remove(arcana)
			bot.send_message(game.cid, "Se ha removido la arcana *{}* con habilidad *{}*".format(arcana["Título reverso"], arcana["Texto reverso"]), ParseMode.MARKDOWN)		
	else:
		bot.send_message(game.cid, "No se puede/No puedes usar este poder en este momento", ParseMode.MARKDOWN)

def plusOneAction(bot, game, uid):
	game.board.state.plusOneEnable = True
	return True
		
def reubicar_action(bot, game, uid):
	log.info('reubicar_action called')
	btnMarkup = create_arcanas_buttons(bot, game, action, uid, restrict = [])
	bot.send_message(uid, "Partida {}\n*Elige desde Arcana quieres ponerlo.*:".format(game.groupName), parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup)
	return False
	# Botones Publicos
	# El jugador mueve destino de una arcana a otra.
	# Mostrar arcanas (menos las horas) (Cancel jugador no decide más)
	# Mostrar destinos Arcana (Cancel muestra arcanas)
	# Mostrar arcanas posibles (Cancel muestra destinos de nuevo)
	# Verificar que la arcana no sea la misma

def ciclar_action(bot, game, uid):
	log.info('ciclar_action called')
	return False
	# Botones Publicos
	# El jugador mueve destino de una arcana a otra.
	# Mostrar arcanas (menos las horas)
	# Verificar que la arcanano tenga destinos 
	
# Accion a realizar, usuario que llama a la accion, restricciones de arcanas a mostrar
def create_arcanas_buttons(bot, game, action, uid, restrict = []):
	
	#(-?[0-9]*)\*([a-z]*)ArcanaAR\*(.*)\*(-?[0-9]*)
	#"Elige en que Arcana quieres ponerlo."
	btns = []
	i = 0
	for arcana_on_table in game.board.state.arcanasOnTable:
		if arcana_on_table["Texto"] not in restrict:
 			btns.append([game.board.create_arcana_button(
				game.cid, arcana_on_table, i, comando_callback = "{}ArcanaAR".format(action))])
		i += 1
	# Agrego boton cancelar
	datos = str(cid) + "*{}ArcanaAR*Cancelar*".format(action) + str(-1)
	btns.append([InlineKeyboardButton("Cancelar", callback_data=datos)])
	btnMarkup = InlineKeyboardMarkup(btns)
	
def descartarmenor_action(bot, game, uid):
	log.info('descartarmenor_action called')
	return False
	# Botones en privado
	# Mostrar arcanas (Cancel jugador no decide más)
	# Mostrar destinos Arcana (Cancel muestra arcanas)
	# Verificar que el destino a eliminar sea menor al destino restante	
	
# Acciones que se realizan al usar las fadded
def can_use_fadded(bot, game, uid, arcana):
	# Detecto el timing por el texto de la carta
	texto = arcana["Texto reverso"]
	titulo = arcana["Título reverso"]
	# Si es true es jugable antes de destino, sino prediccion
	destino = True if "de jugar" in texto else False
	# Si es true es antes, sino despues
	antes = True if "Antes de" in texto else False
	# Si es true la puede usar el jugador activo, sino el grupo
	jugador_activo = True if "el jugador activo" in texto else False	
	# Si es antes de poner destino el estado debe ser Jugar Fate, sino Predecir
	log.info('destino: {}, antes: {}, Req jugador_activo: {}, Es el jugador activo?: {}'.format(destino, antes, jugador_activo, (uid==game.board.state.active_player.uid)))
	
	# VErifico si es el jugador correcto el que ejecuta 
	if (jugador_activo and not (uid==game.board.state.active_player.uid)) or (
		(not jugador_activo) and (uid==game.board.state.active_player.uid)):
		return False
	
	# Verifico que sea en la fase correcta.
	if antes and destino and game.board.state.fase_actual == "Jugar Fate":
		return True
	elif ((not antes) or (not destino)) and game.board.state.fase_actual == "Predecir":
		return True
	return False		
