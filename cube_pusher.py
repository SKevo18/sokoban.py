import typing as t
import os
import sys
from pathlib import Path
from enum import Enum


ROOT_PATH = Path(__file__).parent.absolute()
LEVELS_ROOT = ROOT_PATH / 'levels'

C = '\u001b[32;1m▣\u001b[0m'
P = '\u001b[34;1m☺\u001b[0m'
G = '\u001b[33;1m•\u001b[0m'
NON_SOLID = (' ', C, G, 'P', 'C', 'G')



class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)



def get_key():
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode('utf-8')

    elif os.name == 'posix':
        import tty
        import select

        fd = sys.stdin.fileno()
        old_settings = tty.tcgetattr(fd)  # type: ignore

        try:
            tty.setcbreak(fd)
            while True:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    return sys.stdin.read(1)

        finally:
            tty.tcsetattr(fd, tty.TCSADRAIN, old_settings)  # type: ignore



def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        print("\033c", end='')



class CubePusher:
    def __init__(self, level_index: int = 0):
        self.boards = self.load_levels()
        self.level_index = level_index
        self.board = self.boards[self.level_index]
        self.steps = 0
        self.player_position, self.cube_positions, self.goal_positions = self.find_initial_positions()


    def load_levels(self) -> t.List[list]:
        level_files = sorted(LEVELS_ROOT.glob('level_*.txt'), key=lambda path: path.stem)
        levels = []

        for level_file in level_files:
            level_data = [list(line.rstrip()) for line in level_file.read_text('utf-8').splitlines()]
            levels.append(level_data)

        if len(levels) < 1:
            raise RuntimeError("No levels are defined.")

        return levels


    def find_initial_positions(self) -> t.Tuple[t.Tuple[int, int], t.List[t.Tuple[int, int]], t.List[t.Tuple[int, int]]]:
        player_position, cube_positions, goal_positions = None, [], []

        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell == 'P':
                    player_position = (y, x)
                elif cell == 'C':
                    cube_positions.append((y, x))
                elif cell == 'G':
                    goal_positions.append((y, x))

        if player_position is None or len(cube_positions) != len(goal_positions):
            raise RuntimeError('Player position is not defined, or amount of cubes do not equal amount of goals.')

        return player_position, cube_positions, goal_positions


    def print_hud(self):
        print(f"""
Level: {self.level_index + 1}
Solution Steps: {self.steps}
    """)
        print()


    def print_board(self):
        self.print_hud()

        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if (y, x) == self.player_position:
                    print(P, end=" ")

                elif (y, x) in self.cube_positions:
                    print(C, end=" ")

                elif (y, x) in self.goal_positions:
                    print(G, end=" ")

                elif cell in ('P', 'C', 'G'):
                    print(" ", end=" ")

                else:
                    print(cell, end=" ")

            print()


    def next_level(self):
        if (self.level_index + 1) >= len(self.boards):
            clear_screen()
            print("You have completed all levels! Congratulations!")
            sys.exit(0)

        else:
            print(f"""
                You have finished level {self.level_index + 1} with {self.steps} steps!

                Press 'Enter' to continue to level {self.level_index + 2}, anything else to restart current level
            """)

            enter = input()
            if enter == '':
                self.level_index += 1
                self.board = self.boards[self.level_index]
                self.player_position, self.cube_positions, self.goal_positions = self.find_initial_positions()
                self.steps = 0

            else:
                self.restart_level()


    def restart_level(self):
        self.player_position, self.cube_positions, _ = self.find_initial_positions()
        self.steps = 0


    def is_level_completed(self):
        return all([position in self.goal_positions for position in self.cube_positions])


    def move(self, direction: Direction):
        dx, dy = direction.value
        new_player_position = (self.player_position[0] + dx, self.player_position[1] + dy)

        if self.board[new_player_position[0]][new_player_position[1]] in NON_SOLID:
            if new_player_position in self.cube_positions:
                new_cube_position = (new_player_position[0] + dx, new_player_position[1] + dy)
                if self.board[new_cube_position[0]][new_cube_position[1]] in NON_SOLID and new_cube_position not in self.cube_positions:
                    self.cube_positions[self.cube_positions.index(new_player_position)] = new_cube_position
                    self.player_position = new_player_position
                    self.steps += 1
            elif new_player_position not in self.cube_positions:
                self.player_position = new_player_position
                self.steps += 1

        if self.is_level_completed():
            self.next_level()


    def main_menu(self):
        print("""Cube Pusher (https://github.com/SKevo18/cube_pusher)

Controls:
• Move with `w`, `a`, `s`, `d`.
• `q` to exit.

Press 'Enter' to start.""")


    def game_loop(self):
        while True:
            clear_screen()
            self.print_board()

            key = get_key()
            if key in ('q', 'Q'):
                break

            if key in ('r', 'R'):
                self.restart_level()
                continue

            direction = None
            if key in ('w', 'W', 'H'):
                direction = Direction.UP
            elif key in ('s', 'S', 'P'):
                direction = Direction.DOWN
            elif key in ('a', 'A', 'K'):
                direction = Direction.LEFT
            elif key in ('d', 'D', 'M'):
                direction = Direction.RIGHT

            if direction:
                self.move(direction)



if __name__ == '__main__':
    try:
        level_index = int(sys.argv[1]) - 1 if len(sys.argv) > 1 else 0
        cube_pusher = CubePusher(level_index)
        cube_pusher.game_loop()

    except KeyboardInterrupt:
        clear_screen()
        print("Exitting...")
