import json
from datetime import datetime
from random import shuffle

from Boardgamebox.Player import Player
from Boardgamebox.Board import Board
from Boardgamebox.State import State

class Game(object):
    def __init__(self, cid, initiator, groupName, tipo = None, modo = None, ):
        self.playerlist = {}
        self.player_sequence = []
        self.cid = cid
        self.board = None
        self.initiator = initiator
        self.dateinitvote = None
        self.history = []
        # Nombre del juego que se jugará LostExpedition, JustOne...
        self.tipo = tipo
        # Modo de juego solitario, coopertativo, competitivo...
        self.modo = modo
        # Nombre del grupo cuando se creo...
        self.groupName  = groupName
        # Configuraciones variadas...
        self.configs = {}
    
    def add_player(self, uid, name):
        self.playerlist[uid] = Player(uid, name)

    def get_hitler(self):
        for uid in self.playerlist:
            if self.playerlist[uid].role == "Hitler":
                return self.playerlist[uid]

    def find_player(self, name):
        for uid in self.playerlist:
            if self.playerlist[uid].name == name:
                return self.playerlist[uid]
        return None;
    
    def get_cultist(self):
        cultistas = []
        for uid in self.playerlist:
            if self.playerlist[uid].role == "Cultista":
                cultistas.append(self.playerlist[uid])
        return cultistas

    def get_poseidos(self):
        poseidos = []
        for uid in self.playerlist:
            if self.playerlist[uid].poseido:
                poseidos.append(self.playerlist[uid])
        return poseidos
    
    def shuffle_player_sequence(self):
        for uid in self.playerlist:
            self.player_sequence.append(self.playerlist[uid])
        shuffle(self.player_sequence)

    def remove_from_player_sequence(self, Player):
        for p in self.player_sequence:
            if p.uid == Player.uid:
                p.remove(Player)

    def print_roles(self):
        rtext = ""
        if self.board is None:
            #game was not started yet
            return rtext
        else:
            for p in self.playerlist:
                rtext += self.playerlist[p].name + "'s "
                if self.playerlist[p].is_dead:
                    rtext += "(dead) "
                rtext += "secret role was " + self.playerlist[p].role + "\n"
            return rtext
    def encode_all(obj):
        if isinstance(obj, Player):
            return obj.__dict__
        if isinstance(obj, Board):
            return obj.__dict__            
        return obj
    
    def jsonify(self):
        return json.dumps(self.__dict__, default= encode_all)
    
    def increment_player_counter(game):
        if game.board.state.player_counter < len(game.player_sequence) - 1:
            game.board.state.player_counter += 1
        else:
            game.board.state.player_counter = 0
