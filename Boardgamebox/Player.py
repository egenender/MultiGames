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
