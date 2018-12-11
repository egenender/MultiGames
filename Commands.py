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
from Constants.Cards import opciones_opcional
from Constants.Cards import opciones_choose_posible_role
from Constants.Cards import modos_juego

from Constants.Config import JUEGOS_DISPONIBLES
from Constants.Config import MODULOS_DISPONIBES


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

def command_continue(bot, update, args):
	
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	if uid not in ADMIN:
		bot.send_message(cid, uid)	
	
	game = load_game(cid)
	if game:
		GamesController.games[cid] = game		
		if game.board.state.fase_actual == "execute_actions":
			execute_actions(bot, cid, uid)
		else:
			bot.send_message(cid, "No estas en fase de continue, prueba con /resolve")
	else:
		bot.send_message(cid, "No hay juego que continuar")
	
	
def command_worflow(bot, update, args):
	cid, uid = update.message.chat_id, update.message.from_user.id
	game, player = get_base_data2(cid, uid)	
	if uid in ADMIN:
		
		modo_juego = modos_juego[game.modo]	
		tiempo_dia = "dia" if game.board.state.esdedia else "noche"
		acciones_workflow_actual = modo_juego["worflow"][tiempo_dia]		
		game.board.state.acciones_carta_actual = acciones_workflow_actual
		game.board.state.index_accion_actual = 1
		
		# Hago reset de cartas en deck ya que al ppio no deberia ser, igual esto lo deberia hacer el al final 
		game.board.state.count_cartas_deck = 0
		
		bot.send_message(cid, "Se inicia la ejecución del %s. Utilizar /continue en caso que se trabe." % tiempo_dia)
		#showImages(bot, cid, [game.board.cartasExplorationActual[0]])
		execute_actions(bot, cid, uid)

# Metodo que ira ejecutando las acciones.
# Si una accion no tiene opciones comenzará a ejecutarla.
# Se hará cada comando uno atras del otro hasta cumplir 
def execute_actions(bot, cid, uid):
	
	game, player = get_base_data2(cid, uid)
	if game is not None:
		# Seteo que estoy ejecutando acciones
		game.board.state.fase_actual = "execute_actions"
		
		#sleep(2)
		#try:
		#ot.send_message(cid, "Init Execute Actions")		
		acciones = game.board.state.acciones_carta_actual		
		index_accion_actual = game.board.state.index_accion_actual
		try:
			accion_actual = acciones[index_accion_actual]
		except Exception as e:
			accion_actual = acciones[str(index_accion_actual)]
		tipo_accion_actual = accion_actual["tipo"]
		index_opcion_actual = game.board.state.index_opcion_actual
		opciones_accion_actual = accion_actual["opciones"]

		# Veo si hay más de una opcion, si no la hay seteo el index_opcion_actual a 1
		if len(opciones_accion_actual) == 1 and tipo_accion_actual != "opcional":
			index_opcion_actual = 1
			
		# Si el tipo_accion_actual es opcional y es la primera vez que entra...
		#t.send_message(cid, "La accion que se esta ejecutando es de tipo %s" % tipo_accion_actual)
		if tipo_accion_actual == "opcional":
			#bot.send_message(cid, "Es una accion opcional. El indice es %s" % str(index_opcion_actual))
			if str(index_opcion_actual) == "0":
				#ot.send_message(cid, "Entrado en elegir si se hace o no la accion opcional")
				# Mando una pregunta para elegir accion.				
				#bot.send_message(opciones_opcional)
				send_choose_buttons(bot, cid, uid, game, opciones_opcional)
				return
			elif index_opcion_actual == 2:
				# Si es no pongo la primera opcion y comando ridiculamente alto para terminar la accion.
				game.board.state.index_opcion_actual = 1
				index_opcion_actual = 1
				game.board.state.index_comando_actual = 99									
			
		# Si el jugador ya eligio opcion.
		if index_opcion_actual != 0:
			
			#Continuo ejecutando la opcion actual hasta que se le acaben los comandos				
			try:
				opcion_actual = opciones_accion_actual[index_opcion_actual]
			except Exception as e:
				opcion_actual = opciones_accion_actual[str(index_opcion_actual)]
			comandos_opcion_actual = opcion_actual["comandos"]
			# Obtengo el ultimo indice de comando y le aumento 1.
			if (game.board.state.comando_pedido and game.board.state.comando_realizado) or not game.board.state.comando_pedido:
				game.board.state.index_comando_actual += 1
				game.board.state.comando_pedido = False
				game.board.state.comando_realizado = False			
				
			index_comando_actual = game.board.state.index_comando_actual
			#bot.send_message(cid, "Realizando comando %s/%s de la accion %s" % (str(index_comando_actual), str(len(comandos_opcion_actual)), game.board.state.index_accion_actual))
			# Si es mayor a la cantidad de comandos entonces ya ejecute todos los comandos!
			if index_comando_actual > len(comandos_opcion_actual):
				# Vuelvo atras los indices. Voy a la siguiente accion. Para eso aumento el indice de accion actual,
				# y reseteo los otros
				game.board.state.index_comando_actual = 0 
				game.board.state.index_opcion_actual = 0
				game.board.state.estado_accion_opcional = 0
				# Verifico si hay otra accion a realizar para eso hago lo mismo que con los comandos
								
				game.board.state.index_accion_actual += 1
				if game.board.state.index_accion_actual > len(acciones):
					# Si ya se hicieron todas las acciones vuelvo el indice a 0 y terminamos!
					game.board.state.index_accion_actual = 0
					
					if game.board.state.ejecutando_carta:
						game.board.state.ejecutando_carta = False
															
						if game.board.state.adquirir_final:
							command_gain_skill(bot, None, [0, cid, uid])
							# Pongo en off el flag de adquirir final
							game.board.state.adquirir_final = False
						else:
							command_remove_exploration(bot, None, [1,cid,uid])
						# Si todavia hay cartas pido al usuario que continue la ejecucion.
						if game.board.cartasExplorationActual:
							bot.send_message(cid, "Se ha terminado de resolver la carta. Continue con /resolve")
						
					else:
						command_show_exploration(bot, None, [1,cid,uid])
						bot.send_message(cid, "Puede comenzar a resolver la ruta con /resolve")
					game.board.state.fase_actual = "resolve"
					save(bot, cid)
				else:
					# Llamada recursiva con nuevo indice de accion actual
					execute_actions(bot, cid, uid)		
			else:
				#Antes de comenzar a ejecutar comandos
				# Ejecuto el proximo comando
				
				game.board.state.comando_realizado = False
				game.board.state.comando_pedido = True
				try:
					comando_actual = comandos_opcion_actual[index_comando_actual]
				except Exception as e:
					comando_actual = comandos_opcion_actual[str(index_comando_actual)]
				#t.send_message(cid, "Comando a executar %s" % comando_actual )
				comando = comandos[comando_actual]
				
				if "comando_argumentos" in opcion_actual:
					comando_argumentos = opcion_actual["comando_argumentos"]
				else:
					comando_argumentos = None
				
				if "ejecutar_al_final" in opcion_actual:
					ejecutar_al_final = opcion_actual["ejecutar_al_final"]
					bot.send_message(cid, "Deberia ejecutar al final el comando %s" % ejecutar_al_final)
				else:
					ejecutar_al_final = None
				
				iniciar_ejecucion_comando(bot, cid, uid, comando, comando_argumentos, ejecutar_al_final)
		else:
			# En el caso de que haya varias opciones le pido al usuario qwue me diga cual prefiere.
			send_choose_buttons(bot, cid, uid, game, opciones_accion_actual)
			
		#except Exception as e:
		#	bot.send_message(cid, 'No se ejecuto el execute_actions debido a: '+str(e))
	
