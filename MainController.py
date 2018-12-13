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

'''
Solitario: 
Dia: Obten 6 cartas. 2 mazo, 2 mano, 1 mazo, 1 mano.
Se ordenan por número.
Resuelve.
Pierde 1 comida.
Noche: Primera de la mano. Poner de mazo o mano hasta completar 6.
Se puede poner adelante o atras en la ruta.
Resuelve.
Pierde 1 comida. Ir a día.
'''

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
		init_just_one(bot, game, player_number)


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
		
def init_just_one(bot, game, player_number):
	try:
		cid = game.cid
		log.info('Game init_lost_expedition called')
		game.shuffle_player_sequence()
		# Seteo las palabras
		opciones_botones = {
			"spanish-original.txt" : "Español Original",
			"spanish-ficus.txt" : "Español Ficus"
		}
		Commands.simple_choose_buttons(bot, cid, cid, cid, "choosedicc", "¿Elija un diccionario para jugar?", opciones_botones)
		'''
		url_palabras_posibles = '/app/txt/JustOne/spanish-original.txt'	
		with open(url_palabras_posibles, 'r') as f:
			palabras_posibles = f.readlines()
			random.shuffle(palabras_posibles)		
			game.board.cartas = palabras_posibles[0:12]
			game.board.cartas = [w.replace('\n', '') for w in game.board.cartas]
		start_round_just_one(bot, game)
		'''
	except Exception as e:
		bot.send_message(game.cid, 'No se ejecuto el comando debido a: '+str(e))

def callback_finish_config_justone(bot, update):
	try:
		callback = update.callback_query
		log.info('review_clues_callback called: %s' % callback.data)	
		regex = re.search("(-[0-9]*)\*choosedicc\*(.*)\*([0-9]*)", callback.data)
		cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
		mensaje_edit = "Has elegido el diccionario: {0}".format(opcion)
		try:
			bot.edit_message_text(mensaje_edit, cid, callback.message.message_id)
		except Exception as e:
			bot.edit_message_text(mensaje_edit, uid, callback.message.message_id)		

		game = Commands.get_game(cid)	
		url_palabras_posibles = '/app/txt/JustOne/{0}'.format(opcion)	
		with open(url_palabras_posibles, 'r') as f:
			palabras_posibles = f.readlines()
			random.shuffle(palabras_posibles)		
			game.board.cartas = palabras_posibles[0:12]
			game.board.cartas = [w.replace('\n', '') for w in game.board.cartas]
		start_round_just_one(bot, game)
		
	except Exception as e:
		bot.send_message(ADMIN[0], 'No se ejecuto el comando debido a: '+str(e))
	
	
def next_player_after_active_player(game):
	#log.info('next_player_after_active_player called')
	if game.board.state.player_counter < len(game.player_sequence) - 1:
		return game.board.state.player_counter +1
	else:
		return 0
		
def start_round_just_one(bot, game):        
	cid = game.cid	
	log.info('start_round called')
	# Se marca al jugador activo
	
	if not game.board.cartas:
		# Si no quedan cartas se termina el juego y se muestra el puntaje.
		mensaje = "Juego finalizado! El puntaje fue de: *{0}*".format(game.board.state.progreso-1)		
		game.board.state.fase_actual = "Finalizado"
		Commands.save(bot, game.cid)
		bot.send_message(cid, mensaje, ParseMode.MARKDOWN)
		return
	
	#Reseteo los votos	
	game.board.state.last_votes = {}
	game.board.state.amount_shuffled = {}
	
	active_player = game.player_sequence[game.board.state.player_counter]
	reviewer_player = game.player_sequence[next_player_after_active_player(game)]
	game.board.state.active_player = active_player
	game.board.state.reviewer_player = reviewer_player
	# Le muestro a los jugadores la palabra elegida para el jugador actual
	
	palabra_elegida = game.board.cartas.pop(0)
	game.board.state.acciones_carta_actual = palabra_elegida
	bot.send_message(game.cid, "El jugador %s tiene que adivinar" % active_player.name)
	bot.send_message(game.cid, "El jugador %s revisara las pistas" % reviewer_player.name)
	game.dateinitvote = datetime.datetime.now()
	for uid in game.playerlist:
		if uid != game.board.state.active_player.uid:
			#bot.send_message(cid, "Enviando mensaje a: %s" % game.playerlist[uid].name)
			mensaje = "Nueva palabra en el grupo *{1}*.\nLa palabra es: *{0}*, propone tu pista!".format(palabra_elegida, game.groupName)
			bot.send_message(uid, mensaje, ParseMode.MARKDOWN)
			mensaje = "/clue Ejemplo"
			bot.send_message(uid, mensaje)			
						
	game.dateinitvote = datetime.datetime.now()
	game.board.state.fase_actual = "Proponiendo Pistas"
	Commands.save(bot, game.cid)
	
