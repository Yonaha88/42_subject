*This project has been created as part of the 42 curriculum by kyonaha.*

# RAG against the machine

## Description

This project is a small **Retrieval-Augmented Generation** (RAG) system that answers questions about the [vLLM](https://github.com/vllm-project/vllm) code base (version 0.10.1).

A language model alone cannot answer "how do I load a LoRA adapter in vLLM?": it has never read the repository. RAG solves this in three steps:

1. **Retrieve**: find the few pieces of the repository that talk about the question.
2. **Augment**: paste these pieces into the prompt, next to the question.
3. **Generate**: let the model (`Qwen/Qwen3-0.6B`) write the answer from what it has just been given.

Everything except the last step is classic programming: reading files, cutting text, counting words. The retrieval is done with BM25, written from scratch, with no vector database and no embedding model.

On the public datasets the search finds the right source in its first five results for **92 %** of the documentation questions and **85 %** of the code questions (the subject asks for 80 % and 50 %).

## Instructions

### Requirements

- Python 3.10 or later and [uv](https://docs.astral.sh/uv/).
- About 1 GB of disk for the virtual environment (CPU build of PyTorch) and 1.5 GB for the model, downloaded by the first `answer` command into the Hugging Face cache (`~/.cache/huggingface`, or `$HF_HOME` if set). No GPU is needed.

### Installation

```bash
make install        # same as: uv sync
```

### Data

The data is not part of the repository. Put it in place as follows:

```
data/
├── raw/vllm-0.10.1/                 the vLLM repository to index
├── datasets/
│   ├── UnansweredQuestions/         dataset_docs_public.json, dataset_code_public.json
│   └── AnsweredQuestions/           same files, with the reference sources
├── processed/                       written by `index`
└── output/                          written by `search_dataset` and `answer_dataset`
```

### Commands

Every command is run from the root of the repository as `uv run python -m src <command> [options]`.

| Command | What it does |
|---|---|
| `index --max_chunk_size 2000` | Reads `data/raw/`, writes the index to `data/processed/`. Only the files that changed since the last run are read again. |
| `search "<question>" --k 5` | Prints the `k` best sources for one question. |
| `search_dataset --dataset_path <file> --k 10 --save_directory <dir>` | Searches every question of a dataset, writes a `StudentSearchResults` file. |
| `answer "<question>" --k 5` | Searches, then answers one question with the model. |
| `answer_dataset --student_search_results_path <file> --save_directory <dir>` | Answers every question of a search results file. |
| `evaluate --student_search_results_path <file> --dataset_path <file>` | Prints recall@1, 3, 5 and 10 against a dataset of `AnsweredQuestions`. |
| `serve --port 8000` | Starts a local HTTP API (see [Bonus features](#bonus-features)). |

Extra options: `--raw_directory` (default `data/raw`) for `index`, `--processed_directory` (default `data/processed`) for every command that uses the index, `--max_context_tokens` (default 2000) for the two `answer` commands, and, described in [Bonus features](#bonus-features): `--semantic` and `--full` for `index`; `--method`, `--semantic_weight` and `--use_cache` for `search`, `search_dataset` and `answer`.

### Makefile

| Rule | Action |
|---|---|
| `make install` | Install the dependencies with `uv sync`. |
| `make run` | Run the program (shows the list of commands). |
| `make debug` | Run the program under `pdb`. |
| `make lint` | `flake8` and `mypy` with the flags of the subject. |
| `make lint-strict` | `flake8` and `mypy --strict`. |
| `make test` | Run the unit tests with `pytest`. |
| `make clean` | Remove the caches (`__pycache__`, `.mypy_cache`, ...). |

## Example usage

```console
$ uv run python -m src index --max_chunk_size 2000
Indexed 14062 chunks, 12933 distinct tokens
Ingestion complete! Indices saved under data/processed

$ uv run python -m src search "How do I enable prefix caching?" --k 3
1. data/raw/vllm-0.10.1/docs/features/automatic_prefix_caching.md [418:593]
2. data/raw/vllm-0.10.1/tests/v1/engine/test_engine_args.py [503:2121]
3. data/raw/vllm-0.10.1/vllm/engine/arg_utils.py [73823:74963]

$ uv run python -m src search_dataset \
    --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
    --k 10 \
    --save_directory data/output/search_results/UnansweredQuestions
Saved student_search_results to data/output/search_results/UnansweredQuestions/dataset_docs_public.json

$ uv run python -m src evaluate \
    --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
    --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json
Evaluation Results
========================================
Questions evaluated: 100
Recall@1: 0.730 Recall@3: 0.910 Recall@5: 0.920 Recall@10: 0.960

$ uv run python -m src answer "How do I enable prefix caching?" --k 5
To enable prefix caching in vLLM, set `enable_prefix_caching=True` in the
vLLM engine configuration. [...]

Sources:
  data/raw/vllm-0.10.1/docs/features/automatic_prefix_caching.md [418:593]
  [...]

$ uv run python -m src answer_dataset \
    --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
    --save_directory data/output/search_results_and_answer/UnansweredQuestions
Loaded 100 questions
Processed 100 of 100 questions
Saved student_search_results_and_answer to data/output/search_results_and_answer/UnansweredQuestions/dataset_docs_public.json
```

Wrong input gives one line of explanation, never a traceback:

```console
$ uv run python -m src search "lora" --k 0
Error: --k must be a positive integer, got 0
$ uv run python -m src search ""
Error: the query must not be empty
$ uv run python -m src search "zzzqqq"
No result found.
```

## System architecture

```
            index (once)                          search / answer (each question)

 data/raw/ ──► corpus ──► chunking ──► indexing ──► data/processed/index.json
               which       cut files    count the                │
               files       in chunks    words                    ▼
                                                 question ──► retrieval ──► sources
                                                              (BM25)          │
                                                                              ▼
                                                 answer ◄── generation ◄── augmentation
                                                            (Qwen3-0.6B)   (build prompt)
```

One module per stage, in the order a question goes through them. Reading the files in this order is the easiest way to understand the project:

| Module | Role |
|---|---|
| `src/models.py` | The pydantic models: the shape of every piece of data and of every JSON file. |
| `src/corpus.py` | Lists the files to index and reads them. |
| `src/chunking.py` | Cuts a file into chunks of at most `max_chunk_size` characters. |
| `src/tokenization.py` | Turns a text into the list of words used for matching. |
| `src/indexing.py` | Builds the inverted index and saves it. |
| `src/retrieval.py` | Ranks the chunks for a question with BM25. |
| `src/augmentation.py` | Writes the prompt from the retrieved sources. |
| `src/generation.py` | Loads the model and generates the answer. |
| `src/evaluation.py` | Computes recall@k. |
| `src/semantic.py` | The embedding model and the vector store (bonus). |
| `src/searcher.py`, `src/cache.py` | Loads the index once and searches (`bm25`, `semantic` or `hybrid`); optionally remembers the results of earlier questions. |
| `src/server.py` | The local HTTP API (FastAPI). |
| `src/cli.py` | The commands; each one chains the modules above. |
| `src/validation.py`, `src/storage.py`, `src/errors.py` | Checking user values, reading and writing JSON, and the error type shown to the user. |
| `src/__main__.py` | Entry point; the only place where errors are caught and printed. |

A chunk is stored as a `MinimalSource` (file path, first character, last character). The index never stores the text of a chunk: the text is read again from the file when it is needed for the prompt.

## Chunking strategy

Chunks may not be longer than 2000 characters (`--max_chunk_size`). A chunk that mixes two unrelated subjects is harder to match with a question, so files are cut where their author cut them.

**Python code** (`.py`). The file is parsed with the standard `ast` module. A cut is allowed before each top-level statement (import, function, class...) and before each member of a class; decorators stay with their function. Neighbouring blocks are then glued together while the result fits in the limit. Gluing matters: a chunk holding only a two-line function has too few words to be found, and experiments with "one function per chunk" lost more than 30 points of recall. A file that does not parse is cut between lines instead.

**Markdown and text** (`.md`, `.txt`). The file is cut at its headings: one section, one chunk. Lines inside fenced code blocks are skipped so that a shell comment (`# install`) is not taken for a heading. Sections are *not* glued together: a section is already about one subject. A section longer than the limit is cut between paragraphs.

In both cases a block that is still too long (a huge function, a huge table) is cut at the last end of line before the limit, and a line longer than the limit is cut at the limit. Chunks cover each file with no gap and no overlap, and the limit is never exceeded.

The corpus gives 14,062 chunks from 1,847 files (12,440 Python chunks with a median of 1,728 characters; 1,622 documentation chunks with a median of 468 characters).

## Retrieval method

**Tokenization** (`src/tokenization.py`). BM25 only matches identical tokens, so the question and the chunk that answers it must produce the same tokens:

1. names are split into words: `snake_case`, `CamelCase`, `HTTPServer` and `qwen3` become `snake case`, `camel case`, `http server`, `qwen 3`. `vLLM` and `gRPC` (one lowercase letter + an acronym) are not split: with `vLLM` split into `v` and `llm`, almost every question contained the word `llm` and was pulled towards files like `vllm/entrypoints/llm.py`;
2. everything is lowercased and about fifty stop words (`what`, `is`, `the`...) are dropped;
3. a tiny stemmer strips `s`, `ing`, `ed` and `e`, so that `cache`, `caches`, `cached` and `caching` are one token.

**Index** (`src/indexing.py`). An inverted index maps each token to the chunks that contain it and how many times: `"lora" -> [(chunk 12, 3 times), (chunk 40, 1 time), ...]`. The tokens of the file path are added to each chunk, three times: a chunk of `vllm/lora/models.py` is about LoRA even if the word is not in its text. For a Markdown chunk, the words of its headings are added once more, because a heading names the section.

**Ranking** (`src/retrieval.py`). Each chunk gets a BM25 score, the sum over the tokens of the question of

```
idf(token) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * chunk_length / average_length))
```

where `tf` is the number of times the token is in the chunk, `idf = ln((N - n + 0.5) / (n + 0.5) + 1)` is high for a token found in few chunks, `k1 = 1.5` limits the effect of repetitions and `b = 0.75` compensates for long chunks. Only the chunks listed in the postings of the question's tokens are visited, which is why a search takes a few milliseconds.

Finally, the score of a chunk that lives in a supporting folder (`tests/`, `benchmarks/`, `examples/`, `tools/`...) is multiplied by 0.8. The answers are mostly in the library (`vllm/`) and in the documentation (`docs/`); a test file often repeats the same words and used to take a place in the top 5. The factor is mild on purpose: a chunk of `tests/` can still be first. The other way round, the score of a documentation chunk (`.md`) is multiplied by 1.2: the answer to a question asking for an explanation is in the documentation, but it used to lose against code chunks that repeat the same words.

**Generation**. The retrieved sources are added to the prompt in rank order until the token budget (2000 tokens by default, counted with the tokenizer of the model) is reached. A system message tells the model to answer only from the sources and to say so when the answer is not there. Decoding is greedy (the same question always gives the same answer) and the "thinking" mode of Qwen3 is turned off. When the search finds nothing, a fixed sentence is returned instead of letting the model invent an answer.

## Performance analysis

Measured with the provided moulinette (`--k 10 --max_context_length 2000`) on the public datasets; the `evaluate` command gives the same numbers.

| Dataset | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Required (recall@5) |
|---|---|---|---|---|---|
| docs (100 questions) | 0.730 | 0.910 | **0.920** | 0.960 | 0.80 |
| code (99 questions) | 0.444 | 0.717 | **0.848** | 0.879 | 0.50 |

| Operation | Measured | Limit |
|---|---|---|
| `index` (1,847 files) | about 5 s | 5 min |
| `search_dataset`, 100 questions (index loading included) | about 1 s | 90 s for 200 questions |
| `answer`, per question (CPU, 20 threads) | about 10 s | none |

The index file is 10 MB.

What each idea brings (recall@5, each line adds to the previous one):

| Step | docs | code |
|---|---|---|
| Fixed 2000-character chunks, lowercase words | 0.84 | 0.64 |
| Structural chunks (AST and headings) | 0.84 | 0.55 |
| + split names (`snake_case`, `CamelCase`) | 0.81 | 0.68 |
| + stop words | 0.84 | 0.66 |
| + stemming | 0.88 | 0.70 |
| + file path tokens, once | 0.87 | 0.81 |
| + file path tokens, three times | 0.89 | 0.85 |
| + headings once, supporting files x0.8 | 0.92 | 0.86 |

The largest gain on code comes from the file path. Questions about code name a feature ("the fused batched MoE layer"), and that name is often in the path of the file but rarely in each of its chunks. Structural chunking alone does not help code; its benefit shows on the documentation (0.85 to 0.89 with the final tokenizer) because the reference sources are sections.

The last step is the only one added after the first measurements: the supporting-file factor gives +3 points on docs and +1 on code, and the heading words +2 points on docs at recall@3. It is consistent for the factors 0.4, 0.6 and 0.8.

**Two later additions.** The final version also keeps `vLLM` and `gRPC` whole in the tokenizer (the usual rule cuts `vLLM` into `v` and `LLM`, and `llm` would then be in almost every chunk), and multiplies the score of the Markdown chunks by 1.2, a small bonus for the documentation, which explains vLLM in prose:

| Step | docs | code |
|---|---|---|
| Version of the table above | 0.92 | 0.86 |
| + `vLLM` kept whole | 0.90 | 0.85 |
| + `.md` chunks x1.2 (final) | **0.92** | **0.85** |

The other weights (path x3, headings x1, supporting files x0.8, BM25 k1 and b) stay within ±2 points when moved, so they were kept.

With 100 questions, one question is one point: differences of one or two points between variants are noise.

**What did not help.** Each of these was measured on the public datasets (recall@5, docs / code). The embedding and fusion rows are available as bonus options (`--method`), but none of them beats BM25 alone, which is why the default search stays purely lexical:

| Idea | docs | code |
|---|---|---|
| BM25 alone (final version) | 0.92 | 0.85 |
| Embeddings alone (`all-MiniLM-L6-v2`, 256 tokens; the former bonus model) | 0.61 | 0.29 |
| Embeddings alone (`bge-micro-v2`, 256 tokens + path; the current bonus model) | 0.77 | 0.54 |
| Embeddings alone (`bge-small-en-v1.5`; indexing would take about 7 minutes) | 0.75 | 0.36 |
| BM25 + embeddings, reciprocal rank fusion (weight 0.1 to 0.5 for the embeddings) | 0.84 to 0.93 | 0.63 to 0.83 |
| Cross-encoder (`ms-marco-MiniLM-L-6-v2`) re-ranking the top 10 BM25 results | 0.86 to 0.90 | 0.65 to 0.72 |
| Smaller chunks (400 to 1500 characters) | 0.86 to 0.89 | 0.75 to 0.84 |
| Extra chunks overlapping the cuts | 0.90 | 0.85 to 0.87 |
| At most 2 chunks per file in the top 5 | 0.91 | 0.77 |

The chunk size and overlap rows were measured on the version before the last step (0.89 / 0.85), the others on the final one. The questions contain exact names (`trust_remote_code`, `VLLM_RPC_TIMEOUT`); a general embedding model blurs them, while BM25 matches them exactly.

Known limits: BM25 cannot match a synonym (a question about "speed" does not find a text about "throughput"), and a few reference sources are so short (under 100 characters) that a chunk of 2000 characters around them never reaches the overlap required by the evaluation.

## Design decisions

- **BM25 from scratch instead of a library or embeddings.** It is about thirty lines, every number in it can be explained, indexing takes seconds and it already exceeds the required recall. Embeddings and a hybrid search are available as bonus options, but they did not raise the recall (see Performance analysis), so the default search stays purely lexical.
- **The index is one JSON file described by a pydantic model** (`SearchIndex`). It can be opened in an editor to see what an inverted index is, and a damaged file is rejected with a clear message (`pickle` is opaque and unsafe to load from an untrusted file).
- **The index stores positions, not text.** A chunk is a `MinimalSource`, exactly what the output format asks for, so no conversion is needed.
- **One way to handle errors.** Functions raise `RagError` with a message written for the user; `__main__.py` catches it and prints it. No other module prints errors or calls `sys.exit`.
- **`torch` is imported only by the `answer` commands.** Importing it takes seconds; `search` should not pay for it.
- **The same `tokenize` function for chunks and questions**, and the same `read_text` function everywhere a file is read, so that tokens and character positions always agree.
- **CPU-only PyTorch** is selected in `pyproject.toml` to keep the installation at 1 GB instead of several.

## Challenges faced

- **Character positions.** The evaluation compares character ranges, so an offset error is a silent failure. `ast` gives line numbers, not positions; they are converted with a table of line starts. Files are always read the same way, and a test checks that the chunks of a file, put end to end, give back the file exactly.
- **Small chunks are not better chunks.** The first idea, one function per chunk, was much worse than fixed-size chunks. Measuring every idea with `evaluate` before keeping it was essential.
- **Code questions are written in English, code is written in identifiers.** Splitting names, stemming and indexing the file path were all needed to connect the two.
- **Python Fire converts arguments** (`--k 2.5` is a float, `--k` alone is `True`, a query of digits is an int). Every value is checked before it is used.
- **A small model on a CPU.** Qwen3-0.6B is slow to read a long prompt and tends to invent when the context is weak: hence the token budget, the strict system message and the fixed answer when nothing is found.

## Bonus features

The five bonuses are implemented. All of them are off by default, so the mandatory commands behave exactly as described above (and `index` stays at about 5 seconds).

### 1. Semantic embeddings (`src/semantic.py`)

`index --semantic` also builds a vector index: every chunk is turned into a vector by `TaylorAI/bge-micro-v2` (an English retrieval model of 17 M parameters and 3 layers, run with `transformers`, mean pooling, 256 tokens at most). The embedded text is the file path followed by the chunk: as for BM25, the path is a useful clue. The vectors are saved in `data/processed/vectors.npz`, each one under a name made of the file fingerprint and the position of the chunk. A search with `--method semantic` embeds the question and returns the chunks whose vectors are closest (cosine similarity).

```bash
uv run python -m src index --semantic        # about 210 s the first time, on 16 cores
uv run python -m src search "How to serve several LoRA adapters?" --method semantic
```

### 2. Hybrid retrieval (`src/retrieval.py`, `src/searcher.py`)

`--method hybrid` takes the 50 best chunks of the BM25 ranking and the 50 best of the semantic ranking and merges the two lists with **reciprocal rank fusion**: a chunk gets `weight / (1 + rank)` from each list (1/2 for the first, 1/3 for the second). Using ranks instead of scores lets BM25 scores and cosine similarities be mixed without rescaling. The semantic list has a weight of 0.3 by default (`--semantic_weight`) and BM25 a weight of 1.

```bash
uv run python -m src search "How to serve several LoRA adapters?" --method hybrid --k 5
```

Measured results (recall@5):

| Method | docs | code |
|---|---|---|
| `bm25` (default) | **0.92** | **0.85** |
| `semantic` | 0.77 | 0.54 |
| `hybrid` (weight 0.3, `1 + rank`; default) | **0.93** | 0.84 |
| `hybrid` (weight 0.1, `60 + rank`; former setting) | 0.92 | 0.81 |

**Tuning the weight.** With the usual `60 + rank` of RRF, the first place (1/61) and the tenth (1/70) score almost the same, so even low semantic candidates pushed the top BM25 results out, and a weight above 0.1 lowered the recall (public code 0.69 at weight 0.3). Adding 1 instead lets only the top of each ranking count strongly. Any weight from 0.2 to 0.6 gives about the same result, so 0.3, near the middle, is used (adding 5, 10 or 15, and pools of 10, 20 or 100 candidates, did not do better).

**Choosing the model.** Small English models were compared under one condition: the whole `index --semantic` must finish within 300 seconds (16-core CPU, recall@5 of the semantic search alone). The time is roughly "number of chunks x tokens read": reading 14,062 chunks at 256 tokens each took 340 seconds even with a model of the same size.

| Model | Tokens read | Time | docs / code |
|---|---|---|---|
| `all-MiniLM-L6-v2` (former) | 256 | 342 s | 0.61 / 0.29 |
| `all-MiniLM-L6-v2` | 128 | about 170 s | 0.68 / 0.28 |
| `snowflake-arctic-embed-xs` + path | 128 | about 170 s | 0.66 / 0.48 |
| `multi-qa-MiniLM-L6-cos-v1` + path | 128 | 204 s | 0.74 / 0.47 |
| `multi-qa-MiniLM-L6-cos-v1` + path | 96 | 157 s | 0.74 / 0.40 |
| `bge-micro-v2` + path | 128 | about 100 s | 0.73 / 0.42 |
| `bge-micro-v2` + path | 192 | 152 s | 0.77 / 0.49 |
| **`bge-micro-v2` + path (current)** | **256** | **209 s** | **0.77 / 0.54** |
| `bge-small-en-v1.5` + path | 128 | stopped at 300 s | — |
| static (`static-retrieval-mrl-en-v1`, `potion-retrieval-32M`) | all | about 8 s | 0.50 / 0.26 to 0.34 |

The models trained for retrieval (`multi-qa-MiniLM`, `bge-micro-v2`) do much better on code than the former model, which finds similar sentences; adding the path helps too. `bge-micro-v2` has only 3 layers (MiniLM has 6), so it reads twice as many tokens in the same time, and reading more of each chunk raises the recall: that is why it comes first. Hybrid gives the same results at 192 and 256 tokens, but the semantic search alone gains 5 points on code, so 256 is used: it still fits in 300 seconds. The static models (a vector per word looked up in a table, then averaged) are 40 times faster but lose accuracy on docs.

On this corpus the questions contain exact names, so the lexical ranking is the strongest and the semantic one works as a correction. Hybrid is within one point of BM25 on both datasets, and it needs the semantic index (about 210 s) and the model, so `bm25` stays the default. Hybrid is meant for questions that share no word with the answer (a paraphrase), and it costs a model load of a few seconds.

### 3. Incremental indexing (`src/indexing.py`)

`index` keeps, for every file, a fingerprint (a SHA-256 of its text, of `--max_chunk_size` and of the indexing version). On the next run it reads the previous index and **only reads, cuts and counts again the files whose fingerprint changed**; for the others it reuses their chunks and word counts, which it gets back by reading the inverted index the other way round. Added and removed files are handled. The result is exactly the index a full rebuild would give (a test checks it). The vectors are reused the same way: a vector is found again through its name, so only the changed chunks are embedded. The vector file also records how the vectors were made (model name and `MAX_TOKENS`); when that differs from the current settings, all of them are made again. `--full` forces a complete rebuild.

```
$ uv run python -m src index --semantic        # after editing one file of the corpus
Indexed 14062 chunks, 12933 distinct tokens
1 files read again, 1968 reused, 0 removed
Vectors: 14 created, 14048 reused               # 7.6 s in total instead of 3 min 9 s
```

When the way chunks are cut or words are counted changes, `INDEXING_VERSION` must be raised; it is part of the fingerprint, so every file is then read again.

### 4. Caching (`src/cache.py`)

- **The index** is built once and saved; every command only loads it (about 1 s for 14,000 chunks), and `serve` keeps it in memory.
- **The results of the questions.** With `--use_cache`, `search`, `search_dataset` and `answer` save the results (and the answers, which saves the 10 seconds of the model) in `data/processed/query_cache.json`. The cache belongs to one index: its fingerprint is a hash of `index.json` and `vectors.npz`, so a new index makes the old results disappear. An unreadable cache file is ignored, and at most 2000 entries are kept (the oldest are dropped first). The model is loaded only when a question is not in the cache.

```
$ uv run python -m src search "How to configure OpenAI server?" --method hybrid --use_cache
4.1 s   (loads the model, searches, saves)
$ uv run python -m src search "How to configure OpenAI server?" --method hybrid --use_cache
0.5 s   (read from the cache)
```

### 5. Local HTTP API (`src/server.py`)

`serve` loads the index once and answers over HTTP with FastAPI (served by uvicorn). It listens on `127.0.0.1:8000` and uses the cache by default; `--method` chooses the search.

```bash
uv run python -m src serve --port 8000
curl "http://127.0.0.1:8000/health"
curl "http://127.0.0.1:8000/search?query=How%20to%20configure%20OpenAI%20server&k=3"
curl -X POST http://127.0.0.1:8000/answer -H 'Content-Type: application/json' \
     -d '{"query": "What is PagedAttention?", "k": 5}'
```

`/search` returns a `MinimalSearchResults` and `/answer` a `MinimalAnswer` (the same models as the files). `/answer` works with `GET` (URL parameters) and `POST` (a JSON body). FastAPI checks the shape of a request with pydantic (`k` a positive integer, the body JSON). A wrong request (empty query, `k` that is not a positive integer, broken JSON) gets a JSON `{"error": ...}` with status 400, and the server keeps running. The model is loaded at the first `/answer`, so the server starts fast. Opening `http://127.0.0.1:8000/docs` in a browser shows the API page that FastAPI builds by itself.

## Resources

The articles below are in Japanese.

- BM25: [Elasticsearchの全文検索スコア(BM25)は、ざっとこう計算される](https://zenn.dev/wm3/articles/4514602f514e5c) (how the BM25 score is computed).
- `ast`: [たった1行から始めるPythonのAST(抽象構文木)入門](https://qiita.com/rhoboro/items/5bbaa3fa659ed7454d56) (introduction to Python's abstract syntax tree).
- Python Fire: [Python-Fireについて](https://qiita.com/SaitoTsutomu/items/a5eb827737c9d59af2af) and [Python Fire コマンドラインインターフェース作成の革命](https://omomuki-tech.com/archives/2378#i-4).
- `tqdm`: [グレートなtqdmの使い方](https://qiita.com/SeeLog/items/73c054a37722890b17a2).
- `json`: [【Python】jsonモジュールの使い方](https://qiita.com/coticoticotty/items/b0758214ad177f99e531).
- `pickle`: [Pythonのpickleの使い方](https://note.nkmk.me/python-pickle-usage/).
- `pathlib`: [python pathlibの使い方メモ](https://qiita.com/studio_haneya/items/11c9e825bd8068af7e87).

### Use of AI

Claude (Anthropic) was used as an assistant throughout this project:

- to explain the concepts (TF-IDF, BM25, the stages of a RAG pipeline);
- to write and restructure the unit tests and this README;
- to run the experiments reported in the performance analysis (chunking and tokenization variants measured with the moulinette).

Every number in this README was measured by running the code, and the code passes the unit tests, `flake8` and `mypy --strict`.
