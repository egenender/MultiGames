__author__ = "Eduardo Peluffo"
from PIL import Image
from io import BytesIO

class helper:	
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
	
	def next_player_after_active_player(game):
		if game.board.state.player_counter < len(game.player_sequence) - 1:
			return game.board.state.player_counter +1
		else:
			return 0
	def increment_player_counter(game):
		if game.board.state.player_counter < len(game.player_sequence) - 1:
			game.board.state.player_counter += 1
		else:
			game.board.state.player_counter = 0
	
	def showImages(bot, cid, cartas, img_caption = ""):
		images = []
		for carta in cartas:
			images.append(get_img_carta(carta))

		widths, heights = zip(*(i.size for i in images))

		total_width = sum(widths)
		max_height = max(heights)

		new_im = Image.new('RGB', (total_width, max_height))

		x_offset = 0
		for im in images:
			new_im.paste(im, (x_offset,0))
			x_offset += im.size[0]

		bio = BytesIO()
		bio.name = 'image.jpeg'
		new_im.save(bio, 'JPEG')
		bio.seek(0)
		bot.send_photo(cid, photo=bio, caption=img_caption)
	
	def get_img_carta(num_carta, url_imagen, fila, columna):
		# Para cartas en imagenes de 3X3
		carta = cartas_aventura[num_carta]
		fila, columna = carta["fila"], carta["columna"]	
		url_img = url_imagen		
		img = Image.open(url_img)
		width, height = img.size
		widthCarta, heightCarta = width/3, height/3
		# Este switch se hace para corresponder al llamado del metodo, sino tendria que haber sido columna, fila.
		columna, fila = int(fila), int(columna)
		#log.info(img.size)
		x, y = (fila*widthCarta), (columna*heightCarta)
		#log.info(x)
		#log.info(y)
		left, top, right, bottom = x, y, widthCarta+x, heightCarta+y
		cropped = img.crop( ( left, top, right, bottom ) )
		return cropped
	
	
	
