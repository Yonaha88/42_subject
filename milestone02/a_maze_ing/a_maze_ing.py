#!/usr/bin/env python3
"""Command-line entry point for the A-Maze-ing maze generator.

Usage: ``python3 a_maze_ing.py config.txt``

Loads the configuration file given as the first argument, generates a
maze, and runs the interactive terminal menu. All maze generation,
solving, and rendering logic lives in the reusable :mod:`mazegen`
module so it can be imported independently by other projects.
"""

from mazegen import MazeGenerator, ConfigError

if __name__ == "__main__":
    try:
        gen = MazeGenerator()
        gen.set_config()
        gen.entry_point()
    except ConfigError as e:
        print(e)
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
    except EOFError:
        print("\nEOF received. Exiting.")
    except BaseException:
        print("\nUnexpected error")