def review_clues(bot, game):
	game.dateinitvote = None
	game.board.state.fase_actual = "Revisando Pistas"
	reviewer_player = game.board.state.reviewer_player
	bot.send_message(game.cid, "El revisor %s esta viendo las pistas" % reviewer_player.name)
	send_reviewer_buttons(bot, game)
	#Commands.save(bot, game.cid)

def remove_same_elements_dict(last_votes):
	last_votes_to_lower = {key:val.lower() for key, val in last_votes.items()}
	result = {}
	for key,val in last_votes_to_lower.items():
		if val not in result.values():
			result[key] = val.lower()
		else:
			result = {key2:val2 for key2, val2 in result.items() if val2 != val}
	return {key:val for key, val in last_votes.items() if key in list(result.keys())}, {key:val for key, val in last_votes.items() if key not in list(result.keys())}
	
def send_reviewer_buttons(bot, game):
	reviewer_player = game.board.state.reviewer_player
	# Armo los botones para que el reviewer los analice.
	btns = []
	# Creo los botones para elegir al usuario
	cid = game.cid
	uid = reviewer_player.uid
	comando_callback = 'rechazar'
	mensaje_pregunta = "Partida {0}.\nElija las palabras para anularlas o Finalizar para enviar las pistas restantes al jugador activo".format(game.groupName)
	# Antes de enviar las pistas elimino las que son iguales no importa el case
	votes_before_method = len(game.board.state.last_votes)
	# En amount_shuffled guardo las cartas eliminadas
	game.board.state.last_votes, game.board.state.amount_shuffled = remove_same_elements_dict(game.board.state.last_votes)
	
	votes_after_method = len(game.board.state.last_votes)
	if votes_before_method > votes_after_method:
		bot.send_message(game.cid, "Se han eliminado automaticamente *{0}* votos".format(votes_before_method-votes_after_method), ParseMode.MARKDOWN)
	# Se ponen todos los botones de pistas
	for key, value in game.board.state.last_votes.items():
		txtBoton = value
		datos = str(cid) + "*" + comando_callback + "*" + str(value) + "*" + str(uid)
		btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])		
	comando_callback = 'finalizar'
	datos = str(cid) + "*" + comando_callback + "*" + str("finalizar") + "*" + str(uid)
	btns.append([InlineKeyboardButton('Finalizar', callback_data=datos)])	
	btnMarkup = InlineKeyboardMarkup(btns)	
	bot.send_message(uid, mensaje_pregunta, reply_markup=btnMarkup)	
	#Commands.save(bot, game.cid)
	
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
		game.board.state.last_votes = {key:val for key, val in game.board.state.last_votes.items() if val != opcion}		
		game.board.state.amount_shuffled.update({key:val for key, val in game.board.state.last_votes.items() if val == opcion})
		bot.send_message(game.cid, "El revisor %s ha descartado una pista" % reviewer_player.name)
		#Commands.save(bot, game.cid)
		
		# Si todavia hay pistas...
		if game.board.state.last_votes:
			send_reviewer_buttons(bot, game)
		else:
			bot.send_message(game.cid, "Todas las pistas han sido descartadas. Se pasa al siguiente jugador")
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
		#Commands.save(bot, game.cid)
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
			bot.send_message(game.cid, "La palabra era: {0}.\nSe ha eliminado del mazo 1 carta como penalización".format(game.board.state.acciones_carta_actual), ParseMode.MARKDOWN)			
			game.board.discards.append(game.board.state.acciones_carta_actual)
			game.board.discards.append(game.board.cartas.pop(0))
		Commands.save(bot, game.cid)
		start_next_round(bot, game)
	except Exception as e:
		bot.send_message(game.cid, 'No se ejecuto el comando debido a: '+str(e))