def send_choose_buttons(bot, cid, uid, game, opciones_accion_actual):
	#sleep(3)
	strcid = str(game.cid)
	btns = []
	player = game.playerlist[uid]
	# Creo los botones para elegir al usuario
	for opcion_comando in opciones_accion_actual:							
		txtBoton = ""
		comando_op = opciones_accion_actual[opcion_comando]								
		for comando in comando_op["comandos"]:			
			if comando_op["comandos"][comando] in comandos:
				cmd = comandos[comando_op["comandos"][comando]]
			else:
				cmd = None
			# Busco si el comando tiene un texto.
			if cmd is not None and "txt_boton" in cmd:
				txtBoton += cmd["txt_boton"] + " "
			else:
				txtBoton += comando_op["comandos"][comando] + " "
		txtBoton = txtBoton[:-1]
		'''	
		
		if len(txtBoton) > 15:
			txtBoton = txtBoton[:15]
		'''		
		#txtBoton = "%s" % (opcion_comando)
		datos = strcid + "*opcioncomandos*" + str(opcion_comando) + "*" + str(uid)
		#log.info("Se crea boton con datos: %s %s" % (txtBoton, datos))
		#ot.send_message(cid, datos)	
		
		# Me fijosi la opcion tiene alguna restriccion, en ese caso la verifico
		# Ejemplo "restriccion" : ["player", "hand", "distinct", "0"]
		if "restriccion" in comando_op:
			atributo = get_atribute(comando_op["restriccion"], game, player)
			#ot.send_message(cid, atributo)
			if not verify_restriction(atributo, comando_op["restriccion"][2], comando_op["restriccion"][3]):
				btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])
		else:
			btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])
	btnMarkup = InlineKeyboardMarkup(btns)
	#for uid in game.playerlist:
	bot.send_message(cid, "Elija una de las opciones:", reply_markup=btnMarkup)

def get_atribute(restriccion, game, player):
	if restriccion[0] == "player":
		return getattr(player, restriccion[1])
	elif restriccion[0] == "state":
		return getattr(game.board.state, restriccion[1])

def verify_restriction(atributo, tipo, restriccion):
	if tipo == "len":
		return str(len(atributo)) == restriccion
	elif tipo == "igual":
		return str(atributo) == restriccion
	
def elegir_opcion_comando(bot, update):	
	#try:		
	callback = update.callback_query
	log.info('elegir_opcion_comando called: %s' % callback.data)	
	regex = re.search("(-[0-9]*)\*opcioncomandos\*(.*)\*([0-9]*)", callback.data)
	cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)	
	
	game = get_game(cid)
	game.board.state.index_opcion_actual = int(opcion)
	
	#bot.delete_message(callback.chat.id, callback.message.message_id)
	bot.edit_message_text("Has elegido la opcion: %s" % opcion, cid, callback.message.message_id)
	execute_actions(bot, cid, uid)
	#except Exception as e:
	#		bot.send_message(cid, 'No se ejecuto el elegir_opcion_comando debido a: '+str(e))

def elegir_opcion_skill(bot, update):	
	#try:		
	callback = update.callback_query
	log.info('elegir_opcion_comando called: %s' % callback.data)	
	regex = re.search("(-[0-9]*)\*opcionskill\*(.*)\*([0-9]*)", callback.data)
	cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)	
	
	game, player = get_base_data2(cid, uid)
	game.board.state.index_opcion_actual = int(opcion)
	
	index_player_skill = player.skills.index(int(opcion))
	#bot.delete_message(callback.chat.id, callback.message.message_id)
	bot.edit_message_text("Has elegido la carta: %s" % opcion, cid, callback.message.message_id)
	command_use_skill(bot, update, [index_player_skill, cid, uid])
	#except Exception as e:
	#		bot.send_message(cid, 'No se ejecuto el elegir_opcion_comando debido a: '+str(e))

