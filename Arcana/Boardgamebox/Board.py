from Constants.Cards import cartas_aventura

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ForceReply

from Arcana.Boardgamebox.State import State
from Boardgamebox.Board import Board as BaseBoard

from Arcana.Constants.Cards import FATETOKENS, ARCANACARDS

class Board(BaseBoard):
	def __init__(self, playercount, game):
		BaseBoard.__init__(self, playercount, game)
		self.arcanaCards = random.sample(ARCANACARDS[:], len(ARCANACARDS))
		self.fateTokens = random.sample(FATETOKENS[:], len(FATETOKENS))
		self.fateTokensDiscard = []
		# Se seteara en difficultad el doom inicial
		self.state = State()
		
	def draw_fate_token(self):
		if len(self.fateTokens) == 0:
			# Si esta vacio agrego pongo los del descarte
			self.fateTokens = random.sample(self.fateTokensDiscard, len(self.fateTokensDiscard))
			self.fateTokensDiscard = []
		return self.fateTokens.pop()
	
	def print_board(self, bot, game):
		bot.send_message(game.cid, "--- *Estado de Partida* ---\n", parse_mode=ParseMode.MARKDOWN)
		btns = []
		btns.append([self.create_arcana_button(game.cid, game.board.state.topArcana)])
		btnMarkup = InlineKeyboardMarkup(btns)
		bot.send_message(game.cid, "*Arcana de arriba del mazo:*", parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup)
		board = "*Arcanas Activas*:\n"
		btns = []
		for arcana_on_table in game.board.state.arcanasOnTable:
			btns.append([self.create_arcana_button(game.cid, arcana_on_table)])
		btnMarkup = InlineKeyboardMarkup(btns)
		bot.send_message(game.cid, "*Arcanas Activas*:", parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup)
		'''
		board = ""
		board += "--- *Estado de Partida* ---\n"
		board += "Arcana de arriba del mazo:\n{0}".format(self.print_arcana_front(self.state.topArcana))
		board += "\n"
		board += "*Arcanas Activas*:\n"
		for arcana_on_table in self.state.arcanasOnTable:
			board += "{0}".format(self.print_arcana_front(arcana_on_table))
		
		board += "\n"
		board += "--- *Orden de jugadores* ---\n"
		for player in game.player_sequence:
			nombre = player.name.replace("_", " ")
			if self.state.active_player == player:
				board += "*{}*".format(nombre) + " " + u"\u27A1\uFE0F" + " "
			else:
				board += "{}".format(nombre) + " " + u"\u27A1\uFE0F" + " "
		board = board[:-3]
		board += u"\U0001F501"

		board += "\n\nEl jugador *{0}* es el jugador activo".format(game.board.state.active_player.name)
		
		return board
		'''
	
	def create_arcana_button(self, cid, arcana, tokens = []):
		titulo = arcana["Título"]	
		texto = arcana["Texto"]
		lunas = arcana["Lunas"]
		#if len(tokens) > 0:
		titulo += " ({}/{})".format(len(tokens), lunas)
		
		txtBoton = "{}".format(titulo)
		comando_callback = "txtArcanaAR"
		uid = cid # Solo se va a usar para mostrar en pantallas de juego
		datos = str(cid) + "*" + comando_callback + "*" + str(titulo) + "*" + str(uid)
		return InlineKeyboardButton(txtBoton, callback_data=datos)

	def print_arcana_front(self, arcana):
		return "*{}*\n{}\nCantidad de lunas: {}\n".format(arcana["Título"], arcana["Texto"], arcana["Lunas"])
	
	def print_arcana_back(self, arcana):
		return "*{}*\n{}\n".format(arcana["Título reverso"], arcana["Texto reverso"])
	def print_puntaje(self, game):		
		board += "--- *Puntaje de jugadores* ---\n"
		for player in game.player_sequence:
			nombre = player.name.replace("_", " ")
			board += "*{} ({})*\n".format(nombre, player.puntaje)
		return board