def send_clues(bot, game):
	text = ""
	for key, value in game.board.state.last_votes.items():
		player = game.playerlist[key] 
		text += "*{1}: {0}*\n".format(value, player.name)
	mensaje_final = "[{0}](tg://user?id={1}) es hora de adivinar! Pone /guess Palabra o /pass si no se sabes la palabra\nLas pistas son: \n{2}\n*NO SE PUEDE HABLAR*".format(game.board.state.active_player.name, game.board.state.active_player.uid, text)
	
	game.board.state.fase_actual = "Adivinando"
	Commands.save(bot, game.cid)
	
	bot.send_message(game.cid, mensaje_final, ParseMode.MARKDOWN)

def pass_just_one(bot, game):
	start_next_round(bot, game)	

def start_next_round(bot, game):
	log.info('start_next_round called')
	# start next round if there is no winner (or /cancel)
	# Si hubo descartes los muestro antes de comenzar el nuevo turno
	if game.board.state.amount_shuffled:
		text_eliminadas = "*Pistas eliminadas*\n"
		for key, value in game.board.state.amount_shuffled.items():
			player = game.playerlist[key] 
			text += "*{1}: {0}*\n".format(value, player.name)			
		bot.send_message(game.cid, text_eliminadas, ParseMode.MARKDOWN)
	increment_player_counter(game)
	start_round_just_one(bot, game)
	
def start_round(bot, game):        
        log.info('start_round called')

	
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
        



def print_player_info(player_number):
    if player_number == 5:
        return "Hay 4 investigadores y 1 cultista."
    elif player_number == 6:
        return "Hay 4 investigadores y 2 cultistas."
    elif player_number == 7:
        return "Hay 5 investigadores y 2 cultistas."
    elif player_number == 8:
        return "Hay 6 investigadores y 2 cultistas."
    elif player_number == 9:
        return "Hay 6 investigadores y 3 cultistas."

def inform_players(bot, game, cid, player_number):
        log.info('inform_players called')
        bot.send_message(cid,
                "Comencemos el juego con %d jugadores\n%s\nVe a tu chat privado y mira tu rol secreto!" % (
        player_number, print_player_info(player_number)))
        available_roles = list(playerSets[player_number]["roles"])
        
        # Elijo al jugador poseido        
        poseidoid = choice(list(game.playerlist))
        game.playerlist[poseidoid].poseido = True
                
        for uid in game.playerlist:
                random_index = randrange(len(available_roles))
                #log.info(str(random_index))
                role = available_roles.pop(random_index)
                #log.info(str(role))
                party = get_membership(role)
                game.playerlist[uid].role = role
                game.playerlist[uid].party = party
                # I comment so tyhe player aren't discturbed in testing, uncomment when deploy to production
                if not debugging:
                        bot.send_message(uid, "Tu rol secreto es: %s\nEres de los %s" % (role, party))
                else:
                        bot.send_message(ADMIN, "Jugador %s su rol es %s. Eres de los %s" % (game.playerlist[uid].name, role, party))


