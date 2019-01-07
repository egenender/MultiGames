from Boardgamebox.Player import Player as BasePlayer
from Arcana.Constants.Cards import PLAYERFATETOKENS

class Player(BasePlayer):
	def __init__(self, name, uid):		
		BasePlayer.__init__(self, name, uid)		
		# Tokens que el jugador modificara cuando el resto de jugadores le diga. Marca que posible Fate tiene en mano
		self.playerFateTokens = PLAYERFATETOKENS[:]
		self.hiddenPlayerFateTokens = []
		# Fate Tokens que tiene el jugador en mano
		self.fateTokens = []

	def print(self):
		board = "--- Stats Jugador {} ---\n".format(self.name)
		board += "--- Tokens Visibles ---\n"
		for fateToken in self.playerFateTokens:
			board += "{0}({1}) ".format(fateToken["Texto"], fateToken["TimeSymbols"])
		board = board[:-1]
		return board
