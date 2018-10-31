from Constants.Cards import playerSets
from Constants.Cards import policies
import random
from Boardgamebox.State import State

class Board(object):
    def __init__(self, playercount, game):
        self.state = State()
        self.num_players = playercount
        self.fascist_track_actions = playerSets[self.num_players]["track"]
        self.policies = random.sample(policies, len(policies))        
        self.discards = []
        self.previous = []        
        # LostExpedition
        self.cartasAventura = []
   
    def print_board(self, player_list):
        board = "--- Posesión actual ---\n"
        
        for uid in player_list:
            board += "%s tiene " % (player_list[uid].name)
            for i in range(player_list[uid].tokens_posesion):
                board += "\U0001F47F"            
            board += "\n"            
        return board
