from calendar import c
import numpy as np
import pygame as pyg
import math as m
import time as t
import sys
import random as rd
import copy
#rotation kick 구현 필요
#회전 충돌 검사를 정형화할 필요성 큼
#현재 벽차기에 대한 아이디어 존재
#anchor_point, check_collision 적극 활용 권장
#check side/floor collision 을 one function merging 중

def rotate_point(point, rotation_matrix):
    y, x = point
    rotated = np.array([x, y]) @ rotation_matrix
    return np.array([rotated[1], rotated[0]])


def multiply_rows_by_matrix(shape_matrix, rotation_matrix):
    return np.array([rotate_point(point, rotation_matrix) for point in shape_matrix])


#모든 데이터는(PIXEL_POSITIONS 제외) for y for x 형식 / 행 우선, 모든 좌표는  (y, x) 형식.( units[y][x] )
class Tetromino:
    TETRO_TYPES = ['S', 'Z', 'L', 'J', 'I', 'O', 'T']
    WEIGHTS    = [0.08, 0.08, 0.15, 0.2, 0.19, 0.15, 0.15]
    # WEIGHTS    = [0, 0, 0, 0, 1, 0, 0] #debuging

    MOVING_SHAPES = [
        np.array([ [-1, -1], [-1, 0], [0, 0], [0, 1] ]),
        np.array([[0, -1], [0, 0], [-1, 0], [-1, 1] ]),
        np.array([ [-1, 0], [0, 0], [1, 0], [1, 1] ]),
        np.array([ [-1, 0], [0, 0], [1, 0], [1, -1] ]),
        np.array([ [-1, 0], [0, 0], [1, 0], [2, 0] ]),
        np.array([ [0, 0], [0, 1], [1, 0], [1, 1] ]),
        np.array([ [-1, 0], [0, -1], [0, 1], [0, 0] ]) ]
    
    ROTATION_SHAPES = []
    ROTATION_MATRIX = [
        np.array([ [0, -1], [1, 0] ]), # I
        np.array([ [1, 0], [0, 1] ]),   # O
        np.array([ [0, 1], [-1, 0] ]) ] # L, J, S, Z, T


    def __init__(self, units):
        self.tetro_type = self.choose_type()
        self.offsets = self.moving_offsets = Tetromino.MOVING_SHAPES[self.tetro_type]
        self.rotation_offsets              = Tetromino.ROTATION_SHAPES[self.tetro_type]

        if self.tetro_type == 'O':
            self.rotation_cycle = 2
            self.anchor_point = np.array([0, 4])    #테트로미노 형성 지점의 units 인덱스, 
        else:
            if self.tetro_type == 'I':
                self.rotation_cycle = 2
            else : self.rotation_cycle = 4

            self.anchor_point = np.array([1, 4])
        
        self.units = units
        self.rotated = 0

        for y, x in self.offsets + self.anchor_point:
            self.units[y][x].display_type = self.tetro_type

        self.present_absolute_coords = self.offsets + self.anchor_point
        #위 속성은, 테트로미노의 현재 절대 좌표 array(units 의 인덱스 4개)이며,
        #변경 방식은 다음과 같다:
        #테트로미노 형성 => offsets + anchor_point 으로 초기화 =>어느 방향으로든
        #이동할 때마다 anchor_point 를 변경하고, offsets 는 고정된 상태로 유지
        #이후 update_display_state() 를 통해 위 속성에 저장된 이동 전 units 들(anchor 변경 전 위치)에서
        #테트로미노를 지우고, 위 속성을 anchor 변경 후로 업데이트한 후, 그 값으로 이동한 테트로미노를 그린다. 
    
    @classmethod
    def initilaize_attr(cls):
        cls.MOVING_SHAPES     = dict(zip(cls.TETRO_TYPES, cls.MOVING_SHAPES))
        for tetro_type in cls.TETRO_TYPES:
            shape = cls.MOVING_SHAPES[tetro_type]
            if tetro_type == 'I':
                cls.ROTATION_SHAPES.append([shape] + [multiply_rows_by_matrix(shape, cls.ROTATION_MATRIX[0])])
            
            elif tetro_type == 'O':
                cls.ROTATION_SHAPES.append([shape])
            
            else:
                cls.ROTATION_SHAPES.append([shape] + [
                    multiply_rows_by_matrix(shape, np.linalg.matrix_power(cls.ROTATION_MATRIX[2], i)) for i in range(1, 4)] )
        
        cls.ROTATION_SHAPES = dict(zip(cls.TETRO_TYPES, cls.ROTATION_SHAPES))


    @classmethod
    def choose_type(cls):
        chosen_type = rd.choices(cls.TETRO_TYPES, cls.WEIGHTS, k=1)
        return chosen_type[0]


    def drag_down_tetro(self):
        self.anchor_point += [1, 0]
        print(1)
        #테트로미노를 아래로 한 칸 이동


    def is_floor_collision(self):
        for y, x in self.present_absolute_coords:
            if  y >= 17:
                return True
            elif self.units[y+1][x].filled:
                return True


    def is_valid_unit(self, dy = 0, dx = 0):
        for y, x in self.present_absolute_coords:
            if x + dx < 0 or x + dx > 9:
                return False
            elif self.units[y + dy][x + dx].filled:
                return False
        return True
    

    def can_side_move(self, dx):
        return self.is_valid_unit(dx)

    
    def can_rotation(self):
        return self.is_valid_unit()


    def fix_to_board(self):
        for y, x in self.present_absolute_coords:
            self.units[y][x].filled = True
        

    def update_display_state(self):
        for y, x in self.present_absolute_coords:
            self.units[y][x].display_type = 'B' 

        self.present_absolute_coords = self.offsets + self.anchor_point
        for y, x in self.present_absolute_coords:
            self.units[y][x].display_type = self.tetro_type


    def try_rotate_clockwise(self):
        dummy = copy.deepcopy(self)
        if dummy.tetro_type == 'O':
            return
        dummy.rotated += 1
        index = dummy.rotated % dummy.rotation_cycle
        if index == 0:
            dummy.offsets = dummy.moving_offsets
            dummy.rotated = 0
        else: dummy.offsets = dummy.rotation_offsets[index]
        dummy.present_absolute_coords = dummy.offsets + dummy.anchor_point

        if not dummy.can_rotation():
            dummy.try_SRS_KICK()
        
        else:
            self.rotated = dummy.rotated
            self.offsets = dummy.offsets
            self.present_absolute_coords = dummy.present_absolute_coords


    def try_SRS_KICK(self, GameBoard):
        for dy, dx in GameBoard.SRS_KICK_DATA:
            if self.is_valid_unit(dy, dx):





