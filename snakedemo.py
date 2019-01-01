import pygame, sys, math, random
from pygame.locals import *
from collections import deque

def create_board(size):
    return [[Node(x, y) for x in range(size)] for y in range(size)]

def new_apple():
    while True:
        apple_x = math.floor(random.uniform(0, 1) * size)
        apple_y = math.floor(random.uniform(0, 1) * size)
        if board[apple_y][apple_x].block == False:
            return apple_x, apple_y

class Node:
    def __init__(self, x, y):
        self.block = False
        self.x = x
        self.y = y
        self.parent = None
        self.g_score = -1
        self.f_score = -1
        self.heuristic = lambda x_final, y_final: math.floor(abs(x_final - self.x) + abs(y_final - self.y))
    def __str__(self):
        return str(self.x) + ", " + str(self.y)
    def __sub__(self, other):
        return Node(self.x - other.x, self.y - other.y)

def draw():
    screen.fill(BLACK)   
    apple = pygame.draw.rect(screen, RED, (apple_x * BLOCK_W, apple_y * BLOCK_H, BLOCK_W, BLOCK_H))
    first = True
    for part in snake:
        if first:
            pygame.draw.rect(screen, WHITE, (part.x * BLOCK_W, part.y * BLOCK_H, BLOCK_W, BLOCK_H))
            first = False
        else:
            pygame.draw.rect(screen, GREEN, (part.x * BLOCK_W, part.y * BLOCK_H, BLOCK_W, BLOCK_H))

    pygame.display.update()

def check_bounds(current=Node(-1,-1), i=0, j=0):
    if next_x < 0 or next_x >= size or next_y < 0 or next_y >= size:
        die()
    if board[next_y][next_x].block and current.x == -1 and current.y == -1:
        die()
    if current.x + j < 0 or current.x + j > size - 1 or current.y + i < 0 or current.y + i > size - 1:
        return False
    if board[current.y + i][current.x + j].block:
        return False
    if current.y + i == current.y and current.x + j == current.x or (i == -1 and j == -1) or (i == -1 and j == 1) or (i == 1 and j == -1) or (i == 1 and j == 1):
        return False
    return True

def die():
    f = pygame.font.SysFont('Arial', 30)
    t = f.render('Score: ' + str(score), True, RED)
    screen.blit(t, (SCREEN_W//2 - 50, SCREEN_H//2))
    print("Score: ", score)
    pygame.display.update()
    pygame.time.wait(3000)
    sys.exit()

def a_star(x, y):
    end_x = x
    end_y = y

    closed_set = []
    open_set = []

    open_set.append(board[snake_y][snake_x])
    board[snake_y][snake_x].g_score = 0
    board[snake_y][snake_x].f_score = board[snake_y][snake_x].heuristic(end_x, end_y)

    while (len(open_set) > 0):
        open_set.sort(key=lambda n: n.f_score)
        current = open_set[0]

        if current.x == end_x and current.y == end_y:
            return make_path(board, current)
        
        open_set.remove(current)
        closed_set.append(current)

        for i in range(-1, 2):
            for j in range(-1, 2):

                if not check_bounds(current, i, j):
                    continue

                neighbour = board[current.y + i][current.x + j]
                if closed_set.count(neighbour) != 0:
                    continue
                
                temp_score = neighbour.g_score + 1

                if open_set.count(neighbour) == 0:
                    open_set.append(neighbour)
                
                neighbour.parent = current
                neighbour.g_score = temp_score
                neighbour.f_score = neighbour.g_score + neighbour.heuristic(end_x, end_y)

    return []

def make_path(b, c):
    current = c
    path = [current]

    while current.parent != None:
        path.append(current.parent)
        current = current.parent

    return path   

def stall(end_x, end_y):
    lowestfScore = -1
    lowestfScoreNode = None

    for i in range(-1, 2):
        for j in range(-1, 2):
            if not check_bounds(snake[0], i, j):
                continue
            
            neighbour = board[snake[0].y + i][snake[0].x + j]
            pathScore = neighbour.g_score + neighbour.heuristic(end_x, end_y)

            if pathScore > lowestfScore:
                lowestfScore = pathScore
                lowestfScoreNode = neighbour

    return lowestfScoreNode

def start_screen():
    wait = True
    f = pygame.font.SysFont('Arial', 30)
    t = f.render("Pres Enter to Start", True, GREEN)
    screen.blit(t, (SCREEN_W//2 - 80, SCREEN_H//2 - 20))
    pygame.display.update()
    while wait:
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit(0)
            elif e.type == KEYDOWN:
                if (e.key == K_RETURN):
                    wait = False

SPEED = 80
SCREEN_W = 600
SCREEN_H = 600
ROWS = 40
COLS = 40
BLOCK_W = math.floor(SCREEN_W//COLS)
BLOCK_H = math.floor(SCREEN_H//ROWS)

size = ROWS

clock = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

BLACK=(0,0,0)
GREEN=(0,255,0)
RED=(255,0,0)
WHITE=(255,255,255)

screen.fill(BLACK)

dirs = 1
snake_x = 0
snake_y = 0
next_x = 0
next_y = 0
apple_x = 0
apple_y = 0
score = 0

board = create_board(size)
snake = deque()
snake.append(board[snake_y][snake_x])
board[snake_y][snake_x].block = True
apple_x, apple_y = new_apple()

start_screen()

while True:
    p = a_star(apple_x, apple_y)
    for i in p:
        i.parent = None
        i.g_score = -1
        i.f_score = -1
    
    for i in range(size):
        for j in range(size):
            board[i][j].parent = None
            board[i][j].g_score = -1
            board[i][j].f_score = -1

    next_loc = None
    if p:
        next_loc = p[-2]
    else:
        next_node = stall(apple_x, apple_y)
        if (next_node == None):
            die()
        else:
            next_loc = next_node

    next_x = next_loc.x
    next_y = next_loc.y

    clock.tick(SPEED)
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit(0)

    check_bounds()
    
    snake.appendleft(board[next_y][next_x])
    board[next_y][next_x].block = True

    snake_x = next_x
    snake_y = next_y    

    if snake_x == apple_x and snake_y == apple_y:
        apple_x, apple_y = new_apple()
        score += 1
    else:
        tail = snake.pop()
        tail.block = False
        board[tail.y][tail.x].block = False

    draw()
