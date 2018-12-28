import json
from datetime import datetime
from random import shuffle

from Boardgamebox.Game import Game as BaseGame
from SayAnything.Boardgamebox.Player import Player
from SayAnything.Boardgamebox.Board import Board
#from Boardgamebox.Board import Board
#from Boardgamebox.State import State

class Game(BaseGame):
	def __init__(self, cid, initiator, groupName, tipo = None, modo = None):
		BaseGame.__init__(self, cid, initiator, groupName, tipo, modo)		
	
	# Creacion de player de Say Anything.
	def add_player(self, uid, name):
		self.playerlist[uid] = Player(uid, name)
	def create_board(self):
		player_number = len(game.playerlist)
		self.board = Board(player_number, self)
