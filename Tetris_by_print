import numpy as np
import sys
import random as rd
import select
import time as t

class Tetromino:
    TETRO_TYPES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
    WEIGHTS     = [0.1, 0.1, 0.15, 0.15, 0.15, 0.2, 0.15]

    # 각 미노별 4가지 회전 상태 정의 (y, x)
    ROTATION_SHAPES = {
        'S': [np.array([[0, -1], [0, 0], [0, 1], [0, 2]]), np.array([[-1, 0], [0, 0], [1, 0], [2, 0]]), np.array([[0, -2], [0, -1], [0, 0], [0, 1]]), np.array([[-2, 0], [-1, 0], [0, 0], [1, 0]])],
        'Z': [np.array([[-1, -1], [0, -1], [0, 0], [0, 1]]), np.array([[-1, 1], [-1, 0], [0, 0], [1, 0]]), np.array([[0, -1], [0, 0], [0, 1], [1, 1]]), np.array([[-1, 0], [0, 0], [1, 0], [1, -1]])],
        'L': [np.array([[0, -1], [0, 0], [0, 1], [-1, 1]]), np.array([[-1, 0], [0, 0], [1, 0], [1, 1]]), np.array([[1, -1], [0, -1], [0, 0], [0, 1]]), np.array([[-1, -1], [-1, 0], [0, 0], [1, 0]])],
        'O': [np.array([[-1, -1], [-1, 0], [0, -1], [0, 0]])],
        'I': [np.array([[0, -1], [0, 0], [0, 1], [0, 2]]), np.array([[-1, 0], [0, 0], [1, 0], [2, 0]]), np.array([[0, -2], [0, -1], [0, 0], [0, 1]]), np.array([[-2, 0], [-1, 0], [0, 0], [1, 0]])],
        'J': [np.array([[0, -1], [0, 0], [0, 1], [-1, -1]]), np.array([[-1, 0], [0, 0], [1, 0], [-1, 1]]), np.array([[0, -1], [0, 0], [0, 1], [1, 1]]), np.array([[-1, 0], [0, 0], [1, 0], [1, -1]])],
        'T': [np.array([[-1, -1], [-1, 0], [0, 0], [0, 1]]), np.array([[-1, 1], [0, 1], [0, 0], [1, 0]]), np.array([[0, -1], [0, 0], [1, 0], [1, 1]]), np.array([[-1, 0], [0, 0], [0, -1], [1, -1]])]
    }

    # J, L, S, T, Z용 Kick Data (표 기반 변환: +Y -> -dy)
    SRS_KICK_DATA = {
        (0, 1): np.array([[0, 0], [0, -1], [-1, -1], [2, 0], [2, -1]]),
        (1, 0): np.array([[0, 0], [0, 1], [1, 1], [-2, 0], [-2, 1]]),
        (1, 2): np.array([[0, 0], [0, 1], [1, 1], [-2, 0], [-2, 1]]),
        (2, 1): np.array([[0, 0], [0, -1], [-1, -1], [2, 0], [2, -1]]),
        (2, 3): np.array([[0, 0], [0, 1], [-1, 1], [2, 0], [2, 1]]),
        (3, 2): np.array([[0, 0], [0, -1], [1, -1], [-2, 0], [-2, -1]]),
        (3, 0): np.array([[0, 0], [0, -1], [1, -1], [-2, 0], [-2, -1]]),
        (0, 3): np.array([[0, 0], [0, 1], [-1, 1], [2, 0], [2, 1]])
    }

    # I 미노용 Kick Data
    SRS_KICK_DATA_I = {
        (0, 1): np.array([[0, 0], [0, -2], [0, 1], [1, -2], [-2, 1]]),
        (1, 0): np.array([[0, 0], [0, 2], [0, -1], [-1, 2], [2, -1]]),
        (1, 2): np.array([[0, 0], [0, -1], [0, 2], [-2, -1], [1, 2]]),
        (2, 1): np.array([[0, 0], [0, 1], [0, -2], [2, 1], [-1, -2]]),
        (2, 3): np.array([[0, 0], [0, 2], [0, -1], [-1, 2], [2, -1]]),
        (3, 2): np.array([[0, 0], [0, -2], [0, 1], [1, -2], [-2, 1]]),
        (3, 0): np.array([[0, 0], [0, 1], [0, -2], [2, 1], [-1, -2]]),
        (0, 3): np.array([[0, 0], [0, -1], [0, 2], [-2, -1], [1, 2]])
    }

    def __init__(self, units):
        self.tetro_type = self.choose_type()
        self.rotation_offsets = Tetromino.ROTATION_SHAPES[self.tetro_type]  # <This is a constant set of offsets that is determined by tetro_type> !
        self.rotation_cycle = len(self.rotation_offsets)
        self.rotated = 0
        self.offset = self.rotation_offsets[self.rotated] # <This is a variable of a offset that changes when moving, rotating> !
        self.anchor_point = np.array([1, 4])
        self.units = units
        self.current_coords = self.offset + self.anchor_point
        self.update_display_first()


    @classmethod
    def choose_type(cls):
        return rd.choices(cls.TETRO_TYPES, cls.WEIGHTS, k=1)[0]


    def update_display_first(self):
        for y, x in self.current_coords:
            self.units[y][x].display_type = 'T'


    def move_down(self):
        self.anchor_point += [1, 0]


    def lock(self):
        for y, x in self.current_coords:
            self.units[y][x].filled = True


    def update_display(self):
        for y, x in self.current_coords:
            self.units[int(y)][int(x)].display_type = 'B'
        self.current_coords = self.offset + self.anchor_point
        for y, x in self.current_coords:
            self.units[int(y)][int(x)].display_type = 'T'


    def is_collied(self, coords_list, dy=0, dx=0):
        for y, x in coords_list:
            ny, nx = int(y + dy), int(x + dx)
            if ny < 0 or ny > 16: return 3 # 바닥/천장 충돌
            if nx < 0 or nx > 9: return 1  # 벽 충돌
            if self.units[ny][nx].filled: return 2 # 블록 충돌
        return False


    def rotate_tetro(self, direction):
        if self.tetro_type == 'O': return False
        
        next_rotated = (self.rotated + direction) % self.rotation_cycle
        next_offsets = self.rotation_offsets[next_rotated]
         
        kick_set = Tetromino.SRS_KICK_DATA_I if self.tetro_type == 'I' else Tetromino.SRS_KICK_DATA
        try_offsets = kick_set.get((self.rotated, next_rotated))
        
        if try_offsets is not None:
            # try_offsets의 첫 번째인 [0, 0]이 바로 "기본 회전" 테스트임
            for dy, dx in try_offsets:
                if not self.is_collied(next_offsets + self.anchor_point, dy, dx):
                    self.anchor_point += [dy, dx]
                    self.rotated = next_rotated
                    self.offset = next_offsets
                    return True
        return False