class GameBoard:
    PIXEL_POSITIONS = [(x, y) for y in range(0, 30 * 18, 30) for x in range(0, 30 * 10, 30)] #coords to blit Block image
    SRS_KICK_DATA = np.array([[0, 1], [0, -1], [1, 0], [1, 1], [1, -1]])
    
    
    def __init__(self):
        self.score = 0
        self.level =1
        self.units = [] #2d list of BlockUnit instances, made at func-generate_map


    def generate_map(self):
        row_units = []

        for position in GameBoard.PIXEL_POSITIONS:
            row_units.append( BlockUnit(position) )

            if len(row_units) == 10:
                self.units.append(row_units)
                row_units = []


    def check_full_row(self):
        for row_index, row_units in enumerate(self.units):
            if all(unit.filled for unit in row_units):
                self.clear_row(row_index)
                self.drag_down_grid(row_index)


    def clear_row(self, row_index):
        for unit in self.units[row_index]:
            unit.display_type = 'B'              #추후 점수 계산 기능 추가 필요
            unit.filled = False


    def drag_down_grid(self, row_index):
        self.units.pop(row_index)
        for row_units in self.units[:row_index]:
            for unit in row_units:
                unit.pixel_position = (unit.pixel_position[0], unit.pixel_position[1] + 30)

        self.units.insert(0, [BlockUnit(self.PIXEL_POSITIONS[i]) for i in range(10)])





class BlockUnit:
    TYPE_IMAGES = { tetro_type : pyg.transform.scale( pyg.image.load(f'Block_images/{tetro_type}.png') , (30, 30))
                    for tetro_type in Tetromino.TETRO_TYPES}
    TYPE_IMAGES['B'] = pyg.transform.scale( pyg.image.load('Block_images/black_background.png') , (30, 30)) #B means a black background tile
##    white_background_image = pyg.transform.scale( pyg.image.load('Block_images/white_background.png') , (30, 30))


    def __init__(self, pixel_position):
        self.pixel_position = pixel_position
        self.display_type = 'B'
        self.filled = False






class ScreenManager:
    screen = pyg.display.set_mode((300, 540))# 기본화면, 필요시 참조하여 변경


    @classmethod
    def reset_screen(cls, units):
        cls.screen.fill((0, 0, 0))
        for row in units:
            for unit in row:
                cls.screen.blit(BlockUnit.TYPE_IMAGES[unit.display_type], unit.pixel_position)






pyg.init()
pyg.display.set_caption("TETRIS")
Tetromino.initilaize_attr()
GB = GameBoard()
GB.generate_map()
current_tetro = Tetromino(GB.units)
change_happened = False
harddropped = False

clock = pyg.time.Clock()
fall_speed = 500#(ms)
drop_interval = 0.8 #seconds
drop_timer = 0.0
fix_timer = 0.0

running = True
while running:

    dt = clock.tick(60) / 1000
    drop_timer += dt
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
                    if current_tetro.can_side_move(-1):
                        current_tetro.anchor_point -= [0, 1]
                        change_happened = True

                elif event.key == pyg.K_s:         #down movement
                    if current_tetro.is_floor_collision():
                        pass
                    else:
                        current_tetro.anchor_point += [1, 0]
                        change_happened = True
                        drop_timer = 0.0

                elif event.key == pyg.K_d:         #right movement
                    if current_tetro.can_side_move(1):
                        current_tetro.anchor_point += [0, 1]
                        change_happened = True

                elif event.key == pyg.K_KP5: #promptly drop tetromino
                    while not current_tetro.is_floor_collision():
                        current_tetro.drag_down_tetro()
                        current_tetro.update_display_state()
                    harddropped = True
                    drop_timer = 0.0

                elif event.key == pyg.K_KP6:
                    current_tetro.try_rotate_clockwise() #rotate tetromino clockwise
                    change_happened = True

    if harddropped:
        current_tetro.fix_to_board()
        GB.check_full_row()
        harddropped = False
        current_tetro = None
        current_tetro = Tetromino(GB.units)

    if current_tetro.is_floor_collision():
        if fix_timer >= 1:
            current_tetro.fix_to_board()
            GB.check_full_row()
            current_tetro = None
            current_tetro = Tetromino(GB.units)
            fix_timer = 0.0
        else:
            fix_timer += dt
        drop_timer = 0.0
    else:
        fix_timer = 0.0

 
    if change_happened:
        change_happened = False
        current_tetro.update_display_state()

    ScreenManager.reset_screen(current_tetro.units)
    pyg.display.flip()
