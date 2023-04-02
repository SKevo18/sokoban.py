import typing as t

import os
import sys

from pathlib import Path
from time import sleep



ROOT_PATH = Path(__file__).parent.absolute()
LEVELS_ROOT = ROOT_PATH / 'levels'

C = '▣'
P = '☺'
G = '•'
NON_SOLID = (' ', C, G)


def get_key():
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode('utf-8')

    elif os.name == 'posix':
        import tty
        import select

        fd = sys.stdin.fileno()
        old_settings = tty.tcgetattr(fd) # type: ignore

        try:
            tty.setcbreak(fd)
            while True:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    return sys.stdin.read(1)

        finally:
            tty.tcsetattr(fd, tty.TCSADRAIN, old_settings) # type: ignore



def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        print("\033c", end='')



def load_levels() -> t.List[list]:
    level_files = sorted(LEVELS_ROOT.glob('level_*.txt'), key=lambda path: path.stem)
    levels = []

    for level_file in level_files:
        level_data = [list(line.rstrip()) for line in level_file.read_text('utf-8').splitlines()]
        levels.append(level_data)


    if len(levels) < 1:
        raise RuntimeError("No levels are defined.")

    return levels



def find_initial_positions() -> t.Tuple[t.Tuple[int, int], t.List[t.Tuple[int, int]], t.List[t.Tuple[int, int]]]:
    global BOARD
    player_position, CUBE_POSITION, goal_positions = None, [], []

    for y, row in enumerate(BOARD):
        for x, cell in enumerate(row):
            if cell == 'P':
                player_position = (y, x)
                BOARD[y][x] = ' '

            elif cell == 'C':
                CUBE_POSITION.append((y, x))
                BOARD[y][x] = ' '

            elif cell == 'G':
                goal_positions.append((y, x))
                BOARD[y][x] = ' '
    
    if player_position is None:
        raise RuntimeError('Player position is not defined.')


    return player_position, CUBE_POSITION, goal_positions


BOARDS = load_levels()
print(sys.argv)

STEPS = 0

try:
    LEVEL_INDEX = int(sys.argv[1]) - 1
    BOARD = BOARDS[LEVEL_INDEX]
except (IndexError, ValueError):
    LEVEL_INDEX = 0
    BOARD = BOARDS[LEVEL_INDEX]
initial_player_position, initial_cube_positions, GOAL_POSITIONS = find_initial_positions()

PLAYER_POSITION = initial_player_position
CUBE_POSITIONS = initial_cube_positions



def print_hud():
    print(f"""
Cube Pusher (https://github.com/SKevo18/cube_pusher)

Controls:
• Move with `w`, `a`, `s`, `d`.
• `q` to exit.

Level: {LEVEL_INDEX + 1}
Solution Steps: {STEPS}
    """)
    print()



def print_board():
    print_hud()

    for y, row in enumerate(BOARD):
        for x, cell in enumerate(row):
            if (y, x) == PLAYER_POSITION:
                print(P, end=" ")

            elif (y, x) in CUBE_POSITIONS:
                print(C, end=" ")

            elif (y, x) in GOAL_POSITIONS:
                print(G, end=" ")
            
            else:
                print(cell, end=" ")

        print()



def reload_positions():
    global LEVEL_INDEX, PLAYER_POSITION, CUBE_POSITIONS, GOAL_POSITIONS, BOARD

    BOARD = BOARDS[LEVEL_INDEX]
    initial_player_position, initial_cube_position, GOAL_POSITIONS = find_initial_positions()
    PLAYER_POSITION = initial_player_position
    CUBE_POSITIONS = initial_cube_position



def next_level():
    global LEVEL_INDEX, PLAYER_POSITION, CUBE_POSITIONS, GOAL_POSITIONS, BOARD
    LEVEL_INDEX += 1

    if LEVEL_INDEX >= len(BOARDS):
        clear_screen()
        print("You completed all levels! Congratulations!")
        sys.exit(0)

    else:
        reload_positions()



def is_level_completed():
    return all([position in GOAL_POSITIONS for position in CUBE_POSITIONS])



def game_loop():
    global PLAYER_POSITION, STEPS

    while True:
        clear_screen()
        print_board()

        key = get_key()
        if key in ('q', 'Q'):
            break


        dx, dy = 0, 0
        if key in ('w', 'W'):
            dx, dy = -1, 0
        elif key in ('s', 'S'):
            dx, dy = 1, 0
        elif key in ('a', 'A'):
            dx, dy = 0, -1
        elif key in ('d', 'D'):
            dx, dy = 0, 1


        if dx or dy:
            new_player_position = (PLAYER_POSITION[0] + dx, PLAYER_POSITION[1] + dy)

            if BOARD[new_player_position[0]][new_player_position[1]] in NON_SOLID:
                if new_player_position in CUBE_POSITIONS:
                    new_cube_position = (new_player_position[0] + dx, new_player_position[1] + dy)
                    if BOARD[new_cube_position[0]][new_cube_position[1]] in NON_SOLID and new_cube_position not in CUBE_POSITIONS:
                        CUBE_POSITIONS[CUBE_POSITIONS.index(new_player_position)] = new_cube_position
                        PLAYER_POSITION = new_player_position
                        STEPS += 1

                elif new_player_position not in CUBE_POSITIONS:
                    PLAYER_POSITION = new_player_position
                    STEPS += 1

            if is_level_completed():
                STEPS = 0
                next_level()



if __name__ == '__main__':
    try:
        game_loop()

    except KeyboardInterrupt:
        clear_screen()
        print("Exitting...")
