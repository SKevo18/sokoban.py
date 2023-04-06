import typing as t

import os
import sys

from dataclasses import dataclass
from pathlib import Path
from enum import Enum


ROOT_PATH = Path(__file__).parent.absolute()
LEVELS_ROOT = ROOT_PATH / 'levels'

G = '\u001b[32;1m•\u001b[0m'
C = '\u001b[33;1m▣\u001b[0m'
P = '\u001b[34;1m☺\u001b[0m'
NON_SOLID = (' ', G, C, P, 'G', 'C', 'P')


class QuitGame(Exception):
    pass



class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)



def get_key() -> bytes:
    if os.name == 'posix':
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.buffer.read(1)

            if ch == b'\x1b':
                ch += sys.stdin.buffer.read(2)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch


    elif os.name == 'nt':
        import msvcrt

        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                return ch

    else:
        raise NotImplementedError(f"`get_key()` is not implemented for this platform ({os.name})")



def wait_for_keys(to_wait: t.Iterable[bytes]) -> bool:
    while True:
        key = get_key()

        return key in to_wait



def clear_screen():
    if os.name == 'nt':
        os.system('cls')

    else:
        print("\033c", end='')



@dataclass
class Sokoban:
    level_number: int = 1
    level_pack: str = 'default'


    def __post_init__(self):
        if self.level_number < 1:
            raise RuntimeError(f"Level number can't be lower than 1: {self.level_number}")


        self.level_files = self.get_level_files(self.level_pack)

        try:
            self.board = self.load_level(self.level_files[self.level_number - 1])

        except IndexError:
            raise RuntimeError(f"There is no level with number {self.level_number} in level pack {self.level_pack}, or the pack does not exist.")


        self.steps = 0
        self.player_position, self.cube_positions, self.goal_positions = self.find_initial_positions()



    def get_level_files(self, level_pack: str) -> t.List[Path]:
        def __int_stem(path: Path) -> int:
            try:
                return int(path.stem)
            except ValueError:
                raise RuntimeError(f'Invalid level file name `{path.relative_to(LEVELS_ROOT)}` (must be an integer).')

        return sorted((LEVELS_ROOT / level_pack).glob('*.txt'), key=__int_stem)



    def load_level(self, level_file: Path) -> t.List[list]:
        return [list(line.rstrip()) for line in level_file.read_text('utf-8').splitlines()]



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
Level: {self.level_pack}/{self.level_number}
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
        if (self.level_number + 1) >= len(self.level_files):
            clear_screen()
            print(f"""
                You have completed all levels in level pack `{self.level_pack}`! Congratulations!
            """)
            raise QuitGame()

        else:
            _next_board = self.load_level(self.level_files[self.level_number])
            clear_screen()

            print(f"""
                You have finished level {self.level_number} with {self.steps} steps!

                Press `Enter` to continue to level {self.level_number + 1}, `r` to restart current level, `q` to quit.
            """)

            while True:
                key = get_key()

                if key in (b'\r', b'\n'):
                    self.level_number += 1
                    self.board = _next_board
                    self.player_position, self.cube_positions, self.goal_positions = self.find_initial_positions()
                    self.steps = 0
                    break

                elif key in (b'r'):
                    self.restart_level()
                    break
                
                elif key in (b'q'):
                    raise QuitGame()



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
        clear_screen()

        print(f"""
            Sokoban.py (https://github.com/SKevo18/sokoban.py)

            Level pack: {self.level_pack}
            Level: {self.level_number}

            Controls:
            • Move with `w`, `a`, `s`, `d` or arrow keys.
            • `r` to restart.
            • `q` to exit.

            Press 'Enter' to start, anything else to quit.
        """)

        if wait_for_keys((b'\r', b'\n')):
            return self.game_loop()



    def handle_game_input(self):
        key = get_key()
        if key in (b'q'):
            raise QuitGame

        if key in (b'r'):
            return self.restart_level()

        if key == b'\x00':
            return

        direction = None
        if key in (b'w', b'H', b'\x1b[A'):
            direction = Direction.UP
        elif key in (b's', b'P', b'\x1b[B'):
            direction = Direction.DOWN
        elif key in (b'a', b'K', b'\x1b[D'):
            direction = Direction.LEFT
        elif key in (b'd', b'M', b'\x1b[C'):
            direction = Direction.RIGHT

        if direction:
            return self.move(direction)



    def game_loop(self):
        while True:
            clear_screen()
            self.print_board()

            try:
                self.handle_game_input()

            except QuitGame:
                sys.exit(0)



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('level_number', type=int, default=1, nargs='?')
    parser.add_argument('level_pack', type=str, default='default', nargs='?')
    args = parser.parse_args()


    try:
        sokoban = Sokoban(args.level_number, args.level_pack)
        sokoban.main_menu()

    except KeyboardInterrupt:
        clear_screen()
        print("Exitting...")

    except Exception as exception:
        clear_screen()
        print("Error:", exception)
        sys.exit(1)
