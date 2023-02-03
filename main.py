from random import randint, choices

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Your shoot is out of the Board!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "You've already shoot here"

class BoardWrongShipException(BoardException):
    pass

HID = True  # False means board is open; True means board is hidden
L = 6 # Size of the Board
FREEDOTS = []  # list of free dots of the board (LxL) ; created for AI to random.choices - not to repeat the same shot
for a in range(0,L):
    for b in range(0,L):
        d = (a,b)
        FREEDOTS.append(d)

NEAR = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x +=i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooting(self,shot):
        return shot in self.dots

class Board:
    def __init__(self, size=L):
        self.size = size
        self.count = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False):

        for sd in ship.dots:
            for dx, dy in NEAR:
                cur = Dot(sd.x + dx, sd.y +dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)


    def add_ship(self, ship):
        for sd in ship.dots:
            if self.out(sd) or sd in self.busy:
                raise BoardWrongShipException()
        for sd in ship.dots:
            self.field[sd.x][sd.y] = "■"
            self.busy.append(sd)

        self.ships.append(ship)

        self.contour(ship)

    def shot(self, bd, wounded = False):
        if self.out(bd):
            raise BoardOutException()

        if bd in self.busy:
            raise BoardUsedException()
        self.busy.append(bd)

        for ship in self.ships:
            if ship.shooting(bd):
                ship.lives -= 1
                self.field[bd.x][bd.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("The ship have been destroyed!")
                    return False
                else:
                    print("The ship have been wounded!")
                    wounded = True
                    return True, wounded
        self.field[bd.x][bd.y] = "."
        print("Shot by!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
        self.free = FREEDOTS

        # print(self.free)

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        _coord = choices(self.free)
        d = Dot(_coord[0][0],_coord[0][1])
        print(f"AI turn: {d.x+1} {d.y+1}")
        self.free.remove(_coord[0])
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Your shot: ").split()

            if len(cords) != 2:
                print("Input two coordinates! ")
                continue

            x, y = cords

            if not(x.isdigit()) or not (y.isdigit()):
                print("Input figures! ")
                continue

            x, y = int(x), int(y)
            return Dot(x-1, y-1)

def greet():
    print("\n Welcome for Sea Battle game")
    print("-" * (5*L)*2)
    print("   Input format x and y:   ")
    print("   x - number of string    ")
    print("   y - number of column    ")


class Game:
    def __init__(self, size=L):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        list_var = self.lens
        list_var.sort(reverse = True)
        for i in range(0, len(list_var)):
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), list_var[i], randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def print_boards(self):
        print("-" * (5*L)*2)
        print("        Board of User                  Board of Comp")
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |" + "      | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i in range(0,L):
            res += f"\n{i + 1} | "
            for j in range(0,L):
                res += f"{self.us.board.field[i][j]} | "
            res += f"   {i + 1} | "
            for j in range(0,L):
                _var = self.ai.board.field[i][j] # variable str
                if HID:
                    _var = _var.replace("■", "O")
                res += f"{_var} | "

        print(res)
        print("-" * (5*L)*2)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("User Shot!")
                repeat = self.us.move()
            else:
                print("Comp Shot!")
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("-" * (5*L)*2)
                print("User won!\nGame is over!")
                break

            if self.us.board.defeat():
                self.print_boards()
                print("-" * (5*L)*2)
                print("Computer won! \nGame is over!")
                break
            num += 1

    def start(self):
        greet()
        self.loop()

g = Game()

g.start()