def ejecutar_comando(bot, cid, uid, comando, comando_argumentos, ejecutar_al_final):
	#try:
	log.info('ejecutar_comando called: %s' % comando)
	#bot.send_message(cid, comando)
	#sleep(3)
	game, player = get_base_data2(cid, uid)
	tipo_comando = comando["tipo"]
	# Si el comando es automatico, lo ejecuto sin no deberia pedir argumentos
	if tipo_comando == "automatico":
		# Si el command que quiero usar tiene args se los agrego.
		# Le agrego los argumentos default en caso de que el metodo no me traiga algunos ya ingresados.
		if "comando_argumentos" in comando and comando_argumentos is None:
			getattr(sys.modules[__name__], comando["comando"])(bot, None, [comando["comando_argumentos"], cid, uid])										
		else:
			if comando_argumentos is not None:
				getattr(sys.modules[__name__], comando["comando"])(bot, None, [comando_argumentos, cid, uid])
			else:
				getattr(sys.modules[__name__], comando["comando"])(bot, None, [None, cid, uid])
				
		# Si tiene un comando a ejecutar al final del comando...
		if ejecutar_al_final is not None:
			getattr(sys.modules[__name__], ejecutar_al_final)(bot, game, player)		
	elif tipo_comando == "indicaciones":
		# Genero los botones para preguntar al usuario.
		strcid = str(game.cid)
		
		# Creo los botones para elegir al usuario
		# TODO Automatizar de donde se saca esta lista
		if "player.hand" in comando["indicacion_argumentos"]:			
			#btnMarkup = get_player_hand_buttons(player, comando, strcid)
			btnMarkup = get_list_buttons(player.uid, player.hand, comando["comando"], strcid)
			command_showhand(bot, None, [-1, cid, uid])
		elif "exploradores" in comando["indicacion_argumentos"]:
			btns = get_player_exploradores_buttons(player, comando, strcid)
			if "Usar carta skill" in comando["indicacion_argumentos"]:
				argumento = "Usar carta skill"
				txtBoton = "%s" % (argumento)
				datos = strcid + "*exe*" + argumento + "*" + comando["comando"] + "*" + str(uid)
				btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])
			btnMarkup = InlineKeyboardMarkup(btns)
		else:
			btns = []
			for argumento in comando["indicacion_argumentos"]:
				txtBoton = "%s" % (argumento)
				datos = strcid + "*exe*" + argumento + "*" + comando["comando"] + "*" + str(uid)
				log.info("Se crea boton con datos: %s %s" % (txtBoton, datos))
				#ot.send_message(cid, datos)					
				btns.append([InlineKeyboardButton(txtBoton, callback_data=datos)])
			btnMarkup = InlineKeyboardMarkup(btns)
		#for uid in game.playerlist:
		bot.send_message(cid, comando["indicacion"], reply_markup=btnMarkup)
	else:
		game.board.state.adquirir_final = True
		after_command(bot, cid)
		# Si tiene un comando a ejecutar al final del comando...
		if ejecutar_al_final is not None:
			getattr(sys.modules[__name__], ejecutar_al_final)(bot, game, player)
		
	
def iniciar_ejecucion_comando(bot, cid, uid, comando, comando_argumentos, ejecutar_al_final):
	ejecutar_comando(bot, cid, uid, comando, comando_argumentos, ejecutar_al_final)
	# Despues de ejecutar continuo las ejecuciones si el comando no fue del tipo indicaciones
	tipo_comando = comando["tipo"]
	if tipo_comando != "indicaciones":
		execute_actions(bot, cid, uid)

def get_player_hand_buttons(player, comando, strcid):
	return get_list_buttons(player.uid, player.hand, comando["comando"], strcid)

def get_list_buttons(uid, lista, strcomando, strcid, callback_comando = 'exe'):
	i = 1
	btns = []
	buttonGroup = []	
	for argumento in lista:
		txtBoton = "%s" % (argumento)
		datos = strcid + "*" + callback_comando + "*" + str(i) + "*" + strcomando + "*" + str(uid)
		#log.info("Se crea boton con datos: %s %s" % (txtBoton, datos))
		#ot.send_message(cid, datos)	
		buttonGroup.append(InlineKeyboardButton(txtBoton, callback_data=datos))
		# Agrupo en grupos de 3
		if (i % 3 ==0):
			btns.append(buttonGroup)
			buttonGroup = []
		i += 1
	# Pongo el resto que haya quedado 1 o 2 elementos
	if len(buttonGroup) > 0:
		btns.append(buttonGroup)
	return InlineKeyboardMarkup(btns)

def get_player_exploradores_buttons(player, comando, strcid):	
	i = 1
	btns = []
	buttonGroup = []
	exploradores_list = ["Campero %d❤️" % player.vida_explorador_campero, "Brujula %d❤️" % player.vida_explorador_brujula , "Hoja %d❤️" % player.vida_explorador_hoja]
	
	for argumento in exploradores_list:
		# Si esta muerto no puede perder más vida.
		if "0" in argumento:
			continue
		txtBoton = "%s" % (argumento)
		datos = strcid + "*exe*" + argumento + "*" + comando["comando"] + "*" + str(player.uid)
		#log.info("Se crea boton con datos: %s %s" % (txtBoton, datos))
		#ot.send_message(cid, datos)	
		buttonGroup.append(InlineKeyboardButton(txtBoton, callback_data=datos))
		# Agrupo en grupos de 3
		if (i % 3 ==0):
			btns.append(buttonGroup)
			buttonGroup = []
		i += 1
	# Pongo el resto que haya quedado 1 o 2 elementos
	if len(buttonGroup) > 0:
		btns.append(buttonGroup)
	return btns
	
def increase_count_cartas_deck(bot, game, player):
	game.board.state.count_cartas_deck += 1
	save(bot, game.cid)
	
def reset_count_cartas_deck(bot, game, player):
	game.board.state.count_cartas_deck = 0
	save(bot, game.cid)

def resolve(bot, cid, uid, game, player):
	if game is not None:
		# Busco la carta y obtengo sus acciones		
		if not game.board.cartasExplorationActual:
			bot.send_message(cid, "Exploracion Actual no tiene cartas")			
		else:
			#try:
			# Busco la carta y sus acciones
			carta = cartas_aventura[game.board.cartasExplorationActual[0]]
			#bot.send_message(cid, carta)
			acciones = carta["acciones"]
			# Seteo los indices, las acciones siempre empiezan en 1
			game.board.state.acciones_carta_actual = acciones
			game.board.state.index_accion_actual = 1
			game.board.state.index_comando_actual = 0 
			game.board.state.index_opcion_actual = 0

			bot.send_message(cid, "Se inicia la ejecución de proxima carta de ruta. Utilizar comando /continue en caso que se trabe. Al final se deberia resolver o adquirir la carta.")
			showImages(bot, cid, [game.board.cartasExplorationActual[0]])
			game.board.state.ejecutando_carta = True
			execute_actions(bot, cid, uid)
			#except Exception as e:
			#	bot.send_message(cid, 'No se ejecuto el coommand_resolve_exploration2 debido a: '+str(e))

	
