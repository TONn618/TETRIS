import numpy as np
import pygame as pyg
import math as m
import time as t
import sys
import random as rd

#모든 데이터는 for y for x 형식 / 행 우선, 모든 좌표는  (y, x) 형식.( units[y][x] )
class Tetromino:
    TETRO_TYPES = ['S', 'Z', 'L', 'J', 'I', 'O', 'T']
    WEIGHTS    = [0.08, 0.08, 0.15, 0.15, 0.14, 0.2, 0.2]
    SHAPES = {                                 #각 테트로미노의 anchor_point
        'S' : np.array([ [0, 0], [0, 1], [1, -1], [1, 0]]),     #첫 줄 첫 블럭
        'Z' : np.array([ [0, -1], [0, 0], [1, 0], [1, 1] ]),   #첫 줄 마지막 블럭
        'L' : np.array([ [0, 0], [1, 0], [2, 0], [2, 1] ]),    #최상단 블럭
        'J' : np.array([ [0, 0], [1, 0], [2, -1], [2, 0] ]),   #최상단 블럭
        'I' : np.array([ [0, 0], [1, 0], [2, 0], [3, 0] ]),    #최상단 블럭
        'O' : np.array([ [0, 0], [1, 0], [0, 1], [1, 1] ]),   #좌측 상단 블럭
        'T' : np.array([ [0, -1], [0, 0], [0, 1], [1, 0] ]) } #첫 줄 중앙 블럭


    def __init__(self):
        self.tetro_type = self.choose_type()
        self.offsets = Tetromino.SHAPES[self.tetro_type]
        self.anchor_point = np.array([0, 4])    #테트로미노 형성 지점의 units 인덱스, 

        for y, x in self.offsets + self.anchor_point:
            BlockUnit.units[y][x].display_type = self.tetro_type
        
        self._previous_absolute_coords = self.offsets + self.anchor_point


    @classmethod
    def choose_type(cls):
        chosen_type = rd.choices(cls.TETRO_TYPES, cls.WEIGHTS, k=1)
        return chosen_type[0]


    def drag_down_tetro(self):
        self.anchor_point += [1, 0]
        #테트로미노를 아래로 한 칸 이동


    def check_floor_collision(self):
        for y, x in self._previous_absolute_coords:
            if  y >= 17:
                return True
            elif BlockUnit.units[y+1][x].filled:
                return True


    def check_side_collision(self):
        for y, x in self._previous_absolute_coords:
            if x >= 9 or BlockUnit.units[y][x+1].filled:
                return 'left'
            elif x <= 0 or BlockUnit.units[y][x-1].filled:
                return 'right'


    def fix_to_board(self):
        for y, x in self._previous_absolute_coords:
            BlockUnit.units[y][x].filled = True
        self = None
        

    def update_display_state(self):
        for y, x in self._previous_absolute_coords:
            BlockUnit.units[y][x].display_type = 'B'

        self._previous_absolute_coords = self.offsets + self.anchor_point
        for y, x in self._previous_absolute_coords:
            BlockUnit.units[y][x].display_type = self.tetro_type


##    def handle_block_drop(self):
##        if self.check_floor_collision():      #renew tetro  (del old one and create new one)
##            self.fix_tetromino()              #fix tetro image on gameboard
##            self.renew_tetro()
##
##    @staticmethod
##    def renew_tetro():
##        global current_tetro
##        current_tetro = None
##        current_tetro = Tetromino()



class BlockUnit:
    TYPE_IMAGES = { tetro_type : pyg.transform.scale( pyg.image.load(f'Block_images/{tetro_type}.png') , (30, 30))
                    for tetro_type in Tetromino.TETRO_TYPES}
    TYPE_IMAGES['B'] = pyg.transform.scale( pyg.image.load('Block_images/black_background.png') , (30, 30)) #B means a black background tile
##    white_background_image = pyg.transform.scale( pyg.image.load('Block_images/white_background.png') , (30, 30))
    PIXEL_POSITIONS = [(x, y) for y in range(0, 30 * 18, 30) for x in range(0, 30 * 10, 30)] #coords to blit Block image
    units = [] #all BlockUnit instances are in this list, and this is 2d list, made at func-genegrate_map


    def __init__(self, pixel_position):
        self.pixel_position = pixel_position
        self.display_type = 'B'
        self.filled = False



    @classmethod
    def generate_map(cls):
        ScreenManager.screen.fill((0, 0, 0))
        row_units = []

        for position in cls.PIXEL_POSITIONS:
            ScreenManager.screen.blit(cls.TYPE_IMAGES['B'], position)
            row_units.append( cls(position) )

            if len(row_units) == 10:
                cls.units.append(row_units)
                row_units = []
        pyg.display.flip()
class ScreenManager:
    screen = pyg.display.set_mode((300, 540))


    @classmethod
    def reset_screen(cls):
        cls.screen.fill((0, 0, 0))
        for row in BlockUnit.units:
            for unit in row:
                cls.screen.blit(BlockUnit.TYPE_IMAGES[unit.display_type], unit.pixel_position)




    

pyg.init()
pyg.display.set_caption("TETRIS")
BlockUnit.generate_map()
current_tetro = Tetromino()
change_happened = False
harddropped = False

clock = pyg.time.Clock()
fall_speed = 500#(ms)
drop_interval = 0.8 #seconds
drop_timer = 0.0

running = True
while running:

    drop_timer += (clock.tick(60) / 1000)
    if drop_interval - drop_timer <= 0:
        current_tetro.drag_down_tetro()
        change_happened = True
        drop_timer = 0.0


    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
            pyg.quit()
            sys.exit()


        elif event.type == pyg.KEYDOWN:
                if event.key == pyg.K_a:         #left movement
                    if current_tetro.check_side_collision() == 'left':
                        print(1)
                        continue
                    current_tetro.anchor_point -= [0, 1]
                    change_happened = True

                elif event.key == pyg.K_s:         #down movement
                    current_tetro.anchor_point += [1, 0]
                    change_happened = True
                    drop_timer = 0.0

                elif event.key == pyg.K_d:         #right movement
                    if current_tetro.check_side_collision() == 'right':
                        print(2)
                        continue
                    current_tetro.anchor_point += [0, 1]
                    change_happened = True

                elif event.key == pyg.K_RETURN: #promptly drop tetromino
                    while not current_tetro.check_floor_collision():
                        current_tetro.drag_down_tetro()
                        current_tetro.update_display_state()
                    harddropped = True
                    drop_timer = 0.0

                elif event.key == pyg.K_KP5:
                    pass                               #rotate tetromino clockwise
                    change_happened = True

    if current_tetro.check_floor_collision() or harddropped:
        harddropped = False
        current_tetro.fix_to_board()
        current_tetro = Tetromino()
 
    if change_happened:
        change_happened = False
        current_tetro.update_display_state()

    ScreenManager.reset_screen()
    pyg.display.flip()