def inform_cultist(bot, game, player_number):
        log.info('inform_fascists called')
        for uid in game.playerlist:
                role = game.playerlist[uid].role        
                if role == "Cultista":
                        fascists = game.get_cultist()
                        poseidos = game.get_poseidos()                        
                        pstring = ""
                        for p in poseidos:
                                if p.uid != uid:
                                        pstring += p.name + ", "
                        pstring = pstring[:-2]
                        
                        if not debugging:
                                bot.send_message(uid, "El/los jugador/es poseido/s es/son: %s" % pstring)    
                        else:
                                bot.send_message(ADMIN, "El/los jugador/es poseido/s es/son: %s" % pstring)  
                                
                        if player_number > 5:
                                fstring = ""
                                for f in fascists:
                                        if f.uid != uid:
                                                fstring += f.name + ", "
                                fstring = fstring[:-2]
                        if not debugging:
                                bot.send_message(uid, "Tus amigos cultistas son: %s" % fstring)
                elif role == "Investigador":
                        pass
                else:
                        log.error("inform_fascists: can\'t handle the role %s" % role)


def get_membership(role):
    log.info('get_membership called')
    if role == "Cultista" or role == "Cultista":
        return "malos"
    elif role == "Investigador":
        return "buenos"
    else:
        return None


