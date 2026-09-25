import numpy as np
import sys
import random as rd
import time as t
import pygame as pyg

class Tetromino:
    TETRO_TYPES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
    WEIGHTS     = [0.1, 0.1, 0.15, 0.15, 0.15, 0.2, 0.15]

    # 각 미노별 4가지 회전 상태 정의 (y, x)
    ROTATION_SHAPES = {
        'S': [np.array([[0, -1], [0, 0], [-1, 0], [-1, 1]]), np.array([[-1, 0], [0, 0], [0, 1], [1, 1]]), np.array([[1, -1], [1, 0], [0, 0], [0, 1]]), np.array([[-1, -1], [0, -1], [0, 0], [1, 0]])],
        'Z': [np.array([[-1, -1], [-1, 0], [0, 0], [0, 1]]), np.array([[-1, 1], [0, 1], [0, 0], [1, 0]]), np.array([[0, -1], [0, 0], [1, 0], [1, 1]]), np.array([[-1, 0], [0, 0], [0, -1], [1, -1]])],
        'L': [np.array([[0, -1], [0, 0], [0, 1], [-1, 1]]), np.array([[-1, 0], [0, 0], [1, 0], [1, 1]]), np.array([[1, -1], [0, -1], [0, 0], [0, 1]]), np.array([[-1, -1], [-1, 0], [0, 0], [1, 0]])],
        'O': [np.array([[-1, -1], [-1, 0], [0, -1], [0, 0]])],
        'I': [np.array([[0, -1], [0, 0], [0, 1], [0, 2]]), np.array([[-1, 0], [0, 0], [1, 0], [2, 0]]), np.array([[0, -2], [0, -1], [0, 0], [0, 1]]), np.array([[-2, 0], [-1, 0], [0, 0], [1, 0]])],
        'J': [np.array([[0, -1], [0, 0], [0, 1], [-1, -1]]), np.array([[-1, 0], [0, 0], [1, 0], [-1, 1]]), np.array([[0, -1], [0, 0], [0, 1], [1, 1]]), np.array([[-1, 0], [0, 0], [1, 0], [1, -1]])],
        'T': [np.array([[0, -1], [0, 0], [0, 1], [-1, 0]]), np.array([[-1, 0], [0, 0], [0, 1], [1, 0]]), np.array([[0, -1], [0, 0], [0, 1], [1, 0]]), np.array([[-1, 0], [0, 0], [0, -1], [1, 0]])]
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

    def __init__(self, units, anchor_point, tetro_type=None):
        if tetro_type is None:
            self.tetro_type = GameBoard.get_next_type()
        self.tetro_type = tetro_type
        self.rotation_offsets = Tetromino.ROTATION_SHAPES[self.tetro_type]  # <This is a constant set of offsets that is determined by tetro_type> !
        self.rotation_cycle = len(self.rotation_offsets)
        self.rotated = 0
        self.offset = self.rotation_offsets[self.rotated] # <This is a variable of a offset that changes when moving, rotating> !
        self.anchor_point = anchor_point
        self.units = units
        self.current_coords = self.offset + self.anchor_point
        self.update_display_first()



    def clear_display(self):
        for y, x in self.current_coords:
            self.units[int(y)][int(x)].display_type = 'B'


    def update_display_first(self):
        for y, x in self.current_coords:
            self.units[y][x].display_type = self.tetro_type


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
            self.units[int(y)][int(x)].display_type = self.tetro_type


    def is_collied(self, coords_list, dy=0, dx=0):
        for y, x in coords_list:
            ny, nx = int(y + dy), int(x + dx)
            if ny < 0: return 1             # 바닥 충돌
            if ny > 17: return 2            # 천장 충돌
            if nx < 0 or nx > 9: return 3   # 세로벽 충돌
            if self.units[ny][nx].filled: return 4 # 블록 충돌
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
#   PIXEL_COORDS = [(X, Y) FOR Y in range(18) for X in range(10)]
#   기존에 Blockunit 마다 좌표를 속성값으로 가지게 했지만, 이중 리스트인 units 의 인덱스 값으로 대체하기로 결정.
#   이때 unit는 Blockunit 10개를 한 묶음으로 하는 리스트를 원소로 가지는 구조상, 좌표값이 x, y가 아닌 y, x 가 되게된다. <유의바람>


    def __init__(self):
        self.score = 0
        self.highscore = 0
        self.level = 1
        self.units = []
        self.next_tetro_queue = []    #10개 미리 뽑아 놓기
        self.hold_type = None
        self.next_type = self.get_next_type()


    def load_high_score(self):
        #scores.txt 파일에서 최고 점수 하나를 읽어옴
        with open("scores.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                self.highscore = 0
                return
            # 파일에 저장된 점수들 중 가장 큰 값을 반환 (숫자로 변환)
            scores = [int(line.strip()) for line in lines if line.strip().isdigit()]
            self.highscore = max(scores) if scores else 0
            print(self.highscore)
            return


    def get_next_type(self):
        if self.next_tetro_queue == []:
            self.next_tetro_queue = rd.sample(Tetromino.TETRO_TYPES, 7)
        print(self.next_tetro_queue)
        return self.next_tetro_queue.pop(0)



    def save_score(self):
        #게임 종료 시 현재 점수를 파일에 기록하고 최고 점수 갱신
        # 1. 파일 끝에 현재 점수 추가 (a 모드)
        with open("scores.txt", "a", encoding="utf-8") as f:
            f.write(f"{self.score}\n")


    def generate_map(self):
        row_units = []
        for _ in range(18):
            for _ in range(10):
                row_units.append(BlockUnit())
            self.units.append(row_units)
            row_units = []


    def check_full_row(self):
        rows_to_clear = [i for i, row in enumerate(self.units) if all(u.filled for u in row)][::-1]  # Clear from bottom to top
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


    def get_ghost_positions(self, current_tetro):           #고스트 블럭의 좌표를 계산하는 코드
        max_dy = 0
        while not current_tetro.is_collied(current_tetro.current_coords, max_dy+1, 0):
            max_dy += 1
        ghost_coords = [[y + dy, x] for y, x in current_tetro.current_coords for dy in range(1, max_dy+1)]
        return ghost_coords



    def spawn_tetro(self, tetro_type=None, anchor_point=None):
        if anchor_point is None:
            anchor_point = np.array([1, 4])

        if tetro_type is None:
            tetro_type = self.next_type
            self.next_type = self.get_next_type()
        return Tetromino(self.units, anchor_point, tetro_type)
    

# 위 함수의 anchor_point, tetro_type 디폴트 인자를 왜 저렇게 해놨나 싶다면 필독
# 파이썬은 함수의 정의 시점에 정의된 디폴트 인자의 메모리 주소가 정의 후에도 삭제되지 않는다 사용한다.
# 이때 불변 객체, 가변 객체라는 것이 있는데 불변은 상수, 문자열 같은 값이고 가변 인자는 리스트, 딕셔너리 등 대부분의 값이다
# 불변 객체는 값 변동시 메모리 주소도 변경이 되지만,
# 가변 객체는 값 변동시 메모리 주소가 변하지 않는다
# 이때 가변 객체인 어레이를 디폴트 인자로 넣어버리면, 함수 내부에서 값이 변경된 후
# 다음번 함수 호출 시에도 그 변경된 값이 디폴트 인자로 들어가게 된다
# 즉 함수는 매번 리콜이 되지만, 함수 사용시 인풋값을 직접 넣어주지 않으면 변경된 디폴트 인자의 값은 매번 유지되는 ㅈㄴ 어이없는 일이 생긴다
# 따라서 가변 인자는 ㅅㅂ 절대 디폴트에 넣지 말고 함수 내부에 따로 빼서 변경하는 위의 형식이 효과적이며 실제 관용형식이라고 한다.




    def swap_tetro(self, old_type):   # 반환값은 새로 갱신될 테트로 객체의 테트로 타입
        if self.hold_type is None:
            self.hold_type = old_type
            now_type = self.next_type
            self.next_type = self.get_next_type()
        else:
            now_type = self.hold_type  # 예전 hold 타입 먼저 저장
            self.hold_type = old_type  # 현재 테트로를 hold에 저장
        return now_type
#변수명 설명
# hold_type: 해당 함수가 종료되고 hold 칸에 있을 타입
# next_type: 해당 함수가 종료되고 게임판에 next_tetro 로 띄워질 타입
# old_type: 해당 함수의 인풋값으로 들어온, 즉 삭제될 테트로 타입
# now_type: 해당 함수가 반환할, 즉 갱신되어 생성될 테트로 타입

# 구조 설명
# 여기선 next, hold, now_type 데이터 조작만 해놓는다
# 화면 상단에 띄워지는 건 screen class 에서 조작한다.
# 이 함수의 반환값으로 current_tetro 객체를 새 Tetromino 객체로 업데이트한다
# 이 때 anchor_point 값은 구 테트로의 데이터를 계승하며, 테트로 모양이 달라 벽과 충돌 가능성이 있으므로 생성 직후 SRS Test 를 실행해야 한다.


    def is_gameover(self, current_tetro):
        for y, x in current_tetro.current_coords:
            if current_tetro.units[y+1][x].filled:
                self.save_score()
                return True






class ScreenManager:
    screen = pyg.display.set_mode((480, 540))# 기본화면, 필요시 참조하여 변경


    @classmethod
    def reset_screen(cls):                  #화면을 검게 칠해서 깔끔하게  reset하는 함수
        cls.screen.fill((0, 0, 0))


    @classmethod
    def draw_board(cls, units):             #Tetro가 떨어지는 board를 drawing 함수
        for y, row in enumerate(units):
            for x, unit in enumerate(row):
                cls.screen.blit(BlockUnit.TYPE_IMAGES[unit.display_type], (x * 30 + 180, y * 30))


    @classmethod
    def draw_hold_panel(cls, hold_type):       #Hold 된 테트로를 보여주는 함수
            for y in range(0, 120, 30):
                for x in range(0, 120, 30):
                    cls.screen.blit(BlockUnit.TYPE_IMAGES['B'], (x, y))

            if hold_type is not None:
                for y, x in Tetromino.ROTATION_SHAPES[hold_type][0]:
                    cls.screen.blit(BlockUnit.TYPE_IMAGES[hold_type], ((x+1) * 30, (y+1) * 30))


    @classmethod
    def draw_ghost_block(cls, ghost_block_coords):
        for y, x in ghost_block_coords:
            cls.screen.blit(BlockUnit.TYPE_IMAGES['G'], (x * 30 + 180, y * 30))
    

    @classmethod
    def draw_tetromino(cls, current_tetro):
        for y, x in current_tetro.current_coords:
            cls.screen.blit(BlockUnit.TYPE_IMAGES[current_tetro.tetro_type], (x * 30 + 180, y * 30))


    @classmethod
    def show_gameover_screen(cls, game_board):
        cls.reset_screen()

        title_font = pyg.font.SysFont(None, 72)
        stat_font = pyg.font.SysFont(None, 36)

        title_surf = title_font.render('GAMEOVER', True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(cls.screen.get_width() // 2, cls.screen.get_height() // 2 - 80))
        cls.screen.blit(title_surf, title_rect)

        stats = [
            ('LEVEL', game_board.level),
            ('SCORE', game_board.score),
            ('HIGHSCORE', game_board.highscore),
        ]

        for i, (label, value) in enumerate(stats):
            text = stat_font.render(f'{label}: {value}', True, (255, 255, 255))
            rect = text.get_rect(center=(cls.screen.get_width() // 2, cls.screen.get_height() // 2 + 30 + i * 40))
            cls.screen.blit(text, rect)

        pyg.display.flip()


    @classmethod
    def render_all(cls, units, hold_type, current_tetro, ghost_block_coords=None):
        cls.reset_screen()
        cls.draw_board(units)
        if ghost_block_coords is not None:
            cls.draw_ghost_block(ghost_block_coords)
        cls.draw_tetromino(current_tetro)
        cls.draw_hold_panel(hold_type)
        pyg.display.flip()




class BlockUnit:
    TYPE_IMAGES = { tetro_type : pyg.transform.scale( pyg.image.load(f'Block_images/{tetro_type}.png') , (30, 30))
                    for tetro_type in Tetromino.TETRO_TYPES}
    TYPE_IMAGES['B'] = pyg.transform.scale( pyg.image.load('Block_images/black_background.png') , (30, 30)) #B means a black background tile
#    white_background_image = pyg.transform.scale( pyg.image.load('Block_images/white_background.png') , (30, 30))
    TYPE_IMAGES['G'] = pyg.transform.scale(pyg.image.load('Block_images/ghost_background1.png'), (30, 30))

    def __init__(self):
        self.display_type = 'B'
        self.filled = False





# --- Main Game Loop ---
pyg.init()
GB = GameBoard()
GB.generate_map()
GB.load_high_score()
current_tetro = GB.spawn_tetro()
change_happened = True
harddropped = False
drop_timer = 0.0
fix_timer = 0.0
drop_interval = 0.8
running = True

while running:
        t.sleep(0.05)
        drop_timer += 0.05
        
        # 하강 로직
        if drop_timer >= drop_interval:
            if not current_tetro.is_collied(current_tetro.current_coords, 1, 0):
                current_tetro.move_down()
                change_happened = True
            drop_timer = 0.0


        
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False
                pyg.quit()
                sys.exit()
            if event.type == pyg.KEYDOWN:
                key = event.key
                
                if key == pyg.K_a:      #KeyLeft
                    if not current_tetro.is_collied(current_tetro.current_coords, 0, -1):
                        current_tetro.anchor_point -= [0, 1]
                        change_happened = True

                elif key == pyg.K_d:    #KeyRight
                    if not current_tetro.is_collied(current_tetro.current_coords, 0, 1):
                        current_tetro.anchor_point += [0, 1]
                        change_happened = True

                elif key == pyg.K_s:    #KeyDown
                    if not current_tetro.is_collied(current_tetro.current_coords, 1, 0):
                        current_tetro.move_down()
                        change_happened = True
                        drop_timer = 0.0

                elif key == pyg.K_e:    #Key RotateRight
                    if current_tetro.rotate_tetro(1): change_happened = True

                elif key == pyg.K_q:    #Key RotateLeft
                    if current_tetro.rotate_tetro(-1): change_happened = True

                elif key == pyg.K_SPACE:    #Key HardDrop
                    while not current_tetro.is_collied(current_tetro.current_coords, 1, 0):
                        current_tetro.move_down()
                        current_tetro.update_display()
                    harddropped = True

                elif key == pyg.K_w:    #Key Hold
                    current_tetro.clear_display()
                    new_type = GB.swap_tetro(current_tetro.tetro_type)
                    current_tetro = GB.spawn_tetro(new_type, current_tetro.anchor_point)
                    if GB.is_gameover(current_tetro) and current_tetro.anchor_point[0] <= 1:       #spawn 직후 게임 오버인지 테스트
                        current_tetro.update_display()
                        ScreenManager.render_all(GB.units, GB.hold_type, current_tetro)
                        ScreenManager.show_gameover_screen(GB)
                        running = False
                    current_tetro.update_display()
                    change_happened = True

                elif key == pyg.K_x:    #Key Exit
                    running = False


        if change_happened: 
            current_tetro.update_display()
            ghost_block_coords = GB.get_ghost_positions(current_tetro)
            ScreenManager.render_all(GB.units, GB.hold_type, current_tetro, ghost_block_coords)
            change_happened = False



        elif current_tetro.is_collied(current_tetro.current_coords, 1, 0):          #천장/바닥 테트로 등 충돌했을 경우
            fix_timer += 0.05
            if fix_timer >= 0.5 or harddropped:
                current_tetro.lock()
                GB.check_full_row()
                current_tetro = GB.spawn_tetro()
                if GB.is_gameover(current_tetro):       #spawn 직후 게임 오버인지 테스트
                    current_tetro.update_display()
                    ScreenManager.render_all(GB.units, GB.hold_type, current_tetro)
                    ScreenManager.show_gameover_screen(GB)
                    running = False
                fix_timer = 0.0
                harddropped = False
                change_happened = True
        else:
            fix_timer = 0.0
