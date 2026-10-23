*This project has been created as part of the 42 curriculum by kyonaha.*

# Call Me Maybe

## Description

Call Me Maybe turns a request written in plain English into a function call
that a program can run. Given the request "What is the sum of 2 and 3?" and a
list of available functions, it answers with the name of the function and its
arguments:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {"a": 2.0, "b": 3.0}
}
```

The model is Qwen3-0.6B, a small model that often breaks the JSON format when
it is simply asked to answer. To make the output reliable, the program uses
**constrained decoding**: the model only chooses between tokens that keep the
text valid according to a grammar built from the function definitions. The
model decides *which* function to call and *which* values to use; the grammar
decides *how* the answer is written.

Inputs and output (all JSON):

| File | Content |
|---|---|
| `functions_definition.json` | The functions: name, description, typed parameters, return type |
| `function_calling_tests.json` | The prompts: a list of `{"prompt": "..."}` |
| `function_calls.json` | The result: for each prompt, `prompt`, `name` and `parameters` |

Supported parameter types: `string`, `number` (written as a float, for
example `3.0`), `integer`, `boolean` and `null`. The types `array` and
`object` are accepted in the definitions file but are not supported by the
decoder; the program stops with an error message when a function uses them.

## Instructions

Requirements: Python 3.10 or later and [uv](https://docs.astral.sh/uv/).
The `llm_sdk` package is included in the repository. The model
(Qwen/Qwen3-0.6B) is downloaded from Hugging Face the first time the program
runs, so an internet connection is needed once.

```bash
make install      # install the dependencies (uv sync)
make run          # run with the default files in data/input and data/output
make debug        # run under pdb
make lint         # flake8 and mypy on src
make lint-strict  # flake8 and mypy --strict on src
make clean        # remove the caches
```

Default files: `data/input/functions_definition.json`,
`data/input/function_calling_tests.json`, and the result is written to
`data/output/function_calls.json`. Other files can be given as arguments:

```bash
uv run python -m src \
    --functions_definition data/input/functions_definition.json \
    --input data/input/function_calling_tests.json \
    --output data/output/function_calls.json