def increment_player_counter(game):
    log.info('increment_player_counter called')
    if game.board.state.player_counter < len(game.player_sequence) - 1:
        game.board.state.player_counter += 1
    else:
        game.board.state.player_counter = 0

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
	dp.add_handler(CommandHandler("calltovote", Commands.command_calltovote))
	dp.add_handler(CommandHandler("claim", Commands.command_claim, pass_args = True))
	
	dp.add_handler(CommandHandler("prueba", Commands.command_prueba, pass_args = True))
	
	dp.add_handler(CommandHandler("adminclue", Commands.command_forced_clue))
	dp.add_handler(CommandHandler("nextturn", Commands.command_next_turn))
	dp.add_handler(CommandHandler("guess", Commands.command_guess, pass_args = True))
	dp.add_handler(CommandHandler("pass", Commands.command_pass))
	
	# Comando para hacer comandos sql desde el chat
	dp.add_handler(CommandHandler("comando", Commands.command_newgame_sql_command, pass_args = True)) 

	# Lost Expedition Commands
	dp.add_handler(CommandHandler("hojaayuda", Commands.command_hoja_ayuda))
	dp.add_handler(CommandHandler("reglas", Commands.command_reglas))
	dp.add_handler(CommandHandler("newgamelostexpedition", Commands.command_newgame_lost_expedition))

	dp.add_handler(CommandHandler("drawcard", Commands.command_drawcard, pass_args = True))
	dp.add_handler(CommandHandler("showhand", Commands.command_showhand, pass_args = True))

	dp.add_handler(CommandHandler("losebullet", Commands.command_losebullet, pass_args = True))
	dp.add_handler(CommandHandler("gainbullet", Commands.command_gainbullet, pass_args = True))
	dp.add_handler(CommandHandler("losefood", Commands.command_losefood, pass_args = True))
	dp.add_handler(CommandHandler("gainfood", Commands.command_gainfood, pass_args = True))        
	dp.add_handler(CommandHandler("stats", Commands.command_showstats))
	dp.add_handler(CommandHandler("campero", Commands.command_vida_explorador_campero, pass_args = True))
	dp.add_handler(CommandHandler("brujula", Commands.command_vida_explorador_brujula, pass_args = True))
	dp.add_handler(CommandHandler("hoja", Commands.command_vida_explorador_hoja, pass_args = True))
	#
	dp.add_handler(CommandHandler("addrutefromhand", Commands.command_add_exploration, pass_args = True))
	dp.add_handler(CommandHandler("addrutefromdeck", Commands.command_add_exploration_deck, pass_args = True))
	dp.add_handler(CommandHandler("addrutefromhandfirst", Commands.command_add_exploration_first, pass_args = True))
	dp.add_handler(CommandHandler("moverutefirst", Commands.command_add_exploration_deck_first, pass_args = True))
	dp.add_handler(CommandHandler("swaprute", Commands.command_swap_exploration, pass_args = True))
	dp.add_handler(CommandHandler("removerute", Commands.command_remove_exploration, pass_args = True))
	dp.add_handler(CommandHandler("removelastrute", Commands.command_remove_last_exploration, pass_args = True))
	dp.add_handler(CommandHandler("showrute", Commands.command_show_exploration, pass_args = True))
	dp.add_handler(CommandHandler("sortrute", Commands.command_sort_exploration_rute, pass_args = True))
	dp.add_handler(CommandHandler("sorthand", Commands.command_sort_hand, pass_args = True))
	dp.add_handler(CommandHandler("showskills", Commands.command_showskills))
	dp.add_handler(CommandHandler("gainprogreso", Commands.command_increase_progreso, pass_args = True))
	dp.add_handler(CommandHandler("removefirstrute", Commands.command_resolve_exploration))      

	dp.add_handler(CommandHandler("gainskill", Commands.command_gain_skill, pass_args = True))
	dp.add_handler(CommandHandler("useskill", Commands.command_use_skill, pass_args = True))

	dp.add_handler(CommandHandler("losecamp", Commands.command_lose_camp, pass_args = True))
	dp.add_handler(CommandHandler("losecompass", Commands.command_lose_compass, pass_args = True))
	dp.add_handler(CommandHandler("loseleaf", Commands.command_lose_leaf, pass_args = True))
	dp.add_handler(CommandHandler("loseexplorer", Commands.command_lose_explorer, pass_args = True))

	dp.add_handler(CommandHandler("resolve", Commands.command_resolve_exploration2))
	dp.add_handler(CommandHandler("continue", Commands.command_continue, pass_args = True))

	dp.add_handler(CommandHandler("dia", Commands.command_worflow, pass_args = True))
	dp.add_handler(CommandHandler("noche", Commands.command_worflow, pass_args = True))

	dp.add_handler(CommandHandler("save", Commands.save))
	dp.add_handler(CommandHandler("load", Commands.load))	
	
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*exe\*([^_]*)\*(.*)\*([0-9]*)", callback=Commands.execute_command))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*opcioncomandos\*(.*)\*([0-9]*)", callback=Commands.elegir_opcion_comando))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*opcionskill\*(.*)\*([0-9]*)", callback=Commands.elegir_opcion_skill))
	
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*commando\*([^_]*)\*swap\*([0-9]*)", callback=Commands.callback_choose_swap))
	
	
	dp.add_handler(CommandHandler("clue", Commands.command_clue, pass_args = True))
	
	# Pruebas SH
		
	dp.add_handler(CommandHandler("role", Commands.command_choose_posible_role))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*chooserole\*(.*)\*([0-9]*)", callback=Commands.callback_choose_posible_role))

	dp.add_handler(CommandHandler("config", Commands.command_configurar_partida))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*choosegame\*(.*)\*([0-9]*)", callback=Commands.callback_choose_game))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*choosemode\*(.*)\*([0-9]*)", callback=Commands.callback_choose_mode))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*choosegameclue\*(.*)\*([0-9]*)", callback=Commands.callback_choose_game_clue))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*choosedicc\*(.*)\*([0-9]*)", callback=callback_finish_config_justone))
	
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*rechazar\*(.*)\*([0-9]*)", callback=callback_review_clues))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*finalizar\*(.*)\*([0-9]*)", callback=callback_review_clues_finalizado))
	dp.add_handler(CallbackQueryHandler(pattern="(-[0-9]*)\*reviewerconfirm\*(.*)\*([0-9]*)", callback=callback_reviewer_confirm))
	
	
	dp.add_handler(CommandHandler("tirada", Commands.command_roll, pass_args = True))
	
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
