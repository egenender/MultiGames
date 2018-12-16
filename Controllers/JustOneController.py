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

def init_game(bot, game):
	try:
		log.info('init_just_one called')
		cid = game.cid
		log.info('Game init_lost_expedition called')
		game.shuffle_player_sequence()
		# Seteo las palabras
		opciones_botones = {
			"original" : "Español Original",
			"ficus" : "Español Ficus"
		}
		Commands.simple_choose_buttons(bot, cid, 1234, cid, "choosedicc", "¿Elija un diccionario para jugar?", opciones_botones)
		
	except Exception as e:
		bot.send_message(game.cid, 'No se ejecuto el comando debido a: '+str(e))
		
def callback_finish_config_justone(bot, update):
	log.info('callback_finish_config_justone called')
	callback = update.callback_query
	try:
		
		log.info('review_clues_callback called: %s' % callback.data)	
		regex = re.search("(-[0-9]*)\*choosedicc\*(.*)\*([0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
		mensaje_edit = "Has elegido el diccionario: {0}".format(opcion)
		try:
			bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
		except Exception as e:
			bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)		

		game = Commands.get_game(cid)	
		url_palabras_posibles = '/app/txt/JustOne/spanish-{0}.txt'.format(opcion)	
		with open(url_palabras_posibles, 'r') as f:
			palabras_posibles = f.readlines()
			random.shuffle(palabras_posibles)		
			game.board.cartas = palabras_posibles[0:13]
			game.board.cartas = [w.replace('\n', '') for w in game.board.cartas]
		game.board.state.progreso = 0
		start_round_just_one(bot, game)
		
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando debido a: '+str(e))
		bot.send_message(ADMIN[0], callback.data)
		
def start_round_just_one(bot, game):
	log.info('start_round_just_one called')
	cid = game.cid	
	# Se marca al jugador activo
	
	#Reseteo los votos	
	game.board.state.last_votes = {}
	game.board.state.removed_votes = {}
	
	active_player = game.player_sequence[game.board.state.player_counter]
	reviewer_player = game.player_sequence[helper.next_player_after_active_player(game)]
	game.board.state.active_player = active_player
	game.board.state.reviewer_player = reviewer_player
	# Le muestro a los jugadores la palabra elegida para el jugador actual
	
	palabra_elegida = game.board.cartas.pop(0)
	game.board.state.acciones_carta_actual = palabra_elegida	
	
	bot.send_message(cid, game.board.print_board(game), ParseMode.MARKDOWN)
	bot.send_message(game.cid, "El jugador *%s* tiene que adivinar" % active_player.name, ParseMode.MARKDOWN)
	bot.send_message(game.cid, "El jugador *%s* revisara las pistas" % reviewer_player.name, ParseMode.MARKDOWN)
	game.dateinitvote = datetime.datetime.now()
	for uid in game.playerlist:
		if uid != game.board.state.active_player.uid:
			#bot.send_message(cid, "Enviando mensaje a: %s" % game.playerlist[uid].name)
			mensaje = "Nueva palabra en el grupo *{1}*.\nAdivina el jugador: *{2}*\nLa palabra es: *{0}*, propone tu pista!".format(palabra_elegida, game.groupName, game.board.state.active_player.name)
			bot.send_message(uid, mensaje, ParseMode.MARKDOWN)
			if game.board.num_players != 3:
				mensaje = "/clue Ejemplo"
			else:
				mensaje = "/clue Ejemplo Ejemplo2"
			bot.send_message(uid, mensaje)
			
	game.dateinitvote = datetime.datetime.now()
	game.board.state.fase_actual = "Proponiendo Pistas"
	Commands.save(bot, game.cid)
	
def review_clues(bot, game):
	log.info('review_clues called')
	game.dateinitvote = None
	game.board.state.fase_actual = "Revisando Pistas"
	reviewer_player = game.board.state.reviewer_player
	bot.send_message(game.cid, "El revisor {0} esta viendo las pistas".format(reviewer_player.name), ParseMode.MARKDOWN)
	# Antes de enviar las pistas elimino las que son iguales no importa el case
	votes_before_method = len(game.board.state.last_votes)
	# En removed_votes guardo las cartas eliminadas		
	game.board.state.last_votes, game.board.state.removed_votes = helper.remove_same_elements_dict(game.board.state.last_votes)		
	votes_after_method = len(game.board.state.last_votes)	
	if votes_before_method > votes_after_method:
		bot.send_message(game.cid, "Se han eliminado automaticamente *{0}* votos".format(votes_before_method-votes_after_method), ParseMode.MARKDOWN)
	send_reviewer_buttons(bot, game)
	Commands.save(bot, game.cid)

