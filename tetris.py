""" Class file contianing necessary functionality for the Tetris board grid """
import pygame
import random

from piece import Piece


class Tetris:
	def __init__(self):
		self.columns = 10
		self.rows = 20

		self.shapes = ['S', 'Z', 'I', 'O', 'J', 'L', 'T']

		self.window_width = 800
		self.window_height = 750

		self.game_width = 300
		self.game_height = 600

		self.block_size = 30

		self.grid_top_left_x = (self.window_width - self.game_width) // 2
		self.grid_top_left_y = self.window_height - self.game_height - 50


	def create_grid(self, locked_pos: dict = {}) -> list[list[tuple]]:
		grid = [[(0, 0, 0)] * self.columns for _ in range(self.rows)]
		
		# Define locked positions of pieces as a dictionary of {(x, y): (R, G, B)}
		for row in range(self.rows):
			for col in range(self.columns):
			# If the cell in (row, column) contains a locked piece, fetch the colour and apply it to the respective grid cell
				if (col, row) in locked_pos:
					colour = locked_pos[(col, row)] 
					grid[row][col] = colour
		return grid

	@staticmethod
	def convert_shape_format(piece: Piece) -> list[tuple]:
		positions = []

		# Fetch the corresponding piece format and desired rotation
		shape_format = piece.shape[piece.rotation % len(piece.shape)]

		# For each row of the shape format
		for i, row in enumerate(shape_format):
			# Split the string into list of characters
			row = list(row)
			for j, column in enumerate(row):
				if column == '0':
					positions.append((piece.x + j, piece.y + i))

		# Required accomodation for offset in piece shape format definition
		for i, pos in enumerate(positions):
			positions[i] = (pos[0]-2, pos[1]-4)
		return positions

	def valid_space(self, piece: Piece, grid: list[list[tuple]]) -> bool:
		# Make a 2D list of all valid locations on the board that do not contain locked pieces 
		accepted_positions = [[(x, y) for x in range(self.columns) if grid[y][x] == (0, 0, 0)] for y in range(self.rows)]

		# Flatten and parse accepted positions and remove "sub-lists"
		accepted_positions = [x for item in accepted_positions for x in item]

		formatted_shape = self.convert_shape_format(piece)

		for position in formatted_shape:
			if position not in accepted_positions:
				if position[1] >= 0:
					return False
		return True

	@staticmethod
	def check_loss(positions: list[tuple]):
		for position in positions:
			_, y = position
			if y < 1:
				return True
		return False

	def get_shape(self):
		return Piece(random.choice(self.shapes))

	def draw_text_middle(self, text: str, size: int, colour: str, surface: pygame.display):
		font = pygame.font.Font('./arcade.TTF', size) # , bold=False, italic=True)
		label = font.render(text, 1, colour)

		surface.blit(label, (self.grid_top_left_x + (self.game_width / 2) - (label.get_width() / 2), self.grid_top_left_y + (self.game_height / 2) - (label.get_height() / 2)))

	def draw_grid(self, surface: pygame.display):
		r = g = b = 0
		grid_colour = (r, g, b)

		for i in range(self.rows):
			pygame.draw.line(surface, grid_colour, (self.grid_top_left_x, self.grid_top_left_y + i * self.block_size), (self.grid_top_left_x + self.game_width, self.grid_top_left_y + i * self.block_size))
			for j in range(self.columns):
				pygame.draw.line(surface, grid_colour, (self.grid_top_left_x + j * self.block_size, self.grid_top_left_y), (self.grid_top_left_x + j * self.block_size, self.grid_top_left_y + self.game_height))

	@staticmethod
	def clear_rows(grid: list[list[tuple]], locked: dict) -> int:
		increment = 0
		for i in range(len(grid)-1, -1, -1):
			grid_row = grid[i]
			if (0, 0, 0) not in grid_row:
				increment += 1

				index = i
				for j in range(len(grid_row)):
					try:
						del locked[(j, i)]
					except ValueError:
						continue

		if increment > 0:
			for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
				x, y = key
				if y < index:
					new_key = (x, y + increment)
					locked[new_key] = locked.pop(key)
		return increment

	def draw_next_shape(self, piece: Piece, surface: pygame.display):
		font = pygame.font.Font('./arcade.TTF', 30)
		label = font.render("Next Shape", 1, (255, 255, 255))

		start_x = self.grid_top_left_x + self.game_width + 50
		start_y = self.grid_top_left_y + ((self.game_height / 2) - 100)

		shape_format = piece.shape[piece.rotation % len(piece.shape)]

		for i, row in enumerate(shape_format):
			row = list(row)
			for j, column in enumerate(row):
				if column == '0':
					pygame.draw.rect(surface, piece.colour, (start_x + j * self.block_size, start_y + i * self.block_size, self.block_size, self.block_size), 0)

		surface.blit(label, (start_x, start_y - 30))
		# pygame.display.update()

	def draw_window(self, surface, grid: list[list[tuple]], score: int = 0, last_score: int = 0):
		surface.fill((0, 0, 0))

		pygame.font.init()
		font = pygame.font.Font('./arcade.TTF', 65)	 # , bold=True)
		label = font.render("TETRIS", 1, (255, 255, 255))

		surface.blit(label, ((self.grid_top_left_x + (self.game_width / 2)) - (label.get_width() / 2), 30))

		font = pygame.font.Font('./arcade.TTF', 30)
		label = font.render('SCORE    {}'.format(score), 1, (255, 255, 255))

		start_x = self.grid_top_left_x + self.game_width + 50
		start_y = self.grid_top_left_y + ((self.game_height / 2) - 100)

		surface.blit(label, (start_x, start_y + 200))

		label_high_score = font.render('HIGHSCORE    {}'.format(last_score), 1, (255, 255, 255))

		start_x_high = self.grid_top_left_x - 240
		start_y_high = self.grid_top_left_y + 200

		surface.blit(label_high_score, (start_x_high + 20, start_y_high + 200))

		for i in range(self.rows):
			for j in range(self.columns):
				pygame.draw.rect(surface, grid[i][j], (self.grid_top_left_x + j * self.block_size, self.grid_top_left_y + i * self.block_size, self.block_size, self.block_size), 0)

		self.draw_grid(surface)

		border_colour = (255, 255, 255)
		pygame.draw.rect(surface, border_colour, (self.grid_top_left_x, self.grid_top_left_y, self.game_width, self.game_height), 4)

		# pygame.display.update()

	@staticmethod
	def get_max_score(filepath: str = './highscore.txt') -> int:
		with open(filepath, 'r') as file:
			lines = file.readlines()
			score = int(lines[0].strip())
			return score

	def update_score(self, new_score: int, filepath: str = './highscore.txt'):
		score = self.get_max_score()

		with open(filepath, 'w') as file:   
			if new_score > score:
				file.write(str(new_score))
			else: 
				file.write(str(score))


