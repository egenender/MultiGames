from Constants.Cards import cartas_aventura

import random
from Boardgamebox.State import State
from Boardgamebox.Board import Board as BaseBoard

from Arcana.Constants.Cards import FATETOKENS, ARCANACARDS

class Board(BaseBoard):
	def __init__(self, playercount, game):
		BaseBoard.__init__(self, playercount, game)
		self.arcanaCards = random.sample(ARCANACARDS[:], len(ARCANACARDS))
		self.fateTokens = random.sample(FATETOKENS[:], len(FATETOKENS))
		# Se seteara en difficultad el doom inicial
		self.state.doom = None
		self.state.score = 0
		
	def print_board(self, game):
		board = ""
		board += "--- *Estado de Partida* ---\n"
		board += "Cartas restantes: *{0}*\n".format(len(game.board.cartas))
		board += "Frase actual: *{0}*".format(game.board.state.acciones_carta_actual)
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
		if len( game.board.cartas) == 0:
			board += "\n\n‼️Esta es la ultima carta del mazo‼️"
		
		return board
	
	def print_puntaje(self, game):		
		board += "--- *Puntaje de jugadores* ---\n"
		for player in game.player_sequence:
			nombre = player.name.replace("_", " ")
			board += "*{} ({})*\n".format(nombre, player.puntaje)
		return board
