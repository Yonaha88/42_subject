*This project has been created as part of the 42 curriculum by kyonaha.*

# Fly-in

## Description

Fly-in is a drone routing simulator written in Python. A map file
describes a network of zones (the nodes) linked by connections (the
edges). All drones start in the start zone, and the goal is to deliver
every drone to the end zone in as few simulation turns as possible, while
respecting these rules:

- every zone holds at most `max_drones` drones (default 1) at the end of
  a turn, except the start and end zones, which have no limit;
- every connection is used by at most `max_link_capacity` drones
  (default 1) during a turn, in both directions together;
- entering a `normal` or `priority` zone takes 1 turn, entering a
  `restricted` zone takes 2 turns (the drone spends the first one on the
  connection and must land on the second one), and `blocked` zones can
  never be entered;
- when two routes need the same number of turns, the one through
  `priority` zones is preferred.

The program prints one line per turn with the moves of that turn, for
example `D1-roof1 D2-hub-corridorA`. A drone flying toward a restricted
zone is shown with the name of the connection (`D2-hub-corridorA`).

The project is fully object-oriented and type-checked (flake8 and mypy
`--strict`), and it does not use any graph library.

## Instructions

### Requirements

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) to install the dependencies
  (`curl -LsSf https://astral.sh/uv/install.sh | sh` or
  `brew install uv`)

### Installation

```bash
make install        # uv sync: creates .venv with pydantic, flake8, mypy
```

### Running

The test maps of the subject (`maps.tar.gz`) are not stored in this
repository: extract them at the root first (`tar -xzf maps.tar.gz`).

```bash
make run MAP=maps/easy/01_linear_path.txt           # required output
make visual MAP=maps/easy/01_linear_path.txt        # with zone states
uv run python3 main.py <map_file> [--visual]        # without make
```

### Other rules

```bash
make debug MAP=...  # run under pdb
make lint           # flake8 + mypy with the flags of the subject
make lint-strict    # flake8 + mypy --strict
make clean          # remove caches
```

### Map format

```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
connection: hub-roof1
connection: hub-corridorA [max_link_capacity=2]
```

Rules checked by the parser:

- `#` starts a comment, at the beginning or in the middle of a line;
- the first line is `nb_drones: <n>` with 1 ≤ n ≤ 10000, given once;
- exactly one `start_hub:` and one `end_hub:`, neither of them `blocked`;
- zone names are unique and contain no `-` and no space; coordinates are
  integers (negative ones are allowed, the subject maps use them) and two
  zones cannot share the same coordinates;
- metadata is one `[key=value ...]` block; zones accept `zone`, `color`
  and `max_drones`, connections accept `max_link_capacity`; a key cannot
  be repeated; capacities are positive integers; `max_drones` is ignored
  on the start and end zones (they have no limit);
- a connection links two different zones that are already defined, and
  appears only once (`a-b` and `b-a` are the same connection).

Any error stops the program with a message that gives the line and the
cause, for example `Error: line 5: invalid zone type 'fast' (expected
normal, blocked, restricted or priority)`.

## Example

Input (`maps/easy/02_simple_fork.txt`):

```
nb_drones: 4
start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red]
connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

Output (`make run MAP=maps/easy/02_simple_fork.txt`):

```
D1-junction D2-junction
D1-path_a D2-path_b D3-junction D4-junction
D1-goal D2-goal D3-path_a D4-path_b
D3-goal D4-goal
```

A restricted zone takes two turns. Input:

```
nb_drones: 2
start_hub: start 0 0
hub: slow 1 0 [zone=restricted]
end_hub: goal 2 0
connection: start-slow
connection: slow-goal
```

Output (the connection is used during both turns, so D2 leaves after D1
has landed):

```
D1-start-slow
D1-slow
D1-goal D2-start-slow
D2-slow
D2-goal
```

## Algorithm and implementation

### Overview

```
map file --> MapParser --> Network --> Planner --> Schedule --> Validator --> Visualizer
             map_parser.py  models.py   planner.py   schedule.py  validator.py  visualizer.py
