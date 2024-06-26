""" Class file containing necessary functionality for the Tetris piece assets within the game """

SHAPE_LOOKUP = {"S": ([['.....',
                       '.....',
                       '..00.',
                       '.00..',
                       '.....'],
                      ['.....',
                       '..0..',
                       '..00.',
                       '...0.',
                       '.....']], (0, 255, 0)),
                "Z": ([['.....',
                       '.....',
                       '.00..',
                       '..00.',
                       '.....'],
                      ['.....',
                       '..0..',
                       '.00..',
                       '.0...',
                       '.....']], (255, 0, 0)), 
                "I": ([['.....',
                       '..0..',
                       '..0..',
                       '..0..',
                       '..0..'],
                      ['.....',
                       '0000.',
                       '.....',
                       '.....',
                       '.....']], (0, 255, 255)),
                "O": ([['.....',
                       '.....',
                       '.00..',
                       '.00..',
                       '.....']], (255, 255, 0)),
                "J": ([['.....',
                       '.0...',
                       '.000.',
                       '.....',
                       '.....'],
                      ['.....',
                       '..00.',
                       '..0..',
                       '..0..',
                       '.....'],
                      ['.....',
                       '.....',
                       '.000.',
                       '...0.',
                       '.....'],
                      ['.....',
                       '..0..',
                       '..0..',
                       '.00..',
                       '.....']], (255, 165, 0)),
                "L": ([['.....',
                       '...0.',
                       '.000.',
                       '.....',
                       '.....'],
                      ['.....',
                       '..0..',
                       '..0..',
                       '..00.',
                       '.....'],
                      ['.....',
                       '.....',
                       '.000.',
                       '.0...',
                       '.....'],
                      ['.....',
                       '.00..',
                       '..0..',
                       '..0..',
                       '.....']], (0, 0, 255)),
                "T": ([['.....',
                       '..0..',
                       '.000.',
                       '.....',
                       '.....'],
                      ['.....',
                       '..0..',
                       '..00.',
                       '..0..',
                       '.....'],
                      ['.....',
                       '.....',
                       '.000.',
                       '..0..',
                       '.....'],
                      ['.....',
                       '..0..',
                       '.00..',
                       '..0..',
                       '.....']], (128, 0, 128))}


class Piece(object):
    def __init__(self, shape: str):
       self.shape = SHAPE_LOOKUP[shape][0]
       self.colour = SHAPE_LOOKUP[shape][1]

       shape_start_pos = {'S': (5, 2), 'Z': (5, 2), 'I': (5, 3), 'O': (5, 2), 'J': (5, 3), 'L': (5, 3), 'T': (5, 3)}

       self.x = shape_start_pos[shape][0]
       self.y = shape_start_pos[shape][1]
       self.rotation = 0
