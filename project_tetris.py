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
    anchor_point = (0, 4)    #테트로미노 형성 지점의 units 인덱스, 
    SHAPES = {                                 #각 테트로미노의 anchor_point
        'S' : [ (0, 0), (0, 1), (1, -1) (1, 0)]     #첫 줄 첫 블럭
        'Z' : [ (0, -1), (0, 0), (1, 0), (1, 1) ]   #첫 줄 마지막 블럭
        'L' : [ (0, 0), (1, 0), (2, 0), (2, 1) ]    #최상단 블럭
        'J' : [ (0, 0), (1, 0), (2, -1), (2, 0) ]   #최상단 블럭
        'I' : [ (0, 0), (1, 0), (2, 0), (3, 0) ]    #최상단 블럭
        'O' : [ (0, 0), (1, 0), (0, 1), (1, 1) ]   #좌측 상단 블럭
        'T' : [ (0, -1), (0, 0), (0, 1), (1, 0) ] } #첫 줄 중앙 블럭

    
    def __init__(self, chosen_type):
        self.coords = Tetromino.SHAPES[chosen_type]
        
        

    def choose_type(self):
        chosen_type = rd.choices(tetro_types, weights, 1)
        return chosen_type


    def drag_down_tetro(self):
        pass







class BlockUnit:
    TYPE_IMAGES = { tetro_type : pyg.transform.scale( pyg.image.load(f'Block_images/{tetro_type}.png') , (30, 30))
                    for tetro_type in Tetromino.TETRO_TYPES}
    black_background_image = pyg.transform.scale( pyg.image.load('Block_images/black_background.png') , (30, 30))
##    white_background_image = pyg.transform.scale( pyg.image.load('Block_images/white_background.png') , (30, 30))
    coords = [(x, y) for y in range(0, 30 * 18, 30) for x in range(0, 30 * 10, 30)] #coords to blit Block image
    units = [] #all BlockUnit instances are in this list, and this is 2d list, made at func-genegrate_map


    def __init__(self, coord):
        self.coord = coord
        self.filled = False


    @classmethod
    def generate_map(cls):
        ScreenManager.screen.fill((0, 0, 0))
        row_units = []
        for coord in cls.coords:
            if len(row_units) == 10:
                cls.units.append(row_units)
                row_units = []
            ScreenManager.screen.blit(cls.black_background_image, coord)
            row_units.append( cls(coord) )
        pyg.display.flip()


    def blit_unit(self):
        pass





class ScreenManager:
    screen = pyg.display.set_mode((300, 540))






    

pyg.init()
pyg.display.set_caption("TETRIS")
BlockUnit.generate_map()
fall_speed = 500#(ms)
Tetromino.choose_type()
while True:
    break



    