```

| File | Role |
|---|---|
| `models.py` | `ZoneType`, `Zone`, `Connection` (pydantic models) and `Network` (the graph, with an adjacency list) |
| `map_parser.py` | Reads the file line by line and builds the `Network`; reports errors with the line number |
| `pathfinder.py` | Dijkstra from the end zone: the fewest turns from every zone to the end |
| `planner.py` | Plans every drone with a reservation table (see below) |
| `schedule.py` | The position of every drone at every turn, and the output lines |
| `validator.py` | Replays a schedule and reports every broken rule |
| `visualizer.py` | Colored terminal output and the `--visual` mode |
| `main.py` | Command line: ties the parts together |

### Dijkstra's algorithm

Dijkstra's algorithm finds the cheapest way from one point of a graph to
the others when every step has a cost that is zero or more. It keeps a
priority queue (Python's `heapq`) of the places reached so far, sorted by
cost. It repeatedly takes the cheapest one out of the queue: that cost is
final, because every other way goes through a place that already costs
at least as much. Then it tries every neighbour and puts it in the queue
if the new cost is lower than the best one known. Here the cost of a move
is the number of turns needed to enter the next zone (1 for normal and
priority zones, 2 for restricted zones; blocked zones are never entered).

### Planning: prioritized planning with a reservation table

The drones are planned one after another (drone D1 first). Each drone
looks for its earliest arrival, knowing the routes of the drones planned
before it:

1. A **reservation table** counts, for every turn, how many drones are in
   each zone and on each connection. It starts empty.
2. For the next drone, a **Dijkstra search over (zone, turn) states**
   finds the earliest turn at which it can be in the end zone. From a
   state the drone can:
   - wait in its zone (if the zone still has room at the next turn);
   - move to a normal or priority neighbour (1 turn), if the connection
     and the zone have room;
   - fly to a restricted neighbour (2 turns), if the connection has room
     during both turns and the zone has room when it lands.
3. The route found is **reserved**, and the next drone is planned.

Because every drone only uses what is still free, the whole schedule
always respects the capacities, and the drones naturally spread over
several routes or wait when it is useful. This approach is known as
*prioritized planning* or *Cooperative A\** (D. Silver, 2005).

Details:

- **Guided search (A\*)**: `pathfinder.py` first computes, with a normal
  Dijkstra that starts from the end zone, the fewest turns from every zone
  to the end (ignoring the other drones). This is a lower bound of the
  remaining turns, so the search explores the most promising states first
  and still finds the earliest arrival.
- **Tie-breaks**: among routes that arrive at the same turn, the planner
  prefers the one through more priority zones, then the one that spends
  fewer turns in zones with a capacity limit (waiting in the start zone,
  which has no limit, leaves room for the other drones).
- **Unreachable end**: if no route exists on the map, the program stops
  with `Error: no path from 'start' to 'goal'` instead of looping forever.
- **Many drones**: a drone's search starts a few turns before the
  previous drone left the start zone instead of at turn 0 (the drones may
  still overtake each other by a short route). A drone's timeline stores
  only its departure turn and its moves, not one item per waiting turn,
  so time and memory grow with the number of drones instead of its
  square. On the hardest map, 1000 drones take about 2 seconds and 10000
  drones about 21 seconds (150 MB); on the challenger map 10000 drones
  take 2 seconds. `nb_drones` is limited to 10000 so that a map with an
  absurd value (for example 400000000) is refused with a clear error
  instead of running for hours.
- **Self-check**: before printing, `main.py` runs the `ScheduleValidator`
  on the plan. It replays every turn independently from the planner and
  checks every rule (moves, restricted transit, blocked zones, zone and
  connection capacities).

### Complexity

Let Z be the number of zones, C the number of connections and T the
number of turns. One drone search visits at most Z x T states and tries
at most C moves from each, with a binary heap: O(Z·T·log(Z·T)) per drone
in the worst case, but the A\* bound keeps it far smaller in practice.
The reservation table is a dictionary, so each capacity check is O(1).
Memory is proportional to the total length of the routes (the number of
moves and waits after leaving the start zone), for the timelines and the
reservations.

### Results

| Map | Turns | Target |
|---|---|---|
| easy/01 linear path (2 drones) | 4 | ≤ 6 |
| easy/02 simple fork (4 drones) | 4 | ≤ 8 |
| easy/03 basic capacity (4 drones) | 4 | ≤ 6 |
| medium/01 dead end trap (5 drones) | 8 | ≤ 12 |
| medium/02 circular loop (6 drones) | 15 | ≤ 15 |
| medium/03 priority puzzle (5 drones) | 7 | ≤ 12 |
| hard/01 maze nightmare (8 drones) | 13 | ≤ 30 |
| hard/02 capacity hell (12 drones) | 16 | ≤ 35 |
| hard/03 ultimate challenge (15 drones) | 26 | ≤ 45 |
| challenger: the impossible dream (25 drones) | 43 | record 45 |

### Interpretation choices

- A move into a restricted zone uses its connection during both turns.
- Drones crossing a connection in opposite directions share its capacity.
- A drone leaving a zone frees its place for a drone arriving in the same
  turn (zones are counted at the end of each turn).
- A connection from a zone to itself (`a-a`), a blocked start or end
  zone, and two zones at the same coordinates are rejected as map errors.
- A connection must come after the definitions of its two zones ("link
  only previously defined zones", subject VII.4).

## Visual representation

- **Colored output**: every zone name is printed in the color given in the
  map (`color=red`, `color=gold`, ... and even `color=rainbow`). A drone
  flying toward a restricted zone is shown in dim text, which makes the
  two-turn moves easy to spot. Unknown color names are printed without
  color.
- **`--visual` mode** (`make visual MAP=...`): after each turn line, the
  program shows every zone that holds drones, with a gauge of how full it
  is, its type, and the drones inside; then the drones in flight and the
  number of delivered drones. It ends with a summary of the metrics
  (total turns, average turns per drone, total path cost, drones moved per
  turn). This shows at a glance where the bottlenecks are and why a drone
  waits.

```
Turn 2  D1-path_a D2-path_b D3-junction D4-junction
  junction [##] 2/2    D3 D4
  path_a   [#] 1/1     D1
  path_b   [#] 1/1     D2
```

- Colors are only used when the output is a terminal and the `NO_COLOR`
  environment variable is not set, so saving the output to a file gives
  clean text in the required format.

## Resources

- [ダイクストラ法とPythonでグラフの最短ルートを計算する](https://qiita.com/simonritchie/items/216eae753fc393da52af)
  (Qiita, in Japanese) — Dijkstra's algorithm with `heapq`.
- [PythonでA\*（A-star）アルゴリズムを書く](https://qiita.com/simonritchie/items/5e31c5cb7c885c9b814a)
  (Qiita, in Japanese) — A\* and its heuristic.
- K. Okumura, [マルチエージェント経路計画の基礎と最新動向](https://speakerdeck.com/ssii/ssii2023-os3-02)
  (SSII 2023, slides in Japanese) — planning many agents, prioritized
  planning.
- Python documentation (Japanese): [`heapq`](https://docs.python.org/ja/3/library/heapq.html),
  [`dataclasses`](https://docs.python.org/ja/3/library/dataclasses.html),
  [`enum`](https://docs.python.org/ja/3/library/enum.html).
- [pydantic](https://docs.pydantic.dev/), [mypy](https://mypy.readthedocs.io/),
  [flake8](https://flake8.pycqa.org/), [uv](https://docs.astral.sh/uv/),
  [NO_COLOR](https://no-color.org/).

### How AI was used

The design and the code of this project were done by me.

- **README writing**: Claude helped me organize the structure of this README
  and polish its English (and that of the docstrings). I wrote the
  content and reviewed and corrected the final text myself;
- **Understanding**: as a complement to the documentation, Claude explained
  some concepts (Dijkstra's algorithm, A*, `heapq`, pydantic, uv,
  Makefile) so that I could describe them accurately.
