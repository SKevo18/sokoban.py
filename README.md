# Sokoban.py

A pure-Python terminal game based on Soko-Ban. Produced by ChatGPT-4 as an April fools experiment (modified).

## How to play

- You must have [Python 3.6+](https://python.org) downloaded;
- Run `python sokoban.py` (or specify a level number: `python sokoban.py 2`);
- Move with `WASD` or arrow keys (Windows), press `r` to restart current level, `q` to quit;
- The goal is to move all cubes to goals;

### NB

- Each level has unlimited moves/time;
- You can't pull cubes;
- You can't undo a step;
- You can't push 2 or more cubes at the same time;

...so, plan ahead!

## Features

- Pure 3.6+ Python with no third-party modules required;
- Levels are stored as `.txt` files;
- Steps counter;
- Both Windows and Linux compatible;

## TODO

- [ ] Better HUD:
  - [x] Main menu
  - [x] Level completed screen;
  - [ ] Level selector;
- [x] Ability to restart level;
- [ ] Score counter (when collecting something or when pushing cube to goal, etc...);
- [ ] Saves (best steps, score, etc...);
