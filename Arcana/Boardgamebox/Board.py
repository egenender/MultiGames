from Constants.Cards import cartas_aventura

import random
from Arcana.Boardgamebox.State import State
from Boardgamebox.Board import Board as BaseBoard

from Arcana.Constants.Cards import FATETOKENS, ARCANACARDS

class Board(BaseBoard):
	def __init__(self, playercount, game):
		BaseBoard.__init__(self, playercount, game)
		self.arcanaCards = random.sample(ARCANACARDS[:], len(ARCANACARDS))
		self.fateTokens = random.sample(FATETOKENS[:], len(FATETOKENS))
		# Se seteara en difficultad el doom inicial
		self.state = State()
		
	def print_board(self, game):
		board = ""
		board += "--- *Estado de Partida* ---\n"
		board += "Arcana de arriba del mazo: *{0}*\n".format(print_arcana_front(self.state.topArcana))
		board += "\n\n"
		board += "*Arcanas Activas*:\n"
		for arcana_on_table in self.state.arcanasOnTable:
			board += "{0}".format(print_arcana_front(arcana_table))
		
		board += "\n\n"
		board += "--- *Orden de jugadores* ---\n"
		for player in game.player_sequence:
			nombre = player.name.replace("_", " ")
			if self.state.active_player == player:
				board += "*{} ({})*".format(nombre, player.puntaje) + " " + u"\u27A1\uFE0F" + " "
			else:
				board += "{} ({})".format(nombre, player.puntaje) + " " + u"\u27A1\uFE0F" + " "
		board = board[:-3]
		board += u"\U0001F501"

		board += "\n\nEl jugador *{0}* es el jugador activo".format(game.board.state.active_player.name)
		
		return board
	
	def print_arcana_front(arcana):
		return "*{}*\n{}\nCantidad de lunas: {}\n".format(arcana["Título"], arcana["Texto"], arcana["Lunas"])
	
	def print_arcana_back(arcana):
		return "*{}*\n{}\n".format(arcana["Título reverso"], arcana["Texto reverso"])
	def print_puntaje(self, game):		
		board += "--- *Puntaje de jugadores* ---\n"
		for player in game.player_sequence:
			nombre = player.name.replace("_", " ")
			board += "*{} ({})*\n".format(nombre, player.puntaje)
		return board
