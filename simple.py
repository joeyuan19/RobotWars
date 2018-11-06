import random
import time

# To Do
# 1. other BC
# 2. load INX every N turns
# 3. if/else command
# 4. different weapons?

REFRESH_DELAY = .1

BC_PERIODIC = 0
BC_WALLED = 1
BC_WALLED_X = 2
BC_WALLED_Y = 3

BOARD_EMPTY = 0
BOARD_BULLET = -1
BOARD_WALL = -2

LEFT = 'l'
RIGHT = 'r'
UP = 'u'
DOWN = 'd'

MOVE = 'm'
SHOOT = 's'
IF = 'i'
PASS = 'p'

CHECK_WALL = 'w'
CHECK_ROBOT = 'r'
CHECK_BOUNDARY = 'b'

class OutOfBoundsException(Exception):
    pass

class Board(object):
    def __init__(self,length,width,BC=0,inx_length=5,actions_per_turn=1):
        self.length = length
        self.width = width
        self.board = [[0 for i in range(length)] for j in range(width)]
        self.inx_length = inx_length
        self.actions_per_turn = actions_per_turn 
        self.robots = {}
        self.play_order = []
        self.BC = BC

    def add_robot(self,robot):
        rid = len(self.play_order)+1
        sym = chr(ord('A')-1+rid)
        self.play_order.append(rid)
        self.robots[rid] = robot
        self.set_position(robot.x,robot.y,rid)
        return rid,sym
   
    def apply_bc(self,x,y):
        if self.BC == BC_PERIODIC:
            if x < 0:
                x = self.length + x
            else:
                x = x%self.length
            if y < 0:
                y = self.width + y
            else:
                y = y%self.width
        elif self.BC == BC_WALLED:
            if x < 0 or x >= self.length:
                raise OutOfBoundsException() 
            if y < 0 or y >= self.width:
                raise OutOfBoundsException() 
        elif self.BC == BC_WALLED_X:
            if x < 0 or x >= self.length:
                raise OutOfBoundsException() 
        elif self.BC == BC_WALLED_Y:
            if y < 0 or y >= self.width:
                raise OutOfBoundsException() 
        return x,y

    def move_robot(self,robot,x,y):
        try:
            x,y = self.apply_bc(x,y)
        except OutOfBoundsException:
            return
        if self.board[y][x] == BOARD_EMPTY:
            self.set_position(robot.x,robot.y,BOARD_EMPTY)
            self.set_position(x,y,robot.robot_id)
            robot.set_position(x,y)
            self.print_board()

    def robot_shoot_y(self,robot,d):
        u = d//abs(d)
        b = robot.y + u
        try:
            lx,ly = self.apply_bc(robot.y,b)
        except OutOfBoundsException:
            return
        for p in range(b,b+d,u):
            try:
                x,y = self.apply_bc(robot.x,p)
            except OutOfBoundsException:
                return
            if self.board[y][x] != BOARD_EMPTY:
                self.robots[self.board[y][x]].hit(robot.gun_power)
                self.print_board()
                lx,ly = x,y
                break
            else:
                self.set_position(lx,ly,0)
                self.set_position(x,y,-1)
            lx,ly = x,y
            self.print_board()
        self.set_position(lx,ly,0)
        self.print_board()
    
    def robot_shoot_x(self,robot,d):
        u = d//abs(d)
        b = robot.x + u
        try:
            lx,ly = self.apply_bc(b,robot.y)
        except OutOfBoundsException:
            return
        for p in range(b,b+d,u):
            try:
                x,y = self.apply_bc(p,robot.y)
            except OutOfBoundsException:
                return
            if self.board[y][x] != BOARD_EMPTY:
                self.robots[self.board[y][x]].hit(robot.gun_power)
                self.print_board()
                break
            else:
                self.set_position(lx,ly,0)
                self.set_position(x,y,-1)
            lx,ly = x,y
            self.print_board()
        self.set_position(lx,ly,0)
        self.print_board()

    def game_over(self):
        return len([i for i in self.robots if self.robots[i].alive()]) <= 1

    def set_position(self,x,y,value):
        self.board[y][x] = value

    def clear_board(self):
        self.board = [[0 for i in range(length)] for j in range(width)]

    def get_symbol(self,n):
        if n > 0:
            return self.robots[n].symbol
        elif n == BOARD_BULLET:
            return '*'
        elif n == BOARD_WALL:
            return '#'
        else:
            return '.'

    def check(self,check,x,y):
        if check == CHECK_WALL:
            return self.board[y][x] == BOARD_WALL
        elif check == CHECK_ROBOT:
            return self.board[y][x] == BOARD_WALL
        elif check == CHECK_BOUNDARY:
            return not (-1 < x < self.length) or not (-1 < y < self.width)

    def draw_board(self):
        board = [''.join(self.get_symbol(i) for i in row) for row in self.board]
        scoreboard = ['Robot | HP'] + [self.robots[rid].symbol + '     | ' + str(self.robots[rid].hp) for rid in self.robots]
        for i,item in enumerate(scoreboard):
            board[i] = board[i] + '   ' + item
        return '\n'.join(board) + '\n'
    
    def print_board(self):
        print(self.draw_board())
        time.sleep(REFRESH_DELAY)

    def get_winner(self):
        return [self.robots[i] for i in self.robots if self.robots[i].alive()][0]

    def play(self):
        self.itr = 0
        random.shuffle(self.play_order)
        self.print_board()
        while self.next_turn():
            self.itr += 1
        self.print_board()
        print('Winner:',self.get_winner().symbol)
    
    def next_turn(self):
        for i in range(self.inx_length):
            for rid in self.play_order:
                self.robots[rid].act(i)
        return not self.game_over()