class GameBoard:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.units = []


    def generate_map(self):
        self.units = [[BlockUnit() for _ in range(10)] for _ in range(17)]


    def check_full_row(self):
        rows_to_clear = [i for i, row in enumerate(self.units) if all(u.filled for u in row)]
        for i in rows_to_clear:
            self.clear_row(i)
            self.drag_down_grid(i)
            self.score += 100


    def clear_row(self, row_index):
        for unit in self.units[row_index]:
            unit.display_type = 'B'
            unit.filled = False


    def drag_down_grid(self, row_index):
        self.units.pop(row_index)
        self.units.insert(0, [BlockUnit() for _ in range(10)])
    

    # def save_tetro(self, )





class BlockUnit:
    def __init__(self):
        self.display_type = 'B'
        self.filled = False




class ScreenManager:
    DISPLAY_CHARS = {'T': '■', 'B': '□'}


    @classmethod
    def reset_screen(cls, units, score, level):
        print("\033[2J\033[H", end='', flush=True)
        print("═" * 22)
        for row in units:
            print("║", end='')
            print(" ".join(cls.DISPLAY_CHARS.get(u.display_type, '□') for u in row), end='')
            print("║")
        print("═" * 22)
        print(f"Score: {score} | Level: {level}")
        print("A:Left S:Down D:Right Q:CCW E:CW Space:HardDrop X:Quit")


def get_input_async():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1).lower()
    return None




# --- Main Game Loop ---
GB = GameBoard()
GB.generate_map()
current_tetro = Tetromino(GB.units)
change_happened = True
harddropped = False
drop_timer = 0.0
fix_timer = 0.0
drop_interval = 0.8
running = True

try:
    while running:
        t.sleep(0.05)
        drop_timer += 0.05
        
        # 하강 로직
        if drop_timer >= drop_interval:
            if not current_tetro.is_collied(current_tetro.current_coords, 1, 0):
                current_tetro.move_down()
                change_happened = True
            drop_timer = 0.0

        key = get_input_async()
        if key:
            if key == 'a':
                if not current_tetro.is_collied(current_tetro.current_coords, 0, -1):
                    current_tetro.anchor_point -= [0, 1]
                    change_happened = True

            elif key == 'd':
                if not current_tetro.is_collied(current_tetro.current_coords, 0, 1):
                    current_tetro.anchor_point += [0, 1]
                    change_happened = True

            elif key == 's':
                if not current_tetro.is_collied(current_tetro.current_coords, 1, 0):
                    current_tetro.move_down()
                    change_happened = True
                    drop_timer = 0.0

            elif key == 'e':
                if current_tetro.rotate_tetro(1): change_happened = True

            elif key == 'q':
                if current_tetro.rotate_tetro(-1): change_happened = True

            elif key == ' ':
                while not current_tetro.is_collied(current_tetro.current_coords, 1, 0):
                    current_tetro.move_down()
                    current_tetro.update_display()
                harddropped = True

            elif key == 'x':
                running = False


        if change_happened: 
            current_tetro.update_display()
            ScreenManager.reset_screen(GB.units, GB.score, GB.level)
            change_happened = False



        # 바닥에 닿았을 때 고정 로직
        if current_tetro.is_collied(current_tetro.current_coords, 1, 0):
            fix_timer += 0.05
            if fix_timer >= 0.5 or harddropped:
                current_tetro.lock()
                GB.check_full_row()
                current_tetro = Tetromino(GB.units)
                fix_timer = 0.0
                harddropped = False
                change_happened = True
        else:
            fix_timer = 0.0

except KeyboardInterrupt:
    print("\nQuit")
    sys.exit(0)
