# -*- coding: UTF-8 -*-
import random
import sys
import pygame as pg
import numpy as np

pg.init()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.Font(None, 32)

class InputBox(object):
    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        # Re-render the text.
        self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(60, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)
        self.update()


class Button(object):
    def __init__(self, x, y, size=(10,20), text=''):
        self.rect = pg.Rect(x, y, size[0], size[1])
        self.text = text
        self.txt_surface = FONT.render(text, True, (0,0,0))
        self.pressed = False

    def handle_event(self,event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the button
            if self.rect.collidepoint(event.pos):
                self.pressed = True

    def draw(self,screen):
        pg.draw.rect(screen, (0, 0, 240), (self.rect.x, self.rect.y,
                                           self.rect.width,
                                           self.rect.height))
        screen.blit(self.txt_surface, (self.rect.x + 15, self.rect.y + 15))

class StartScreen(object):
    def __init__(self,size):
        self.screen = pg.display.set_mode((size[0], size[1]))
        pg.display.set_caption('Instructions')
        input_box1 = InputBox(80, 300, 60, 32)
        input_box2 = InputBox(310, 300, 60, 32)
        input_box3 = InputBox(550, 300, 60, 32)
        self.button1 = Button(530, 400, (135,50), 'Start')
        self.input_boxes = [input_box1, input_box2, input_box3]
        self.done = True
        self.errorMessage = ''
        self.errState = False
        self.args = []

    def message_to_screen(self,msg,x,y, color=(255,255,255), size=32):
        FONT_INS = pg.font.Font(None, size)
        txt_surface = FONT_INS.render(msg, False, color)
        self.screen.blit(txt_surface, (x, y))

    def draw(self):
        self.screen.fill((0,0,0))
        # Write instruction messages
        msg = 'Press ESC or close the window to end game'
        self.message_to_screen(msg, 60, 20)
        msg = '___'*30
        self.message_to_screen(msg, 0, 35, (30,200,30))
        msg = '*FPS: Time in miliseconds the take the screen to refresh'
        self.message_to_screen(msg, 40, 80, size=27)
        msg = '*Population: Percentage of initial population'
        self.message_to_screen(msg, 40, 120, size=27)
        msg = '*Resolution: Size in pixel of each individual'
        self.message_to_screen(msg, 40, 160, size=27)
        msg = 'FPS: '
        self.message_to_screen(msg, 35, 308, size=25)
        msg = 'Population:               %'
        self.message_to_screen(msg, 215, 308, size=25)
        msg = 'Resolution: '
        self.message_to_screen(msg, 450, 308, size=25)

        # Write error message
        self.message_to_screen(self.errorMessage, 20, 220, (250,50,20), size=40)
        if self.errState:
            self.errState = False

        # Draw buttons and input boxes
        self.button1.draw(self.screen)
        for box in self.input_boxes:
            box.draw(self.screen)

    def handle_event(self,event):
        if event.type == pg.QUIT:
            sys.exit()
        if event.type == pg.KEYDOWN:
            self.errorMessage = ''
            if event.key == pg.K_ESCAPE:
                sys.exit()
        for box in self.input_boxes:
            box.handle_event(event)
        self.button1.handle_event(event)

        if self.button1.pressed:
            for box in self.input_boxes:
                try:
                    x = float(box.text)
                    if x < 0:
                        self.errorMessage = 'ERROR: Please enter positive ' \
                                            'numbers'
                        self.errState = True
                    else:
                        self.args.append(x)
                except ValueError as e:
                    self.errState = True
                    self.errorMessage = 'ERROR: One or more arguments is ' \
                                        'not a number'
            if not self.errState:
                self.done = False
            else:
                self.args = []
                for box in self.input_boxes:
                    box.text = ''
                self.button1.pressed = False

class GameScreen(object):
    def __init__(self,size, res, p):
        self.screen = pg.display.set_mode(size)
        pg.display.set_caption("Conway's Game of Life")
        self.cols = int(size[0] / res)
        self.rows = int(size[1] / res)
        self.res = res
        self.board = np.ndarray((self.cols, self.rows))
        self.next = np.ndarray((self.cols, self.rows))

        for i in range(self.cols):
            for j in range(self.rows):
                if random.random() > 1 - p:
                    self.board[i][j] = 1.0
                else:
                    self.board[i][j] = 0.0

    def handle_event(self, event):
        if event.type == pg.QUIT:
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                sys.exit()

    def countNeighbors(self,x,y):
        neigh = 0
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == j == 0:
                    neigh += 0
                elif (x + i) < 0 or (y + j) < 0:
                    neigh += 0
                else:
                    try:
                        neigh += self.board[x + i][y + j]
                    except IndexError:
                        neigh += 0
        return neigh

    def draw(self):
        for i in range(self.cols):
            for j in range(self.rows):

                if self.board[i][j] == 1.0:
                    color = WHITE
                else:
                    color = BLACK

                area = (i * self.res, j * self.res, self.res - 1, self.res - 1)
                pg.draw.rect(self.screen, color, area, 0)
        pg.display.update()

    def update(self):
        for i in range(self.cols):
            for j in range(self.rows):
                neighbors = self.countNeighbors(i,j)
                state = self.board[i][j]
                if state == 0.0 and neighbors == 3:
                    self.next[i][j] = 1.0
                elif state == 1.0 and (neighbors < 2 or neighbors > 3):
                    self.next[i][j] = 0.0
                else:
                    self.next[i][j] = state
        self.board = self.next.copy()

def startScreen():
    clock = pg.time.Clock()
    start_screen = StartScreen((700,480))
    while start_screen.done:
        for event in pg.event.get():
            start_screen.handle_event(event)
        start_screen.draw()
        pg.display.flip()
        clock.tick(30)
    args = start_screen.args
    return args

def gameScreen(t, p, res):
    clock = pg.time.Clock()
    game_screen = GameScreen((1300,700), res, p)
    while True:
        for event in pg.event.get():
            game_screen.handle_event(event)

        game_screen.draw()
        game_screen.update()

        if t == 0:
            pass
        else:
            clock.tick(1000./float(t))

def main():
    t, p, res = startScreen()
    p = p/100
    gameScreen(t, p, res)

if __name__ == '__main__':
    main()
    pg.quit()