def command_resolve_exploration2(bot, update):
	# Metodo que da los datos basicos devuelve Game=None Player = None si no hay juego.
	'''cid, uid = update.message.chat_id, update.message.from_user.id	
	game = load_game(cid)
	game, player = get_base_data2(cid, uid)
	'''
	
	# Voy sobre seguro, obtengo de BD la app por si hubo se hizo un resolver que no llego a grabar 
	cid, uid = update.message.chat_id, update.message.from_user.id	
	game, player = get_base_data2(cid, uid)
	
	if game:
		if game.board.state.index_accion_actual == 0 or game.board.state.fase_actual == "resolve":			
			#player = game.playerlist[uid]
			resolve(bot, cid, uid, game, player)		
		else:
			bot.send_message(cid, "No estas en fase de resolve, prueba con /continue")
	else:
		bot.send_message(cid, "No hay juego que resolver")	
			
def execute_command(bot, update):
	callback = update.callback_query
	#log.info('execute_command called: %s' % callback.data)
	regex = re.search("(-[0-9]*)\*exe\*([^_]*)\*(.*)\*([0-9]*)", callback.data)
	cid = int(regex.group(1))
	strcid = regex.group(1)	
	opcion = regex.group(2)
	comando = regex.group(3)
	uid = int(regex.group(4))
	struid = regex.group(4)	
	bot.edit_message_text("Has elegido la opcion: %s" % opcion, cid, callback.message.message_id)
	#ot.send_message(cid, "%s %s %s %s" % (strcid, opcion, comando, struid ))
	# Directamente lo ejecuto ya que tengo el argumento.
	resultado = getattr(sys.modules[__name__], comando)(bot, update, [opcion, cid, uid])
	#ot.send_message(cid, resultado)
	# Despues de ejecutar continuo las ejecuciones. Solamente si el comando no tiene un retorno.
	if resultado is None:
		execute_actions(bot, cid, uid)
	
	
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
					if len(tabla_str) < 4096:
						bot.send_message(cid, table)
					else:
						n = 4090
						parts = [tabla_str[i:i+n] for i in range(0, len(tabla_str), n)]
						for part in parts:
							bot.send_message(cid, part)
			else:
				bot.send_message(cid, 'No se obtuvo nada de la consulta')
		except Exception as e:
			bot.send_message(cid, 'No se ejecuto el comando debido a: '+str(e))
			conn.rollback()

# The Lost Expedition
# Generic commands for all games
def showImages(bot, cid, cartas, img_caption = ""):
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
	bot.send_photo(cid, photo=bio, caption=img_caption)
	
def save(bot, cid):
	try:		
		#groupName = "Prueba"		
		game = GamesController.games.get(cid, None)
		gameType = 'LostExpedition'
		save_game(cid, game.groupName, game, gameType )
		#bot.send_message(cid, 'Se grabo correctamente.')
		log.info('Se grabo correctamente.')
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

# Despues de cada comando que actualiza el juego se graba
def after_command(bot, cid):	
	game = get_game(cid)
	# Logica normal, solamente pongo algo como realizado si algo fue pedido.
	if game.board.state.comando_pedido:
		game.board.state.comando_realizado = True
	save(bot, cid)
	
#Lost Expedition
# Comando para hacer luego de que se achica la ruta a explorar
def after_ruta_achicada(bot, cid, uid):
	#sleep(3)
	game = get_game(cid)
	player = game.playerlist[uid]
	if not game.board.cartasExplorationActual:
		# Si es de dia se hace de noche y diceversa
		if game.board.state.esdedia:
			game.board.state.esdedia = False
		else:
			game.board.state.esdedia = True
		
		tiempo = "DÍA. Has /dia para continuar" if game.board.state.esdedia else "NOCHE. Has /noche para continuar"
		bot.send_message(cid, "Exploracion Actual no tiene cartas. Se cambia a %s" % tiempo)
		
		if player.food != 0:
			bot.send_message(cid, "Se pierde uno de comida")
			command_losefood(bot, None, [0, cid, uid])
		else:
			bot.send_message(cid, "Como no hay comida alguien tiene habre. (-1 vida)")
			comando = comandos["lose_life"]
			iniciar_ejecucion_comando(bot, cid, uid, comando, None, None)
	'''
	else:
		# Deduzco de que la ruta se achica por resolve...
		bot.send_message(cid, "Se ha terminado de resolver la carta. Continue con /resolve")
	'''
		
def command_hoja_ayuda(bot, update):
	cid = update.message.chat_id
	help_text = "Eventos amarillos son obligatorios\n" + \
			"Eventos rojo son obligatorios pero tenes que elegir 1\n"  + \
			"Eventos Azules son opcionales"
	bot.send_message(cid, help_text)
	bot.send_photo(cid, photo=open('/app/img/LostExpedition/Ayuda01.jpg', 'rb'))	
	bot.send_photo(cid, photo=open('/app/img/LostExpedition/Ayuda02.jpg', 'rb'))

def command_newgame_lost_expedition(bot, update):
	cid = update.message.chat_id
	fname = update.message.from_user.first_name
	uid = update.message.from_user.id
	groupName = update.message.chat.title
	if uid in ADMIN:
		try:
			game = get_game(cid)
			if game:
				bot.send_message(cid, "Hay un juego ya creado, borralo con /delete.")
			else:
				# Creo el juego si no esta.
				game = Game(cid, update.message.from_user.id, groupName, "LostExpedition" ,"Solitario", )
				GamesController.games[cid] = game
				# Creo el jugador que creo el juego y lo agrego al juego
				player = Player(fname, uid)
				game.add_player(uid, player)				
				player_number = len(game.playerlist)
				bot.send_message(cid, "Se creo el juego y el usuario")
				save(bot, game.cid)
				MainController.init_game(bot, game)

		except Exception as e:
			bot.send_message(cid, 'Error '+str(e))


		
