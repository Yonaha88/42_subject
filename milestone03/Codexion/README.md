*This project has been created as part of the 42 curriculum by kyonaha.*

# Codexion

## Description

Codexion is a concurrency simulation written in C with POSIX threads.
Each coder runs as its own thread and competes for a limited number of
shared resources called dongles. It is not a program that computes a
schedule in advance: the coders really run at the same time, and the
scheduling policy (`fifo` or `edf`) only decides who gets a dongle when
several coders want it.

- The coders sit in a circle. Coder `k` shares dongle `k` with one
  neighbour and dongle `k + 1` with the other; the last coder's second
  dongle is dongle `1`.
- To compile, a coder must hold **both** of its dongles at the same time.
- Each coder repeats the cycle **compile → debug → refactor**.
- After a dongle is released, it stays unusable for `dongle_cooldown`
  milliseconds.
- A coder **burns out** if it does not start a new compile within
  `time_to_burnout` milliseconds of the start of its previous compile
  (or of the simulation start).

The simulation ends when every coder has compiled at least
`number_of_compiles_required` times, or as soon as one coder burns out.

## Instructions

### Build

```sh
make        # builds ./codexion (cc -Wall -Wextra -Werror -pthread)
make clean  # removes object files
make fclean # removes object files and the binary
make re     # fclean + all
```

### Run

```sh
./codexion number_of_coders time_to_burnout time_to_compile time_to_debug \
           time_to_refactor number_of_compiles_required dongle_cooldown scheduler
```

| Argument | Meaning |
|---|---|
| `number_of_coders` | Number of coders, and also the number of dongles (at least 1) |
| `time_to_burnout` | Milliseconds a coder may go without starting a new compile |
| `time_to_compile` | Milliseconds a compile takes (both dongles are held) |
| `time_to_debug` | Milliseconds spent debugging after a compile |
| `time_to_refactor` | Milliseconds spent refactoring after debugging |
| `number_of_compiles_required` | The simulation stops once every coder has compiled this many times |
| `dongle_cooldown` | Milliseconds a dongle stays unusable after it is released |
| `scheduler` | `fifo` or `edf` |

All numbers must be non-negative integers up to `INT_MAX`.
Any invalid argument prints an error to `stderr` and the program exits
without starting the simulation.

- **`fifo`** (First In, First Out): dongles go to coders in the order
  they asked for them.
- **`edf`** (Earliest Deadline First): dongles go to the coder whose
  burnout deadline (start of the last compile + `time_to_burnout`) is
  the earliest. Ties are broken by request order.

Example:

```sh
./codexion 5 800 200 200 200 3 0 fifo
```

Each state change is printed as `timestamp_in_ms coder_id message`, for
example `200 1 is debugging`.

## Blocking cases handled

### Deadlock (Coffman conditions)

A deadlock needs all four Coffman conditions at the same time:

1. **Mutual exclusion**: a dongle can be held by only one coder.
2. **Hold and wait**: a coder holds one dongle while waiting for another.
3. **No preemption**: a dongle cannot be taken away from its holder.
4. **Circular wait**: the waiting coders form a cycle.

The classic deadlock is every coder picking up one dongle and then
waiting forever for its neighbour's.

Conditions 1 and 3 are part of the rules, so Codexion breaks the other two:

- **Hold and wait is broken.** A coder takes its two dongles
  *together* or not at all (`try_take`). The check and the take happen
  while holding the `arbiter` mutex, so no other coder can slip in
  between. A coder that cannot take both holds nothing while it waits.
- **Circular wait is broken.** A coder puts the *same* request
  (same priority key and same ticket) into both of its dongles' queues.
  Since all requests are compared by one total order, the
  highest-priority request is at the head of both of its queues, so that
  coder can always proceed and the waits cannot form a cycle.

### Starvation

Each dongle has its own priority queue (a binary heap). A request is
compared by its key first and its ticket second; the ticket is a global
counter that grows with every request.

- **`fifo`**: the key is the ticket itself. A later request always gets
  a larger ticket, so it can never overtake a coder that is already
  waiting. Every coder is eventually at the head of both queues.
