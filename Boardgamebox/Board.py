from Constants.Cards import cartas_aventura

import random
from Boardgamebox.State import State

class Board(object):
    def __init__(self, playercount, game):
        self.state = State()
        self.num_players = playercount
        #Lost Expedition        
        if game.tipo == "LostExpedition":
            self.cartasAventura = random.sample([*cartas_aventura], len([*cartas_aventura]))
            self.cartasExplorationActual = []
        # Cantidad de veces que se mezclo el mazo.
        self.amount_shuffled = 0
        # Se comienza en el primer lugar
        self.progreso = 1
        self.objetivoprogreso = 9
        
        self.cartas = []
        '''                
        self.exploradores_team1 = {
            "Campero" : {
                "vida" : "3", #Comandos con indicaciones pediran al usuario que actuen y luego volvera a la lista de comandos
                "habilidad" : "Campero",
                "matable" : True,                
            },
            "Brujula" : {
                "vida" : "3", #Comandos con indicaciones pediran al usuario que actuen y luego volvera a la lista de comandos
                "habilidad" : "Brujula",
                "matable" : True,                
            },
            "Hoja" : {
                "vida" : "3", #Comandos con indicaciones pediran al usuario que actuen y luego volvera a la lista de comandos
                "habilidad" : "Hoja",
                "matable" : True,                
            }
        }
        
        self.exploradores_team2 = {
            "Campero" : {
                "vida" : "3", #Comandos con indicaciones pediran al usuario que actuen y luego volvera a la lista de comandos
                "habilidad" : "Campero",
                "matable" : True,                
            },
            "Brujula" : {
                "vida" : "3", #Comandos con indicaciones pediran al usuario que actuen y luego volvera a la lista de comandos
                "habilidad" : "Brujula",
                "matable" : True,                
            },
            "Hoja" : {
                "vida" : "3", #Comandos con indicaciones pediran al usuario que actuen y luego volvera a la lista de comandos
                "habilidad" : "Hoja",
                "matable" : True,                
            }
        }
        '''
        
        self.discards = []
        self.previous = []        
        
        
   
    def print_board(self, player_sequence):
        board = "--- Orden de jugadores ---\n"
        for player in player_sequence:
            nombre = player.name.replace("_", " ")
            board += nombre + " " + u"\u27A1\uFE0F" + " "          
        return board