class Robot(object):
    def __init__(self,hp,gun_range,gun_power,x,y,board,inx):
        self.inx = inx 
        self.hp = hp
        self.x = x
        self.y = y
        self.gun_range = gun_range
        self.gun_power = gun_power
        self.board = board
        self.robot_id,self.symbol = self.board.add_robot(self)

    def alive(self):
        return self.hp > 0

    def hit(self,dmg):
        self.hp -= dmg

    def set_position(self,x,y):
        self.x = x
        self.y = y

    def move(self,direction):
        if direction == DOWN:
            dx,dy = 0,1
        elif direction == UP:
            dx,dy = 0,-1
        elif direction == LEFT:
            dx,dy = -1,0
        elif direction == RIGHT:
            dx,dy = 1,0
        self._move(dx,dy)

    def _move(self,dx,dy):
        self.board.move_robot(self,self.x+dx,self.y+dy)
    
    def shoot(self,direction):
        if direction == UP:
            self.board.robot_shoot_y(self,-self.gun_range)
        elif direction == DOWN:
            self.board.robot_shoot_y(self,self.gun_range)
        elif direction == LEFT:
            self.board.robot_shoot_x(self,-self.gun_range)
        elif direction == RIGHT:
            self.board.robot_shoot_x(self,self.gun_range)

    def ifclause(self,check,space):
        if space == LEFT:
            x,y = self.x-1,self.y
        elif space == RIGHT:
            x,y = self.x+1,self.y
        elif space == UP:
            x,y = self.x,self.y-1
        elif space == DOWN:
            x,y = self.x,self.y+1
        return self.board.check(check,x,y)

    def act(self,i):
        inx = self.inx[i]
        return self._act(inx)

    def _act(self,inx):
        if inx[0] == MOVE:
            self.move(inx[1])
        elif inx[0] == SHOOT:
            self.shoot(inx[1])
        elif inx[0] == IF:
            check = inx[1]
            space = inx[2]
            if self.ifclause(space,check):
                self._act(inx[3:])
        elif inx == PASS:
            pass

L,W = 5,10
b = Board(L,W,inx_length=2)
Robot(3,2,1,0,0,b,['mrsl'])
Robot(3,2,1,L-1,W-1,b,['sdmd'])
b.play()