- **`edf`**: the key is the burnout deadline. A waiting coder's
  deadline is fixed while it waits, but a coder that starts compiling
  moves its own deadline later. Because `time_to_burnout` is the same
  for everyone, a waiting coder can only be overtaken by coders whose
  last compile is even older, and only a limited number of times. Its
  deadline soon becomes the earliest and it gets the dongles.

Starvation-free does not mean burnout-free: if the timings are too
tight (for example `time_to_burnout` close to `time_to_compile`), a
coder can still burn out while waiting for its fair turn. Strict
ordering is kept on purpose, even when breaking it could save a coder
in a tight setup.

### Dongle cooldown

When a coder releases its dongles, `release_dongles` stores
`available_at = now + dongle_cooldown` in each dongle. `dongle_usable`
only lets a coder take a dongle that has no holder **and** whose
`available_at` has passed.

Nobody signals the end of a cooldown, so a waiting coder sets its own
alarm (`wait_turn`):

1. `next_wakeup` picks the time to wake up: the end of a pending
   cooldown, capped at 50 ms from now.
2. While more than 8 ms remain, the coder sleeps in
   `pthread_cond_timedwait` until 8 ms before that time. A neighbour
   that releases a dongle can still wake it early with a signal.
3. In the last 8 ms the coder releases the `arbiter` and sleeps with
   `usleep(left / 2 + 1)`, then checks again. The steps get shorter and
   shorter, so it does not oversleep.

`pthread_cond_timedwait` alone often wakes up a few milliseconds late.
In a test with two coders alternating (`2 5000 200 100 100 8 100 fifo`),
`timedwait` alone started each compile 2–3.5 ms late on average (up to
5 ms), while the two-step wait was usually on time. With only 5 ms of
slack (`2 605 200 100 100 5 100 fifo`), `timedwait` alone burned out in
8 of 8 runs, against 4 of 8 with the two-step wait.

### Precise burnout detection

The burnout must be printed within 10 ms. Two checks make sure of it:

- **The monitor thread** checks every coder every 1 ms
  (`now - last_compile > time_to_burnout`), so a burnout is normally
  reported about 1 ms after it happens. The monitor only takes each
  coder's `state_mutex`, never the `arbiter`, so busy dongle traffic
  cannot delay it.
- **The coder itself** checks again in `log_compile`, right before
  printing `is compiling`. Between two monitor checks, a coder whose
  deadline has just passed could still get its dongles. Without this
  check it would print a compile that happens after its burnout.
  Instead it prints `burned out` itself and stops.

Both checks run while holding `log_mutex` and only print if the
simulation has not stopped yet, so `burned out` is printed exactly once.

### Log serialization

- Every log function (`log_state`, `log_burnout`, `log_compile`) holds
  `log_mutex` while printing, so only one thread prints at a time.
- `write_line` builds the whole line in a local buffer and sends it with
  a single `write`, so a line can never be split by another thread.
- `log_compile` prints `has taken a dongle` twice and `is compiling`
  under the same lock, with the same timestamp, so nothing can appear
  between them.
- No line is printed after the end. The stop flag is checked
  (`is_stopped`) and set (`set_stop`) while holding `log_mutex`, so
  there is no gap between "the simulation is still running" and the
  actual print.

## Thread synchronization mechanisms

### Mutexes

| Mutex | Scope | Protects |
|---|---|---|
| `stop_mutex` | one | The `stop` flag (`is_stopped`, `set_stop`) |
| `log_mutex` | one | Standard output, and the "still running? then print" sequence |
| `arbiter` | one | `next_ticket`, the start counters `arrived` / `started`, and the whole "request → check → take both dongles" sequence |
| `state_mutex` | per coder | `last_compile` and `compiles`, which the monitor reads from another thread |
| `mutex` | per dongle | `holder`, `available_at` and the dongle's request queue |

Locks are only nested in two ways: `arbiter` first and then a dongle
`mutex`, a `state_mutex` or `stop_mutex`; or `log_mutex` first and
then a `state_mutex` or `stop_mutex`. `arbiter` and `log_mutex` are
never held together, and the inner locks are released before any other
lock is taken. No thread takes them in the opposite order, so the
locks themselves cannot deadlock.

