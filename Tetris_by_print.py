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

    def __init__(self, units, anchor_point, tetro_type=None):
        if tetro_type is None:
            tetro_type = Tetromino.choose_type()
        self.tetro_type = tetro_type
        self.rotation_offsets = Tetromino.ROTATION_SHAPES[self.tetro_type]  # <This is a constant set of offsets that is determined by tetro_type> !
        self.rotation_cycle = len(self.rotation_offsets)
        self.rotated = 0
        self.offset = self.rotation_offsets[self.rotated] # <This is a variable of a offset that changes when moving, rotating> !
        self.anchor_point = anchor_point
        self.units = units
        self.current_coords = self.offset + self.anchor_point
        self.update_display_first()


    @classmethod
    def choose_type(cls):
        return rd.choices(cls.TETRO_TYPES, cls.WEIGHTS, k=1)[0]


    def update_display_first(self):
        for y, x in self.current_coords:
            self.units[int(y)][int(x)].display_type = 'T'


    def clear_display(self):
        for y, x in self.current_coords:
            self.units[int(y)][int(x)].display_type = 'B'


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
    LINE_CLEAR_SCORES = {1 : 100, 
                         2 : 225, 
                         3 : 350, 
                         4 : 502, 
                         5 : 800}  # 1~4라인 클리어 시 추가 점수 (5라인은 T-Spin Triple 가정)
    
    COMBO_MULTIPLIERS = {0 : 1.0, 
                         1 : 2.1, 
                         2 : 3.5, 
                         3 : 4.3, 
                         4 : 7.0}  # 콤보 수에 따른 점수 배율 (0콤보는 배율 0으로 처리)


    def __init__(self):
        self.combo = 0
        self.score = 0
        self.level = 1
        self.units = []
        self.next_tetro_queue = [Tetromino.choose_type() for _ in range(11)]    #10개 미리 뽑아 놓기
        self.hold_type = None
        self.next_type = self.next_tetro_queue.pop(0)


    def generate_map(self):
        self.units = [[BlockUnit() for _ in range(10)] for _ in range(17)]

    
    def spawn_tetro(self, tetro_type=None, anchor_point=None):
        if anchor_point is None:
            anchor_point = np.array([1, 4])
        if tetro_type is None:
            tetro_type = self.next_type
            self.next_type = self.next_tetro_queue.pop(0)
            self.next_tetro_queue.append(Tetromino.choose_type())
        return Tetromino(self.units, anchor_point, tetro_type)


    def check_full_row(self):
        rows_to_clear = [i for i, row in enumerate(self.units) if all(u.filled for u in row)]
        
        if not rows_to_clear:
            self.score += GameBoard.LINE_CLEAR_SCORES.get(len(rows_to_clear), 0) * GameBoard.COMBO_MULTIPLIERS.get(self.combo, 1.0)
            self.combo = 0


        else:
            self.score += GameBoard.LINE_CLEAR_SCORES[len(rows_to_clear)]
            for i in rows_to_clear:
                self.clear_row(i)
                self.drag_down_grid(i)



    def clear_row(self, row_index):
        for unit in self.units[row_index]:
            unit.display_type = 'B'
            unit.filled = False


    def drag_down_grid(self, row_index):
        self.units.pop(row_index)
        self.units.insert(0, [BlockUnit() for _ in range(10)])



    def swap_tetro(self, old_type):   # 반환값은 새로 갱신될 테트로 객체의 테트로 타입
        if self.hold_type is None:
            self.hold_type = old_type
            now_type = self.next_type
            self.next_type = self.next_tetro_queue.pop(0)
            self.next_tetro_queue.append(Tetromino.choose_type())
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
#
#




class BlockUnit:
    def __init__(self):
        self.display_type = 'B'
        self.filled = False




class ScreenManager:
    DISPLAY_CHARS = {'T': '■', 'B': '□'}


    @classmethod
    def get_tetro_preview(cls, tetro_type):
        """주어진 타입의 테트로 미리보기 (4x4 그리드)"""
        if tetro_type is None:
            return [['□' for _ in range(4)] for _ in range(4)]
        
        preview_grid = [['□' for _ in range(4)] for _ in range(4)]
        offsets = Tetromino.ROTATION_SHAPES[tetro_type][0]
        
        for y, x in offsets:
            py, px = int(y) + 1, int(x) + 1  # 중앙에 배치
            if 0 <= py < 4 and 0 <= px < 4:
                preview_grid[py][px] = '■'
        
        return preview_grid

    @classmethod
    def reset_screen(cls, units, score, level, hold_type=None, next_type=None):
        print("\033[2J\033[H", end='', flush=True)
        score = int(score)
        
        hold_preview = cls.get_tetro_preview(hold_type)
        next_preview = cls.get_tetro_preview(next_type)
        
        print("═" * 12 + "═" * 22 + "═" * 12)
        print("[HOLD]      ║ " + " " * 20 + "║ [NEXT]")
        
        # 상단 4줄: 게임판과 hold/next 미리보기를 함께 출력
        for i in range(4):
            hold_line = " ".join(hold_preview[i])
            game_content = " ".join(cls.DISPLAY_CHARS.get(u.display_type, '□') for u in units[i])
            next_line = " ".join(next_preview[i])
            
            print(f"{hold_line} ║ {game_content} ║ {next_line}")
        
        # 나머지 게임판 (4줄 이후)
        score_lines = [f"Score: {score}", f"Level: {level}"]
        for i in range(4, len(units)):
            # 좌측 정보 출력
            if i - 4 < len(score_lines):
                left_text = score_lines[i - 4]
                print(f"{left_text:<12}║ ", end='')
            else:
                print("            ║ ", end='')
            
            print(" ".join(cls.DISPLAY_CHARS.get(u.display_type, '□') for u in units[i]), end='')
            print(" ║")
        
        print("═" * 12 + "═" * 22 + "═" * 12)
        print(f"Score: {score} | Level: {level}")
        print("A:Left S:Down D:Right Q:CCW E:CW Space:HardDrop W:Hold X:Quit")
        
        print("═" * 12 + "═" * 22 + "═" * 12)
        print(f"Score: {score} | Level: {level}")
        print("A:Left S:Down D:Right Q:CCW E:CW Space:HardDrop W:Hold X:Quit")


def get_input_async():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1).lower()
    return None




# --- Main Game Loop ---
GB = GameBoard()
GB.generate_map()
current_tetro = GB.spawn_tetro()
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


            elif key == 'w':
                current_tetro.clear_display()
                new_type = GB.swap_tetro(current_tetro.tetro_type)
                current_tetro = GB.spawn_tetro(new_type, current_tetro.anchor_point)
                current_tetro.update_display()
                change_happened = True


            elif key == 'x':
                running = False


        if change_happened:
            print(current_tetro.tetro_type)
            current_tetro.update_display()
            ScreenManager.reset_screen(GB.units, GB.score, GB.level, GB.hold_type, GB.next_type)
            change_happened = False



        # 바닥에 닿았을 때 고정 로직
        if current_tetro.is_collied(current_tetro.current_coords, 1, 0):
            fix_timer += 0.05
            if fix_timer >= 0.5 or harddropped:
                current_tetro.lock()
                GB.check_full_row()
                current_tetro = GB.spawn_tetro()
                fix_timer = 0.0
                harddropped = False
                change_happened = True
        else:
            fix_timer = 0.0

except KeyboardInterrupt:
    print("\nQuit")
    sys.exit(0)