def command_drawcard(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	if uid in ADMIN:
		#bot.send_message(cid, args)
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		# Si no se paso argumento paso 2 cartas.
		try:
			cantidad = int(args[0] if args else 1)
		except Exception as e:
			cantidad = int(args[0][0] if args else 1)
		#log.info(game.board.cartasAventura)
		for i in range(cantidad):
			draw_card_cartasAventura(game, player.hand)		
		#log.info(game.board.cartasAventura)
		#cid = '-1001206290323'
		#log.info(player.hand)
		bot.send_message(cid, "Se han obtenido %s cartas" % cantidad)
		#command_showhand(bot, update, [None, cid, uid])
		# Ordeno las cartas del jugador
		player.hand.sort()
		after_command(bot, cid)
		
def command_showhand(bot, update, args):	
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		if not player.hand:
			bot.send_message(cid, "El jugador no tiene cartas")
		else:
			
			showImages(bot, cid, player.hand, "Mano del Jugador")
		
def command_showskills(bot, update):	
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		if not player.skills:
			bot.send_message(cid, "El jugador no tiene skills.")
		else:
			showImages(bot, cid, player.skills, "Skills jugador")

def command_increase_progreso(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		game.board.progreso += 1
		if game.board.progreso == game.board.objetivoprogreso:
			bot.send_message(cid, "Ganaste")
		else:
			bot.send_message(cid, "Estas a %s de distancia, el objetivo es 9" % game.board.progreso)
		after_command(bot, cid)
		'''
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		if not player.skills:
			bot.send_message(cid, "El jugador no tiene skills.")
		else:
			showImages(bot, cid, player.skills)
		'''
			
def command_losebullet(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		player.bullets -= 1;		
		bot.send_message(cid, "Se ha perdido una bala")
		#ommand_showstats(bot, update)
		after_command(bot, cid)
		
def command_gainbullet(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		player.bullets += 1;
		bot.send_message(cid, "Se ha ganado una bala")
		#ommand_showstats(bot, update)
		after_command(bot, cid)
		
def command_losefood(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		player.food -= 1;
		bot.send_message(cid, "Se ha perdido uno de comida")
		#ommand_showstats(bot, update)
		after_command(bot, cid)
		
def command_gainfood(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		player.food += 1;
		bot.send_message(cid, "Se ha ganado uno de comida")
		#ommand_showstats(bot, update)
		after_command(bot, cid)

def command_lose_life(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
			
	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		if "Campero" in args[0]:
			player.vida_explorador_campero  -=1;
		if "Brujula" in args[0]:
			player.vida_explorador_brujula  -=1;
		if "Hoja" in args[0]:
			player.vida_explorador_hoja  -=1;		
		#Command_showstats(bot, update)
		after_command(bot, cid)
		
def command_gain_life(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		if "Campero" in args[0]:
			player.vida_explorador_campero  +=1;
		if "Brujula" in args[0]:
			player.vida_explorador_brujula  +=1;
		if "Hoja" in args[0]:
			player.vida_explorador_hoja  +=1;		
		
		after_command(bot, cid)
		
def command_vida_explorador_campero(bot, update, args):
	cid, uid = update.message.chat_id, update.message.from_user.id	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		player.vida_explorador_campero  -= int(args[0] if args else 1);
		command_showstats(bot, update)
		after_command(bot, cid)
		
def command_vida_explorador_brujula(bot, update, args):
	cid, uid = update.message.chat_id, update.message.from_user.id	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		player.vida_explorador_brujula  -= int(args[0] if args else 1);
		command_showstats(bot, update)
		after_command(bot, cid)
		
def command_vida_explorador_hoja(bot, update, args):
	cid, uid = update.message.chat_id, update.message.from_user.id	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		player.vida_explorador_hoja  -= int(args[0] if args else 1);
		command_showstats(bot, update)
		after_command(bot, cid)

def command_add_exploration(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		# Primera carta de la mano si no pone argumentos
		carta = int(args[0] if args else 1)-1
		game.board.cartasExplorationActual.append(player.hand.pop(carta))		
		after_command(bot, cid)
		# Si es de día se organiza numericamente. Independiente de modo de juego.
		if game.board.state.esdedia:			
			command_sort_exploration_rute(bot, update, args)
			bot.send_message(cid, "Se ha agregado la carta a la ruta y se ha ordenado la ruta")
		else:
			bot.send_message(cid, "Se ha agregado la carta al final de la ruta")
		#command_showhand(bot, update)
		#command_show_exploration(bot, update)		

def command_add_exploration_first(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		# Primera carta de la mano si no pone argumentos				
		try:
			carta = int(args[0] if args else 1)-1
		except Exception as e:
			carta = int(args[0][0] if args[0] else 1)-1
		
		game.board.cartasExplorationActual.insert(0, player.hand.pop(carta))
		bot.send_message(cid, "Se ha agregado la carta al principio de la ruta")
		after_command(bot, cid)
		if game.board.state.esdedia:
			command_sort_exploration_rute(bot, update, args)
		#command_showhand(bot, update)
		#command_show_exploration(bot, update)		
		

def draw_card_cartasAventura(game, destino):
	destino.append(game.board.cartasAventura.pop(0))
	# Me fijo si hay carta en cartasAventura si no hay más mezclo el descarte en el mazo de aventura
	if not game.board.cartasAventura:
		game.board.cartasAventura = random.sample(game.board.discards, len(game.board.discards))
		game.board.discards = []
		game.board.state.amount_shuffled += 1
		if game.board.state.amount_shuffled == 1:
			bot.send_message(cid, "Se ha mezclado el mazo y se debe consumir 1 de comida")
			#for uid in game.playerlist:
			#	player = game.playerlist[uid]
		else:
			bot.send_message(cid, "Se ha perdido la partida porque se ha mezclado el mazo dos veces. /delete")

def command_peek_deck(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		top_card = game.board.cartasAventura[0]
		showImages(bot, cid, [top_card], "Carta de arriba del deck")
		after_command(bot, cid)
			
def command_add_rute_option(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		try:
			opcion = args[0] if args else "Al final"
		except Exception as e:
			opcion = args[0][0] if args else "Al final"
		if opcion == "Al final":
			command_add_exploration_deck(bot, update, [1, cid, uid]) 
		else:
			command_add_exploration_deck_first(bot, update, [-1, cid, uid])
				
def command_add_exploration_deck(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return		
		#cid = '-1001206290323'
		try:
			cantidad = int(args[0] if args else 1)
		except Exception as e:
			cantidad = int(args[0][0] if args else 1)
		
		#log.info(game.board.cartasAventura)
		for i in range(cantidad):			
			draw_card_cartasAventura(game, game.board.cartasExplorationActual)
		bot.send_message(cid, "Se ha agregado %s cartas al final de la ruta desde el mazo" % cantidad)
				
		after_command(bot, cid)
		
		# Si es de día se organiza numericamente. Independiente de modo de juego.
		if game.board.state.esdedia and not game.board.state.comando_pedido :
			command_sort_exploration_rute(bot, update, args)
		#log.info(game.board.cartasAventura)
		#command_show_exploration(bot, update)
		
def command_add_exploration_deck_first(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return		
		#cid = '-1001206290323'
		# Siempre se agrega de a 1 carta 
		game.board.cartasExplorationActual.insert(0, game.board.cartasAventura.pop(0))		
		bot.send_message(cid, "Se ha agregado la carta al principio de la ruta")
		after_command(bot, cid)
		#log.info(game.board.cartasAventura)
		#command_show_exploration(bot, update)		
		
def command_show_exploration(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return		
		#cid = '-1001206290323'		
		if not game.board.cartasExplorationActual:
			bot.send_message(cid, "Exploracion Actual no tiene cartas")
		else:
			#ot.send_message(cid, "Exploracion Actual")
			showImages(bot, cid, game.board.cartasExplorationActual, "Exploracion Actual")

def command_sort_exploration_rute(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		game.board.cartasExplorationActual.sort()
		#command_show_exploration(bot, update, args)
		after_command(bot, cid)
		#bot.send_message(cid, "Las cartas de ruta han sido ordenadas.")

def command_swap_exploration(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return		
		#cid = '-1001206290323'
		# Me fijo que haya pasado los dos arguemtnso
		if len(args) < 2:
			bot.send_message(cid, "Se tienen que ingresar 2 argumentos")
			return			
		if args[0] == "Sí" or args[0] == "No":			
			if args[0] == "Sí":
				player = game.playerlist[uid]
				
				if len(game.board.state.swap_cards) < 2:
					btnMarkup = get_list_buttons(player.uid, game.board.cartasExplorationActual[1:], "swap", str(cid), "commando")
					bot.send_message(cid, "Elija la carta a cambiar", reply_markup=btnMarkup)
					return "Esperar"
				else:
					command_swap_exploration(bot, update, ["Finalizado", cid, uid, game.board.state.swap_cards[0], game.board.state.swap_cards[1]])
			else:
				bot.send_message(cid, "Se ha decidido no hacer swap")
				after_command(bot, cid)
		else:
			try:
				a, b =  int(args[0])-1, int(args[1])-1
			except Exception as e:
				# No se resta 1 porque el indice tendria que ser 1 más debido a que.
				a, b =  int(args[3]), int(args[4])
			game.board.state.swap_cards = []	
			game.board.cartasExplorationActual[b], game.board.cartasExplorationActual[a] = game.board.cartasExplorationActual[a], game.board.cartasExplorationActual[b]		
			bot.send_message(cid, "Se han intercambiado las cartas %s y %s de la ruta" % (str(a), str(b)))
			after_command(bot, cid)			
			if game.board.state.comando_pedido:
				execute_actions(bot, cid, uid)
			#command_show_exploration(bot, update)

def callback_choose_swap(bot, update):
	callback = update.callback_query
	log.info('callback_choose_swap called: %s' % callback.data)	
	regex = re.search("(-[0-9]*)\*commando\*([^_]*)\*swap\*([0-9]*)", callback.data)
	cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
	bot.edit_message_text("Has elegido la carta: %s" % opcion, cid, callback.message.message_id)
	game = get_game(cid)
	game.board.state.swap_cards.append(int(opcion))
	command_swap_exploration(bot, update, ["Sí", cid, uid])
			
# Remove se usara para resolver y para remover cartas por accion de otras cartas		
def command_remove_exploration(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		# Defecto saco la de la izquierda
		try:
			item_to_remove = int(args[0] if args else 2)-1
		except Exception as e:
			item_to_remove = int(args[0][0] if args[0] else 2)-1
			
		try:			
			game.board.discards.append(game.board.cartasExplorationActual.pop(item_to_remove))
			bot.send_message(cid, "La carta se ha eliminado de la ruta")
			after_ruta_achicada(bot, cid, uid)
			after_command(bot, cid)
			#command_show_exploration(bot, update)
		except Exception as e:
			if str(e) == "pop index out of range":
				# Si se ha pedido automaticamente 
				if game.board.state.comando_pedido:
					bot.send_message(cid, "Se ha intentado sacar una carta que no existe, considero ejecutada la accion.")
					after_command(bot, cid)
				
			else:
				bot.send_message(cid, "El remover carta de exploracion ha fallado debido a: "+str(e))
			

def command_remove_last_exploration(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if len(game.board.cartasExplorationActual) == 1:
			bot.send_message(cid, "No se puede quitar la ultima carta de exploración, considero ejecutada la acción.")
			after_command(bot, cid)
		else:
			command_remove_exploration(bot, update, [[len(game.board.cartasExplorationActual)], cid, uid])
		
		
# Resolver es basicamente remover pero la de mas a la izquierda.
def command_resolve_exploration(bot, update):
	cid, uid = update.message.chat_id, update.message.from_user.id	
	if uid in ADMIN:
		command_remove_exploration(bot, update, [1])

		
def command_gain_skill(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]	
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]
		#cid = '-1001206290323'
		# Defecto saco la de la izquierda
		item_to_remove = 0		
		player.skills.append(game.board.cartasExplorationActual.pop(item_to_remove))
		bot.send_message(cid, "La carta de la ruta ha sido obtenida como skill")
		after_ruta_achicada(bot, cid, uid)
		after_command(bot, cid)
		#command_show_exploration(bot, update)
		
def command_use_skill(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	if uid in ADMIN:
		game = get_game(cid)
		player = game.playerlist[uid]
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		# Si no se pasa parametro o paso -1 hago promp para que la elija		
		if args and args[0] == -1:
			sleep(2)
			if not player.skills:
				bot.send_message(cid, "El jugador no tiene skills.")
				if game.board.state.comando_pedido:
					execute_actions(bot, cid, uid)
				# Si se esta ejecutando de forma automaticamente se vuelve
			else:				
				i = 1
				btns = []
				buttonGroup = []	
				for skill in player.skills:
					txtBoton = "Carta %s" % (skill)
					datos = str(cid) + "*opcionskill*" + str(skill) + "*" + str(uid)
					#log.info("Se crea boton con datos: %s %s" % (txtBoton, datos))
					#ot.send_message(cid, datos)	
					buttonGroup.append(InlineKeyboardButton(txtBoton, callback_data=datos))
					# Agrupo en grupos de 3
					if (i % 3 ==0):
						btns.append(buttonGroup)
						buttonGroup = []
					i += 1
				# Pongo el resto que haya quedado 1 o 2 elementos
				if len(buttonGroup) > 0:
					btns.append(buttonGroup)
				btnMarkup = InlineKeyboardMarkup(btns)
				bot.send_message(cid, "Elija una carta de skill:", reply_markup=btnMarkup)
				return "Esperar"
		else:
			#cid = '-1001206290323'
			# Defecto saco la de la izquierda
			item_to_remove = int(args[0])-1		
			game.board.discards.append(player.skills.pop(item_to_remove))
			bot.send_message(cid, "La carta de la skill ha sido utilizada y puesta en el descarte.")
			after_command(bot, cid)
			if game.board.state.comando_pedido:
				execute_actions(bot, cid, uid)
			
		#command_show_exploration(bot, update)
		
def command_sort_hand(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	if uid in ADMIN:
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		player = game.playerlist[uid]	
		player.hand.sort()		
		command_showhand(bot, update, args)
		after_command(bot, cid)
		
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

def command_lose_camp(bot, update, args):
	#log.info(args)
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	game, player = get_base_data2(cid, uid)	
	if game is None:
		return
	if "Campero" in args[0]:
		player.vida_explorador_campero  -=1;
		after_command(bot, cid)
	if "Brujula" in args[0]:
		player.vida_explorador_brujula  -=2;
		after_command(bot, cid)
	if "Hoja" in args[0]:
		player.vida_explorador_hoja  -=2;
		after_command(bot, cid)
	if args[0] == "Usar carta skill":
		return command_use_skill(bot, None, [-1,cid,uid])	
	
def command_lose_compass(bot, update, args):
	#log.info(args)
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	game, player = get_base_data2(cid, uid)
	if game is None:
		return
	if "Campero" in args[0]:
		player.vida_explorador_campero  -=2;
		after_command(bot, cid)
	if "Brujula" in args[0]:
		player.vida_explorador_brujula  -=1;
		after_command(bot, cid)
	if "Hoja" in args[0]:
		player.vida_explorador_hoja  -=2;
		after_command(bot, cid)
	if args[0] == "Usar carta skill":
		return command_use_skill(bot, None, [-1,cid,uid])	
	
def command_lose_leaf(bot, update, args):
	#log.info(args)
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	game, player = get_base_data2(cid, uid)
	if game is None:
		return
	if "Campero" in args[0]:
		player.vida_explorador_campero  -=2;
		after_command(bot, cid)
	if "Brujula" in args[0]:
		player.vida_explorador_brujula  -=2;
		after_command(bot, cid)
	if "Hoja" in args[0]:
		player.vida_explorador_hoja  -=1;
		after_command(bot, cid)
	if args[0] == "Usar carta skill":
		return command_use_skill(bot, None, [-1,cid,uid])	
	
def command_lose_explorer(bot, update, args):
	try:
		cid, uid = update.message.chat_id, update.message.from_user.id
	except Exception as e:
		cid, uid = args[1], args[2]
	game, player = get_base_data2(cid, uid)
	if game is None:
		return
	if "Campero" in args[0]:
		player.vida_explorador_campero  = 0;
		after_command(bot, cid)
	if "Brujula" in args[0]:
		player.vida_explorador_brujula  = 0;
		after_command(bot, cid)
	if "Hoja" in args[0]:
		player.vida_explorador_hoja  = 0;
		after_command(bot, cid)

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
		
def command_prueba(bot, update, args):
	#log.info(update.message.from_user.id)
	#log.info(update.message.chat_id)
	uid = update.message.from_user.id
	if uid in ADMIN:
		cid = '-1001206290323'
		#update.message.chat_id
		game = get_game(cid)
		if not game:
			bot.send_message(cid, "No hay juego creado en este chat")
			return
		cartas_juego_actual =  random.sample([*cartas_aventura], len([*cartas_aventura]))		
		cartas_mañana = []		
		for i in range(6):
			cartas_mañana.append(cartas_juego_actual.pop(0))				
		cartas_mañana.sort()
		showImages(bot, cid, cartas_mañana)		

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
    bot.send_message(cid,"Bot para multiples juegos. Preguntar al ADMIN por los juegos disponibles")
    #command_help(bot, update)


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
		log.info("Searching Game in DB")
		query = "select * from games where id = %s;"
		cur.execute(query, [cid])
		dbdata = cur.fetchone()
		if cur.rowcount > 0:
			log.info('Updating Game')
			gamejson = jsonpickle.encode(game)
			#log.info(gamejson)
			#query = "UPDATE games SET groupName = %s, data = %s WHERE id = %s RETURNING data;"
			query = "UPDATE games SET groupName = %s, tipojuego = %s, data = %s WHERE id = %s;"
			cur.execute(query, (groupName, gameType, gamejson, cid))
			#log.info(cur.fetchone()[0])
			conn.commit()		
		else:
			log.info('Saving Game in DB')
			gamejson = jsonpickle.encode(game)
			#log.info(gamejson)
			query = "INSERT INTO games(id, groupName, tipojuego, data) VALUES (%s, %s, %s, %s) RETURNING data;"
			#query = "INSERT INTO games(id , groupName  , data) VALUES (%s, %s, %s) RETURNING data;"
			cur.execute(query, (cid, groupName, gameType, gamejson))
			#log.info(cur.fetchone()[0])
			conn.commit()
	except Exception as e:
		bot.send_message(cid, 'No se grabo debido al siguiente error: '+str(e))

def load_game(cid):
	cur = conn.cursor()			
	log.info("Searching Game in DB")
	query = "SELECT * FROM games WHERE id = %s;"
	cur.execute(query, [cid])
	dbdata = cur.fetchone()

	if cur.rowcount > 0:
		log.info("Game Found")
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
	sleep(3)
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
				# Inicio el juego con los valores iniciales, el chat en que se va a jugar, el iniciador y el nombre del chat
				GamesController.games[cid] = Game(cid, update.message.from_user.id, groupName)				
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
	log.info('callback_choose_posible_role called: %s' % callback.data)	
	regex = re.search("(-[0-9]*)\*choosegame\*(.*)\*([0-9]*)", callback.data)
	cid, strcid, opcion, uid, struid = int(regex.group(1)), regex.group(1), regex.group(2), int(regex.group(3)), regex.group(3)
	bot.edit_message_text("Has elegido el juego: %s" % opcion, cid, callback.message.message_id)
		
	game = get_game(cid)
	game.tipo = opcion
	
	modulos_disponibles_juego = MODULOS_DISPONIBES[opcion]
	
	# Si hay solo un modo de juego, lo pongo. Sino pregunto cual se quiere jugar
	if len(modulos_disponibles_juego) == 1:	
		game.modo = next(iter(modulos_disponibles_juego))
		bot.send_message(cid, "Solo hay un modulo y se pone ese %s" % game.modo)
		bot.send_message(cid, "Cada jugador puede unirse al juego con el comando /join.\nEl iniciador del juego (o el administrador) pueden unirse tambien y escribir /startgame cuando todos se hayan unido al juego!")
		save(bot, game.cid)
	else:
		frase_regex = "choosemode"
		pregunta_arriba_botones = "¿Qué modo de juego quieres jugar?"
		chat_donde_se_pregunta = cid
		multipurpose_choose_buttons(bot, cid, uid, chat_donde_se_pregunta, frase_regex, pregunta_arriba_botones, modulos_disponibles_juego)
	
def callback_choose_mode(bot, update):
	callback = update.callback_query
	log.info('callback_choose_posible_role called: %s' % callback.data)	
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
				player = Player(fname, uid)
				game.add_player(uid, player)
				log.info("%s (%d) joined a game in %d" % (fname, uid, game.cid))
	
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
		player = Player(fname, uid)
		try:
			max_jugadores = MODULOS_DISPONIBES[game.tipo][game.modo]["max_jugadores"]
			min_jugadores = MODULOS_DISPONIBES[game.tipo][game.modo]["min_jugadores"]
			
			# Si se ha alcanzado el maximo de jugadores no te puedes unir.
			if len(game.playerlist) == max_jugadores:
				bot.send_message(game.cid, "Se ha alcanzado previamente el maximo de jugadores. Espera el proximo juego!")
			else:
				# Uno al jugador a la partida
				game.add_player(uid, player)				
				save(bot, game.cid)
				
				# Si se ha alcanzado el minimo o superado
				if len(game.playerlist) >= min_jugadores:
					bot.send_message(game.cid, fname + " se ha unido al juego. Hay %s/%s jugadores.\nPueden poner /startgame para comenzar" % (str(len(game.playerlist)), max_jugadores))
				else:
					bot.send_message(game.cid, fname + " se ha unido al juego. Todavia no se ha llegado al minimo de jugadores. Faltan: %s " % (str(min_jugadores - len(game.playerlist))))			
		except Exception:
			bot.send_message(game.cid,
				fname + ", I can\'t send you a private message. Please go to @MultiGamesByLevibot and click \"Start\".\nYou then need to send /join again.")

def command_startgame(bot, update):
	log.info('command_startgame called')
	groupName = update.message.chat.title
	cid = update.message.chat_id
	game = get_game(cid)
	if not game:
		bot.send_message(cid, "There is no game in this chat. Create a new game with /newgame")
	#elif game.board:
	#	bot.send_message(cid, "The game is already running!")
	elif update.message.from_user.id != game.initiator and bot.getChatMember(cid, update.message.from_user.id).status not in ("administrator", "creator"):
		bot.send_message(game.cid, "Solo el creador del juego o un admin puede iniciar con /startgame")	
	else:
		
		# Verifico si la configuracion ha terminado y se han unido los jugadores necesarios		
		min_jugadores = MODULOS_DISPONIBES[game.tipo][game.modo]["min_jugadores"]
		
		if len(game.playerlist) >= min_jugadores:
			save(bot, game.cid)
			MainController.init_game(bot, game)
		else:
			bot.send_message(game.cid, "Falta el numero mínimo de jugadores. Faltan: %s " % (str(min_jugadores - len(game.playerlist))))
			
def command_roll(bot, update, args):	
	if args:
		text_tirada = '¡Tu tirada de ' + ' '.join(args)
	else:
		text_tirada = '¡Tu tirada'
	
	cid = update.message.chat_id
	uid = update.message.from_user.id
	
	tirada = random.randint(1,101)	
	if tirada > 97:
		tirada2 = random.randint(1,101)
		text_tirada +=  ' es *%s!*' % (str(tirada+tirada2))
	elif tirada < 4:
		tirada2 = random.randint(1,101)
		text_tirada +=  ' es *%s!*' % (str(tirada-tirada2))
	elif tirada == 27:
		text_tirada +=  ' es *Épico*!' % (str(tirada+tirada2))		
	else:
		text_tirada +=  ' es *%s!*' % (str(tirada))
		
	bot.send_message(cid, "%s" % (text_tirada), ParseMode.MARKDOWN)
	
	# Si hay un juego creado guardo en el historial
	game = get_game(cid)
	if game and uid in game.playerlist:
		player = game.playerlist[uid]
		texthistory = "Jugador *%s* - %s" % (player.name, text_tirada)
		game.history.append("%s" % (texthistory))

def command_clue(bot, update, args):
	try:		
		#Send message of executing command   
		cid = update.message.chat_id
		uid = update.message.from_user.id

		# Busco en que juegos esta el jugador y agrego el historia oculto en los que este. (Futuro se
		for game_key, game in GamesController.games.items():
			#Solamente si el jugador esta en el partido y 
			if uid in game.playerlist:
				#Check if there is a current game
				# TODO VErificar que no mande pista el jugador activo
				if True:
					if len(args) > 0:
						#Data is being claimed
						# TODO Verificar que el usuario no mande pistas con espacios.
						claimtext = ' '.join(args)
						#claimtexttohistory = "El jugador %s declara: %s" % (game.playerlist[uid].name, claimtext)
						bot.send_message(uid, "Tu pista: %s fue agregada a las pistas." % (claimtext))
						game.board.state.last_votes[uid] = answer
						
						# Verifico si todos los jugadores -1 pusieron pista
						if len(game.board.state.last_votes) == len(game.player_sequence)-1:
							MainController.review_clues(bot, game)
					else:					
						bot.send_message(uid, "Debes mandar un mensaje para hacer una declaración.")

				else:
					bot.send_message(uid, "No puedes hacer claim oculto sin promulgar al menos una política.")
			else:
				bot.send_message(uid, "No puedes hacer claim oculto si no estas en algun partido.")				
	except Exception as e:
		bot.send_message(uid, str(e))
		log.error("Unknown error: " + str(e))
	
	
	