Dongle state is only touched while the `arbiter` is held, so the
per-dongle mutexes are not strictly needed for correctness. They are
kept because the subject requires each dongle's state to be protected by
its own mutex, and they keep each dongle helper (`dongle_usable`,
`dongle_take`, …) safe on its own.

### Condition variables

Both condition variables are used with the `arbiter` mutex.

| Condition variable | Who sleeps | Who wakes it up, and when |
|---|---|---|
| `wake` (per coder) | A coder that cannot take its dongles yet, or that waits for the start | `release_dongles` signals both neighbours after releasing; `wake_all` wakes everyone at the start and at the end |
| `ready` (one) | The main thread in `start_clock` | The last coder to arrive in `wait_start` |

**Simultaneous start.** Each coder increases `arrived` and sleeps on
its `wake`. The last one signals `ready`. The main thread then sets the
start time and every coder's `last_compile` to the same value, sets
`started = 1` and wakes everyone, so all coders start from the same
moment.

**Always re-check after waking up.** Every wait is inside a `while`
loop that checks its condition again (`take_dongles`, `wait_start`,
`start_clock`). Being woken up does not mean the dongles can be taken:

- another coder may have changed the state before this one got the
  `arbiter` back;
- the wake-up may come from a timeout or from `wake_all`;
- POSIX allows spurious wake-ups.

**No lost wake-ups.** A coder checks its condition and goes to sleep
while holding the `arbiter`, and `release_dongles` / `wake_all` signal
while holding the same `arbiter`. A signal therefore can never arrive
between the check and the sleep. The only exception is the short
`usleep` step of `wait_turn` (last 8 ms before a cooldown ends), where
the coder is not on the condition variable; it re-checks right after
that short sleep anyway, so nothing is missed for long.

### Communication between coders and the monitor

Coders and the monitor never call each other. They only share a few
values, each guarded by a mutex:

| Value | Written by | Read by | Used for | Guarded by |
|---|---|---|---|---|
| `last_compile` | the coder, when it starts compiling | the monitor | burnout check | the coder's `state_mutex` |
| `compiles` | the coder, after each compile | the monitor | "everyone is done" check | the coder's `state_mutex` |
| `stop` | the monitor, or a coder that burns out | everyone | ending the simulation | `stop_mutex` (set under `log_mutex`) |

To end the simulation, setting `stop` is not enough: a coder sleeping on
its condition variable would never see it. `stop_simulation` therefore:

1. sets `stop` while holding `log_mutex`;
2. calls `wake_all`, which signals every coder's `wake` while holding
   the `arbiter`.

Woken coders check `is_stopped` in their `while` loop and return.
Coders sleeping in `sleep_until` wake up in short steps and see `stop`
at their next step. `main` then joins all threads.

### Examples of race conditions that are prevented

- **Two neighbours taking the same dongle.** The per-dongle heap decides
  *whose turn* it is: only the coder at the head may take the dongle.
  But a heap alone is not enough: without a lock, two coders could both
  check "I can take it" before either of them takes it. `try_take`
  checks (head of both queues, both dongles free and cooled down) and
  takes both dongles in one step while holding the `arbiter`, so nobody
  can slip in between. `holder` is also read and written under the
  dongle's own mutex.
- **Two coders getting the same ticket.** `make_request` reads and
  increments `next_ticket` while holding the `arbiter`, so two requests
  can never get the same number.

## Resources

- B. Nichols, D. Buttlar, J. Proulx Farrell, *Pthreads Programming*
  (O'Reilly, 1996). Its table of contents was used as the outline for
  personal study notes on threads, mutexes and condition variables.
- Discussions with other 42 students about their implementations.

### How AI was used

Claude (Anthropic) was used for:

- discussing concepts (threads, mutexes, condition variables) and
  creating study notes;
- reviewing code;
- discussing edge cases and getting help when stuck;
- implementation, which was carried out together with the AI;
- turning the author's answers into this README in English and
  correcting mistakes in them.
