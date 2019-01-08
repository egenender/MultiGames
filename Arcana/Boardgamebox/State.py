from Boardgamebox.State import State as BaseState

	class State(BaseState):
		BaseState.__init__(self)
		self.doom = None
		self.score = 0
		self.topArcana = None
		self.arcanasOnTable = []
