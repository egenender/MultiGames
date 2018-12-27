import json
from datetime import datetime
from random import shuffle

from Boardgamebox.Game import Game as BaseGame
#from Boardgamebox.Player import Player
#from Boardgamebox.Board import Board
#from Boardgamebox.State import State

class Game(BaseGame):
	def __init__(self, cid, initiator, groupName, tipo = None, modo = None):
		BaseGame.__init__(self, cid, initiator, groupName, tipo = None, modo = None)		

	def add_player(self, uid, player):
		self.playerlist[uid] = player
