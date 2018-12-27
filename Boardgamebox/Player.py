class Player(object):
        def __init__(self, name, uid):
                self.name = name
                self.uid = uid
                
        def print_stats(self):
                board = "--- Stats Jugador %s ---\n" % self.name                
                return board