```

## Example usage

Run on the sample files:

```console
$ make run
[1/11] {'name': 'fn_add_numbers', 'parameters': {'a': 2.0, 'b': 3.0}}
[2/11] {'name': 'fn_add_numbers', 'parameters': {'a': 265.0, 'b': 345.0}}
...
```

Errors in the input are reported on one line and the program exits with
status 1 instead of crashing:

```console
$ uv run python -m src --input missing.json
Error: missing.json: no such file
```

A prompt for which no valid call can be written is skipped with a warning
and the remaining prompts are still processed.

## Algorithm explanation

**Grammar.** For every function, a grammar describes exactly the text
`{"name": "<function name>", "parameters": {"<p1>": <value>, "<p2>": <value>}}`.
The function name and the parameter names are fixed in the grammar; only the
values and the choice of function are open. The grammar of the whole program
is "any one of these function grammars".

**States.** The grammar is a state machine that works one character at a
time. A state has two operations:

- `feed(char)` returns the next state if the character is allowed, or `None`
  if it is not;
- `can_finish()` tells whether the text read so far is complete.

States are never modified: `feed` returns a new state. A state can therefore
be tried with a candidate token and thrown away without having to undo
anything.

**Generation loop.** For every prompt:

1. The first state is the grammar of all functions.
2. The characters that the current state accepts are computed.
3. If only one character is accepted, it is written directly and the model is
   not called.
4. Otherwise the model gives a score (a logit) to each of its roughly 150,000
   tokens. The tokens are examined from the highest score to the lowest; each
   one is fed to the state character by character, and the first token that
   the grammar accepts is chosen.
5. The state moves forward and the loop restarts, until no character is
   accepted and `can_finish()` is true.

Picking the first accepted token in decreasing order of score gives the same
result as setting the score of every forbidden token to minus infinity and
taking the maximum (greedy decoding), without building a mask over the whole
vocabulary at every step.

The text is then read with `json.loads`. Numbers are converted to the type of
the definition (`float` for `number`, `int` for `integer`).

**Vocabulary.** The vocabulary file of the model stores tokens in the
byte-level BPE alphabet (a space is written `Ġ`, for example). The program
rebuilds the byte-to-character table of this alphabet, converts every token
back to the text it stands for, and keeps the token ids that are valid UTF-8.

## Design decisions

- **Forced characters skip the model.** Much of the output (the keys, the
  function name once it is known, the punctuation) has exactly one valid
  continuation. Writing those characters directly, without a model call,
  saves a call at each of those steps.
- **`Choice` and `Sequence`.** Two small building blocks are combined to
  describe everything. `Sequence` is a list of parts read one after the other.
  `Choice` keeps several alternatives alive at the same time and drops the
  ones that refuse a character. The grammar of a call is a `Sequence`, and the
  grammar of the program is a `Choice` of those sequences. As soon as the
  characters read exclude all the functions but one, the choice becomes a
  single path.
- **One grammar per type.** `string` follows the JSON string rules (escape
  sequences, `\uXXXX`, no control characters). `number` and `integer` accept an
  optional minus sign and no leading zeros, and only `number` accepts a
  fractional part. `boolean` is a choice between `true` and `false`, and
  `null` is the fixed text `null`. Because a number can have any number of
  digits, a number part is allowed to end as soon as it is complete, and the
  next part of the sequence takes over when the following character does not
  continue the number.

## Performance analysis

- **Speed.** The 11 sample prompts are processed in a little over two minutes
  on the school computers (the limit is five minutes). The SDK has no cache,
  so every model call reads the whole prompt again, and a call takes about one
  second. The time is therefore driven by the number of model calls and by the
  length of the prompt; both are kept small (forced characters, short
  prompt).
- **Reliability.** Every character that is written has been accepted by the
  grammar, so the output is always valid JSON that matches the definitions.
  The number of steps per prompt is limited (300) so that a prompt can never
  run forever. Invalid input files, unreadable files and unwritable output
  are reported with a message and a non-zero exit status.
- **Accuracy.** The model chooses the function and copies the values from the
  request. On the sample prompts the right function was chosen every time.
  The values inside strings are less stable: the model sometimes handles quotes
  or the first characters of a string badly, which the grammar cannot detect
  because the text is still valid.

## Challenges faced

- **A space at the start of a string.** The model often starts a string value
  with a token that begins with a space, such as ` /home`, so
  `/home/user/data.json` became ` /home/user/data.json`. Refusing the space
  in the grammar was not enough: the model's favourite token (` /`) was
  rejected, and the next best token had no slash, giving
  `home/user/data.json`. The fix has two parts. The grammar refuses a space
  right after the opening quote, and when a candidate token starts with such a
  space, the space is removed and the rest of the token is tested.
- **The length of the prompt.** A first prompt written in plain natural
  language, with the function list as a JSON schema and long instructions,
  made the run take just under four minutes, because the prompt is read again
  at every step. Switching to the chat format of Qwen (`<|im_start|>` and
  `<|im_end|>`) with a short system message brought it back to a little over
  two minutes.

## Testing strategy

- **Runs on the sample files**: the whole program was run on the sample
  inputs and each line of the output file was compared with its request.
- **Edge cases tried by hand**: an empty prompt, numbers written in words,
  negative numbers, a prompt that matches no function, strings with quotes,
  backslashes and braces, and a regular expression to substitute.

## Resources

References:

- [What is an encoder-decoder? (in Japanese)](https://saycon.co.jp/archives/neta/%E3%80%90%E5%88%9D%E5%BF%83%E8%80%85%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2%E5%90%91%E3%81%91%E3%80%91%E3%82%A8%E3%83%B3%E3%82%B3%E3%83%BC%E3%83%80%E3%83%BB%E3%83%87%E3%82%B3%E3%83%BC%E3%83%80),
  Sei Consulting Group: the encoder-decoder structure explained for beginners
- [Controlling LLM output: a guide to structured text generation (in Japanese)](https://qiita.com/Dataiku/items/a53b1b364a2c76d4cd6c),
  Qiita (translation of Dataiku's "Taming LLM Outputs"): constrained decoding
  and other ways to get a fixed output format

Much of the understanding of the subject also came from talking with other
students and from the explanations of an AI assistant, besides these
articles.

Use of AI. An AI assistant was used:

- to learn the modules and concepts needed for the project (pydantic,
  argparse, tokens and logits, byte-level BPE, state machines);
- to discuss ideas to improve the performance (prompt length, skipping the
  model when one character is possible, how to pick a token);
- to write the docstrings and README: the content was decided by the author, and the AI
  assistant wrote the English text.

## Project structure

| File | Role |
|---|---|
| `src/__main__.py` | Entry point: reads the inputs, runs every prompt, writes the result |
| `src/parser.py` | Command line and input files, validated with pydantic |
| `src/prompt.py` | Builds the prompt sent to the model |
| `src/grammar.py` | The states of the grammar (`Literal`, `Number`, `String`, `Choice`, `Sequence`) |
| `src/generate.py` | The generation loop and the choice of tokens |
| `src/vocabulary.py` | Maps token ids to the text they stand for |
| `src/writer.py` | Writes `function_calls.json` |
| `llm_sdk/` | The SDK provided with the subject |
