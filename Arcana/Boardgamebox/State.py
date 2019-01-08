from Boardgamebox.State import State as BaseState

class State(BaseState):
	def __init__(self):
		BaseState.__init__(self)
		self.doom = None
		self.score = 0
		self.topArcana = None
		self.arcanasOnTable = []