# Remueve repetidos y devuelve ambas listas
def remove_same_elements_dict(last_votes):
	last_votes_to_lower = {key:val.lower() for key, val in last_votes.items()}	
	repeated_keys = []
	valores_last_votes_to_lower = list(last_votes_to_lower.values())#last_votes_to_lower.values()
	for key, value in last_votes_to_lower.items():
		if valores_last_votes_to_lower.count(value) > 1:
			repeated_keys.append(key)	
	return {key:val for key, val in last_votes.items() if key not in repeated_keys}, {key:val for key, val in last_votes.items() if key in repeated_keys}


def send_reviewer_buttons(bot, game):
	log.info('send_reviewer_buttons called')
	reviewer_player = game.board.state.reviewer_player
	# Armo los botones para que el reviewer los analice.
	btns = []
	# Creo los botones para elegir al usuario
	cid = game.cid
	uid = reviewer_player.uid
	comando_callback = 'rechazar'
	mensaje_pregunta = "Partida {0}. Pista {2}.\nElija las palabras para anularlas o Finalizar para enviar las pistas restantes al jugador activo\n{1}".format(game.groupName, get_pistas_eliminadas(game), game.board.state.acciones_carta_actual)
	
	# Se ponen todos los botones de pistas que no fueron eliminadas al momento.
	for key, value in game.board.state.last_votes.items():
		txtBoton = value
		datos = str(cid) + "*" + comando_callback + "*" + str(value) + "*" + str(uid)
		btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])		
	comando_callback = 'finalizar'
	datos = str(cid) + "*" + comando_callback + "*" + str("finalizar") + "*" + str(uid)
	btns.append([InlineKeyboardButton('Finalizar', callback_data=datos)])	
	btnMarkup = InlineKeyboardMarkup(btns)	
	bot.send_message(uid, mensaje_pregunta, reply_markup=btnMarkup)	
	Commands.save(bot, game.cid)
	
def callback_review_clues(bot, update):
	try:
		callback = update.callback_query
		log.info('review_clues_callback called: %s' % callback.data)	
		regex = re.search("(-[0-9]*)\*rechazar\*(.*)\*([0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
		mensaje_edit = "Has eliminado la pista: %s" % opcion
		try:
			bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
		except Exception as e:
			bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)		
		
		game = Commands.get_game(cid)	
		reviewer_player = game.board.state.reviewer_player
		# Remuevo las pistas que son iguales a la elegida
		
		try:
			game.board.state.removed_votes.update({key:val for key, val in game.board.state.last_votes.items() if val == opcion})					
		except Exception as e:
			bot.send_message(ADMIN[0], 'Fallo al usar removed_votes: '+str(e))
			game.board.state.amount_shuffled.update({key:val for key, val in game.board.state.last_votes.items() if val == opcion})
				
		game.board.state.last_votes = {key:val for key, val in game.board.state.last_votes.items() if val != opcion}	
		
		bot.send_message(game.cid, "El revisor %s ha descartado una pista" % reviewer_player.name)
		Commands.save(bot, game.cid)
		
		# Si todavia hay pistas...
		if game.board.state.last_votes:
			send_reviewer_buttons(bot, game)
		else:
			bot.send_message(game.cid, "Todas las pistas han sido descartadas. Se pasa al siguiente jugador")
			bot.send_message(game.cid, "La palabra era: *{0}*.\n".format(game.board.state.acciones_carta_actual), ParseMode.MARKDOWN)			
			start_next_round(bot, game)
	except Exception as e:
		bot.send_message(game.cid, 'No se ejecuto el comando debido a: '+str(e))
	
def callback_review_clues_finalizado(bot, update):
	try:
		callback = update.callback_query
		log.info('review_clues_finalizado_callback called: %s' % callback.data)	
		regex = re.search("(-[0-9]*)\*finalizar\*(.*)\*([0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)	
		game = Commands.get_game(cid)		
		mensaje_edit = "Has finalizado la revision"
		try:
			bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
		except Exception as e:
			bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)
			
		reviewer_player = game.board.state.reviewer_player
		bot.send_message(game.cid, "El revisor %s ha terminado de revisar las pistas" % reviewer_player.name)
		send_clues(bot, game)
		Commands.save(bot, game.cid)
	except Exception as e:
		bot.send_message(game.cid, 'No se ejecuto el comando debido a: '+str(e))

