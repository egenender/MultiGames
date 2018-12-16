__author__ = "Eduardo Peluffo"

# Remueve repetidos y devuelve ambas listas
def remove_same_elements_dict(last_votes):
	last_votes_to_lower = {key:val.lower() for key, val in last_votes.items()}	
	repeated_keys = []
	valores_last_votes_to_lower = list(last_votes_to_lower.values())#last_votes_to_lower.values()
	for key, value in last_votes_to_lower.items():
		if valores_last_votes_to_lower.count(value) > 1:
			repeated_keys.append(key)	
	return {key:val for key, val in last_votes.items() if key not in repeated_keys}, {key:val for key, val in last_votes.items() if key in repeated_keys}

def player_call(player):
	return "[{0}](tg://user?id={1})".format(player.name, player.uid)
