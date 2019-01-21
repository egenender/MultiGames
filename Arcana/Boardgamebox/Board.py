from Constants.Cards import cartas_aventura

import copy
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ForceReply

from Arcana.Boardgamebox.State import State
from Boardgamebox.Board import Board as BaseBoard

from Arcana.Constants.Cards import FATETOKENS, ARCANACARDS

class Board(BaseBoard):
	def __init__(self, playercount, game):
		BaseBoard.__init__(self, playercount, game)
		self.arcanaCards = random.sample(copy.deepcopy(ARCANACARDS), len(ARCANACARDS))
		self.fateTokens = random.sample(copy.deepcopy(FATETOKENS), len(FATETOKENS))
		self.fateTokensDiscard = []
		# Se seteara en difficultad el doom inicial
		self.state = State()
		
	def draw_fate_token(self):
		
		if len(self.fateTokens) == 0:
			# Si esta vacio agrego pongo los del descarte
			self.fateTokens = random.sample(self.fateTokensDiscard, len(self.fateTokensDiscard))
			self.fateTokensDiscard = []
		random.shuffle(self.fateTokens)
		return self.fateTokens.pop()
	
	def print_board(self, bot, game):
		bot.send_message(game.cid, "--- *Estado de Partida* ---\nCondena: {}/7.\nPuntaje {}/7"
				 .format(self.state.doom, self.state.score), parse_mode=ParseMode.MARKDOWN, timeout=20)
		btns = []
		btns.append([self.create_arcana_button(game.cid, self.arcanaCards[len(self.arcanaCards)-1])])
		btnMarkup = InlineKeyboardMarkup(btns)
		bot.send_message(game.cid, "*Arcana de arriba del mazo:*", parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup, timeout=20)
		board = "*Arcanas Activas*:\n"
		btns = []
		i = 0
		for arcana_on_table in game.board.state.arcanasOnTable:
			btns.append([self.create_arcana_button(game.cid, arcana_on_table, i)])
			i += 1
		btnMarkup = InlineKeyboardMarkup(btns)
		bot.send_message(game.cid, "*Arcanas Activas*:", parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup, timeout=20)
		
		if len(game.board.state.fadedarcanasOnTable) > 0:
			btns = []
			i = 0
			for arcana_on_table in game.board.state.fadedarcanasOnTable:
				btns.append([self.create_arcana_button(game.cid, arcana_on_table, -2)])
				i += 1
			btnMarkup = InlineKeyboardMarkup(btns)
			bot.send_message(game.cid, "*Arcanas desvanecidas* para usar /remove N:", parse_mode=ParseMode.MARKDOWN, reply_markup=btnMarkup, timeout=20)
		
		board = ""		
		board += "--- *Orden de jugadores* ---\n"
		for player in game.player_sequence:			
			if self.state.active_player == player:
				nombre += "*{}({})*".format(player.name.replace("_", " "), len(player.fateTokens))
			else:
				nombre += "{}({})".format(player.name.replace("_", " "), len(player.fateTokens))
			board += "{}".format(nombre) + " " + u"\u27A1\uFE0F" + " "
		board = board[:-3]
		board += u"\U0001F501"
		board += "\n\nEl jugador *{0}* es el jugador activo".format(game.board.state.active_player.name)		
		bot.send_message(game.cid, board, parse_mode=ParseMode.MARKDOWN, timeout=20)
		
	
	def create_arcana_button(self, cid, arcana, index = '-1', comando_callback = 'txtArcanaAR'):
		if 'tokens' not in arcana:
			arcana['tokens'] = []
		
		faded = "faded" in arcana and arcana["faded"]
		
		tokens = arcana['tokens']	
		lunas = arcana["Lunas"]		
		if faded:
			texto = arcana["Texto reverso"]
			titulo = arcana["Título reverso"]
		else:
			texto = arcana["Texto"]
			titulo = arcana["Título"]
			
		#if len(tokens) > 0:
		txt_tokens = ""
		if len(arcana['tokens']) > 0:
			for fate in arcana['tokens']:
				txt_tokens += "{}, ".format(fate["Texto"])
			txt_tokens = "[{}]".format(txt_tokens[:-2])
		tokens_lunas = "" if (titulo == "Las horas" or faded) else "({}/{})".format(self.count_fate_tokens(arcana), lunas) 
		txtBoton = "{} {} {}".format(titulo, txt_tokens, tokens_lunas)
		comando_callback = comando_callback
		uid = cid # Solo se va a usar para mostrar en pantallas de juego
		datos = str(cid) + "*" + comando_callback + "*" + str(titulo) + "*" + str(index)
		return InlineKeyboardButton(txtBoton, callback_data=datos)

	def print_arcana_front(self, arcana):
		return "*{}*\n{}\nCantidad de lunas: {}\n".format(arcana["Título"], arcana["Texto"], arcana["Lunas"])
	
	def print_arcana_back(self, arcana):
		return "*{}*\n{}\n".format(arcana["Título reverso"], arcana["Texto reverso"])
	
	def print_result(self, game):		
		resultado = ""
		if game.board.state.score > 6:
			resultado = "Han ganado!"
		else:
			resultado = "Han perdido!"
		return resultado
	def count_fate_tokens(self, arcana):
		i = 0
		for fate in arcana['tokens']:
			i += int(fate["TimeSymbols"])
		return i
