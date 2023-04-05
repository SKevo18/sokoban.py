# Cube Pusher

A pure-Python terminal game based on the original [Cube Pusher](https://idowngames.com/cube-pusher) (which was based on Soko-Ban - which this version actually resembles more closely). Produced by ChatGPT-4 as an April fools experiment (modified).

## How to play

- You must have [Python 3.6+](https://python.org) downloaded;
- Run `python cube_pusher.py` (or specify a level number: `python cube_pusher.py 2`);
- Move with `WASD`, press `q` to quit;
- The goal is to move all cubes (`▣`) to... well, goals (`•`);

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
  - [ ] Main menu
  - [ ] Level completed screen;
  - [ ] Level selector;
- [ ] Ability to restart level;
- [ ] Score counter (when collecting something or when pushing cube to goal, etc...);
- [ ] Saves (best steps, score, etc...);
