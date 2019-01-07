from Boardgamebox.Player import Player as BasePlayer
from Arcana.Constants.Cards import PLAYERFATETOKENS

class Player(BasePlayer):
	def __init__(self, name, uid):		
		BasePlayer.__init__(self, name, uid)		
		# Lost Expedition atributes
		self.playerFateTokens = PLAYERFATETOKENS[:]
		self.hiddenPlayerFateTokens = []

	def print_stats(self):
		board = "--- Stats Jugador %s ---\n" % self.name
		board += "--- %s 🍲 ---\n" % self.food
		
		return board