def callback_reviewer_confirm(bot, update):
	try:
		callback = update.callback_query
		log.info('review_clues_finalizado_callback called: %s' % callback.data)	
		regex = re.search("(-[0-9]*)\*reviewerconfirm\*(.*)\*([0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)	
		game = Commands.get_game(cid)
		#send_clues(bot, game)
		mensaje_edit = "Gracias!"
		try:
			bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
		except Exception as e:
			bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)
			
		reviewer_player = game.board.state.reviewer_player
		bot.send_message(game.cid, "El revisor {0} ha determinado que es {1}".format(reviewer_player.name, opcion))
		
		if opcion == "correcto":
			game.board.state.progreso += 1
			game.board.discards.append(game.board.state.acciones_carta_actual)
		else:
			# Se elimina la proxima carta del mazo.
			bot.send_message(game.cid, "La palabra era: *{0}*.".format(game.board.state.acciones_carta_actual), ParseMode.MARKDOWN)			
			game.board.discards.append(game.board.state.acciones_carta_actual)
			# Solo descarto si hay cartas
			if len(game.board.cartas) != 0:
				bot.send_message(game.cid, "Se ha *eliminado del mazo 1 carta* como penalización", ParseMode.MARKDOWN)			
				game.board.discards.append(game.board.cartas.pop(0))
			else:
				# Si se falla en la ultima carta la penalizacion es perder 1 punto
				bot.send_message(game.cid, "Se ha *perdido 1 punto* como penalización", ParseMode.MARKDOWN)
				game.board.state.progreso -= 1
		Commands.save(bot, game.cid)
		start_next_round(bot, game)
	except Exception as e:
		bot.send_message(game.cid, 'No se ejecuto el comando debido a: '+str(e))

def send_clues(bot, game):
	text = ""
	for key, value in game.board.state.last_votes.items():		
		try:
			player = game.playerlist[key]
		except Exception as e:
			player = game.playerlist[key-1]
		text += "*{1}: {0}*\n".format(value, player.name)
	mensaje_final = "[{0}](tg://user?id={1}) es hora de adivinar! Pone /guess Palabra o /pass si no se sabes la palabra\nLas pistas son: \n{2}\n*NO SE PUEDE HABLAR*".format(game.board.state.active_player.name, game.board.state.active_player.uid, text)
	
	game.board.state.fase_actual = "Adivinando"
	Commands.save(bot, game.cid)
	
	bot.send_message(game.cid, mensaje_final, ParseMode.MARKDOWN)

def pass_just_one(bot, game):
	start_next_round(bot, game)	

def get_pistas_eliminadas(game):
	text_eliminadas = ""
	try:
		if game.board.state.removed_votes:
			text_eliminadas += "*Pistas eliminadas*\n"
			for key, value in game.board.state.removed_votes.items():
				try:
					player = game.playerlist[key]
				except Exception as e:
					player = game.playerlist[key-1]
				
				text_eliminadas += "*{1}: {0}*\n".format(value, player.name)
	except Exception as e:
		if game.board.state.amount_shuffled:
			text_eliminadas += "*Pistas eliminadas*\n"
			for key, value in game.board.state.amount_shuffled.items():
				try:
					player = game.playerlist[key]
				except Exception as e:
					player = game.playerlist[key-1] 
				text_eliminadas += "*{1}: {0}*\n".format(value, player.name)
	return text_eliminadas	



def start_next_round(bot, game):
	bot.send_message(ADMIN[0], game.board.state.removed_votes)
	if game.board.state.removed_votes:
		text_eliminadas = get_pistas_eliminadas(game)
		bot.send_message(game.cid, text_eliminadas, ParseMode.MARKDOWN)
	if not game.board.cartas:
		# Si no quedan cartas se termina el juego y se muestra el puntaje.
		mensaje = "Juego finalizado! El puntaje fue de: *{0}*".format(game.board.state.progreso)		
		game.board.state.fase_actual = "Finalizado"
		Commands.save(bot, game.cid)
		bot.send_message(cid, mensaje, ParseMode.MARKDOWN)
		return
	increment_player_counter(game)
	start_round_just_one(bot, game)


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
	
