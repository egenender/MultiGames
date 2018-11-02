class Player(object):
    def __init__(self, name, uid):
        self.name = name
        self.uid = uid
        self.role = None
        self.party = None
        self.is_dead = False
        self.inspected_players = {} 
        self.tokens_posesion = 0
        self.poseido = False
        # Lost Expedition atributes
        self.hand = []
        self.food = 3
        self.bullets = 3
        self.vida_explorador_campero = 3
        self.vida_explorador_brujula = 3
        self.vida_explorador_hoja = 3
    
    def print_stats(self):
        board = "--- Stats Actuales ---\n"
        board += "--- Comida %s ---\n" % self.food
        board += "--- Balas %s ---\n" % self.bullets
        board += "--- Explorador Campero %s ❤️ ---\n" % self.vida_explorador_campero
        board += "--- Explorador Brujula %s ❤️ ---\n" % self.vida_explorador_brujula
        board += "--- Explorador Hoja %s ❤️ ---\n" % self.vida_explorador_hoja
        
        '''for uid in player_list:
            board += "%s tiene " % (player_list[uid].name)
            for i in range(player_list[uid].tokens_posesion):
                board += "\U0001F47F"            
            board += "\n"  
        '''
        return board
