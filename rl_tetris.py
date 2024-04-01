""" File containing functionality to run the Tetris game """
import pygame

import numpy as np

from tetris import Tetris
from agent import TetrisAgent

EPISODES = 25


if __name__ == '__main__':	
	episode = 0
	while episode < EPISODES:
		tetris = Tetris()
		player = TetrisAgent()
		player.summary()

		window = pygame.display.set_mode((tetris.window_width, tetris.window_height))
		pygame.display.set_caption('Tetris')
		
		locked_positions = {}
		tetris.create_grid(locked_positions)
		
		change_piece = False 
		run = True
		current_piece = tetris.get_shape()
		next_piece = tetris.get_shape()
		clock = pygame.time.Clock()
		fall_time = 0
		fall_speed = 0.35
		level_time = 0
		score = 0
		high_score = tetris.get_max_score()

		while run:
			# Create new grid with updated locked positions
			grid = tetris.create_grid(locked_positions)
			state_space = player.process_state_space(piece_position=tetris.convert_shape_format(current_piece), grid=grid)

			fall_time += clock.get_rawtime()
			level_time += clock.get_rawtime()

			clock.tick()

			# Increase difficulty every 10 seconds
			if level_time / 1000 > 5:
				level_time = 0
				# Until fall speed exceeds 0.15
				if fall_speed > 0.15:
					fall_speed -= 0.005

			action = player.epsilon_greedy_selection(state_space=state_space.reshape(1, -1))
			if action == 0:
				current_piece.x -= 1
				if not tetris.valid_space(current_piece, grid):
					current_piece.x += 1
			elif action == 1:
				current_piece.x += 1
				if not tetris.valid_space(current_piece, grid):
					current_piece.x -= 1
			elif action == 2:
				current_piece.y += 1
				if not tetris.valid_space(current_piece, grid):
					current_piece.y -= 1
			elif action == 3:
				current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
				if not tetris.valid_space(current_piece, grid):
					current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

			if fall_time / 1000 > fall_speed:
				fall_time = 0
				current_piece.y += 1
				if not tetris.valid_space(current_piece, grid) and current_piece.y > 0:
					current_piece.y -= 1
					change_piece = True

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False 
					pygame.display.quit()
					quit()

			piece_position = tetris.convert_shape_format(current_piece)

			for i in range(len(piece_position)):
				x, y = piece_position[i]
				if y >= 0:
					grid[y][x] = current_piece.colour 

			if change_piece:
				for position in piece_position:
					p = (position[0], position[1])
					locked_positions[p] = current_piece.colour

				current_piece = next_piece
				next_piece = tetris.get_shape()
				change_piece = False
				rows_cleared = tetris.clear_rows(grid, locked_positions)
				score += rows_cleared * 10
				tetris.update_score(score)

				if high_score < score:
					high_score = score
			
				reward = player.reward_function(rows_cleared=rows_cleared)

			else:
				reward = player.reward_function(rows_cleared=0)

			tetris.draw_window(window, grid, score, high_score)
			tetris.draw_next_shape(next_piece, window)
			pygame.display.update()

			if tetris.check_loss(locked_positions):
				run = False
				reward = player.reward_function(rows_cleared=0, terminal=True)
				state_space_prime = state_space
			else:
				state_space_prime = player.process_state_space(piece_position=piece_position, grid=grid)
			player.update_replay_buffer(state_space=state_space, action=action, reward=reward, state_space_prime=state_space_prime, terminal_state=not run)

		tetris.draw_text_middle("Game Over", 40, (255, 255, 255), window)
		pygame.display.update()
		pygame.time.delay(2000)
		pygame.quit()

		player.train(mini_batch_size=1000, epochs=1)
		episode += 1
