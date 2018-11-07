from Constants.Cards import cartas_aventura

import random
from Boardgamebox.State import State

class Board(object):
    def __init__(self, playercount, game):
        self.state = State()
        self.num_players = playercount
        #Lost Expedition
        self.cartasAventura = random.sample([*cartas_aventura], len([*cartas_aventura]))
        self.cartasExplorationActual = []
        # Cantidad de veces que se mezclo el mazo.
        self.amount_shuffled = 0
        # Se comienza en el primer lugar
        self.progreso = 1
        self.objetivoprogreso = 9
        
        self.discards = []
        self.previous = []        
        
        
   
    def print_board(self, player_list):
        board = "--- Posesión actual ---\n"
        
        for uid in player_list:
            board += "%s tiene " % (player_list[uid].name)
            for i in range(player_list[uid].tokens_posesion):
                board += "\U0001F47F"            
            board += "\n"            
        return board
