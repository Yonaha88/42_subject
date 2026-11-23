"""コマンドライン: RagCli のメソッド 1 つが 1 コマンド。

  index     corpus -> chunking -> indexing（変わったファイルだけ作り直す）
  search    retrieval（bm25 / semantic / hybrid）
  answer    retrieval -> augmentation -> generation
  evaluate  evaluation
  serve     ローカル HTTP API

エラーはここで表示せず、RagError を投げる（表示は __main__.py）。
"""

from pathlib import Path

from tqdm import tqdm

from src.augmentation import NO_CONTEXT_ANSWER
from src.errors import RagError
from src.evaluation import answered_questions, recall_at_k
from src.indexing import load_index, save_index, update_index
from src.models import (
    MinimalAnswer, MinimalSearchResults, RagDataset, SearchIndex,
    StudentSearchResults, StudentSearchResultsAndAnswer,
)
from src.searcher import SEMANTIC_WEIGHT, Generator, Searcher
from src.storage import load_json, save_json
from src.validation import (
    non_negative_number, positive_integer, required_text,
)

DEFAULT_RAW_DIRECTORY = "data/raw"
DEFAULT_PROCESSED_DIRECTORY = "data/processed"
# moulinette はこれより長いソースを拒否する。
MAX_CHUNK_SIZE = 2000
DEFAULT_CONTEXT_TOKENS = 2000
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
RECALL_CUTOFFS = (1, 3, 5, 10)


class RagCli:
    """Fire が公開するコマンドの集まり。"""

    def index(
        self,
        max_chunk_size: int = MAX_CHUNK_SIZE,
        raw_directory: str = DEFAULT_RAW_DIRECTORY,
        processed_directory: str = DEFAULT_PROCESSED_DIRECTORY,
        full: bool = False,
        semantic: bool = False,
    ) -> None:
        """コーパスを読み、検索用の index を作って保存する。

        前の index があれば、変わったファイルだけ読み直す。

        Args:
            max_chunk_size: チャンクの最大文字数（2000 以下）。
            raw_directory: コーパスのフォルダ。
            processed_directory: index の保存先。
            full: True なら、前の index を使わず全部作り直す。
            semantic: True なら、意味検索用のベクトルも作る。
        """
        max_chunk_size = positive_integer("--max_chunk_size", max_chunk_size)
        if max_chunk_size > MAX_CHUNK_SIZE:
            raise RagError(
                f"--max_chunk_size must not exceed {MAX_CHUNK_SIZE}"
            )
        raw_directory = required_text("--raw_directory", raw_directory)
        processed_directory = required_text(
            "--processed_directory", processed_directory
        )

        # 前の index があれば、変わったファイルだけ作り直す（--full で全部）。
        previous = None if full else load_previous_index(processed_directory)
        update = update_index(previous, raw_directory, max_chunk_size)
        index = update.index
        save_index(index, processed_directory)
        print(
            f"Indexed {len(index.chunks)} chunks, "
            f"{len(index.postings)} distinct tokens"
        )
        print(
            f"{len(update.changed_files)} files read again, "
            f"{len(index.file_digests) - len(update.changed_files)} reused, "
            f"{len(update.removed_files)} removed"
        )
        if semantic:
            # torch の読み込みは数秒かかるので、必要なときだけ import する。
            from src.semantic import TextEmbedder, update_vectors
            created, reused = update_vectors(
                index, processed_directory, TextEmbedder()
            )
            print(f"Vectors: {created} created, {reused} reused")
        print(f"Ingestion complete! Indices saved under {processed_directory}")

    def search(
        self,
        query: str = "",
        k: int = 5,
        processed_directory: str = DEFAULT_PROCESSED_DIRECTORY,
        method: str = "bm25",
        semantic_weight: float = SEMANTIC_WEIGHT,
        use_cache: bool = False,
    ) -> None:
        """1 つの質問に対して、上位 k 件のソースを表示する。

        Args:
            query: 質問。
            k: 表示する件数。
            processed_directory: index の場所。
            method: bm25、semantic、hybrid のどれか。
            semantic_weight: hybrid で、意味検索の順位にかける重み。
            use_cache: True なら、結果をキャッシュする。
        """
        query = required_text("the query", query)
        k = positive_integer("--k", k)
        searcher = make_searcher(
            processed_directory, method, semantic_weight, use_cache
        )

        sources = searcher.search(query, k)
        searcher.save_cache()
        if not sources:
            print("No result found.")
        for rank, source in enumerate(sources, start=1):
            first = source.first_character_index
            last = source.last_character_index
            print(f"{rank}. {source.file_path} [{first}:{last}]")

    def search_dataset(
        self,
        dataset_path: str = "",
        k: int = 10,
        save_directory: str = "",
        processed_directory: str = DEFAULT_PROCESSED_DIRECTORY,
        method: str = "bm25",
        semantic_weight: float = SEMANTIC_WEIGHT,
        use_cache: bool = False,
    ) -> None:
        """データセットの全質問を検索し、結果をファイルに書く。

        Args:
            dataset_path: 質問のデータセット（JSON）。
            k: 1 質問あたりの件数。
            save_directory: 結果を書くフォルダ。
            processed_directory: index の場所。
            method: bm25、semantic、hybrid のどれか。
            semantic_weight: hybrid で、意味検索の順位にかける重み。
            use_cache: True なら、結果をキャッシュする。
        """
        dataset_path = required_text("--dataset_path", dataset_path)
        k = positive_integer("--k", k)
        save_directory = required_text("--save_directory", save_directory)
        dataset = load_json(dataset_path, RagDataset)
        searcher = make_searcher(
            processed_directory, method, semantic_weight, use_cache
        )

        results = []
        for question in tqdm(
            dataset.rag_questions, desc="Searching", unit="question"
        ):
            results.append(
                MinimalSearchResults(
                    question_id=question.question_id,
                    question=question.question,
                    retrieved_sources=searcher.search(question.question, k),
                )
            )
        searcher.save_cache()

        output_path = Path(save_directory) / Path(dataset_path).name
        save_json(
            StudentSearchResults(search_results=results, k=k), output_path
        )
        print(f"Saved student_search_results to {output_path}")

    def answer(
        self,
        query: str = "",
        k: int = 5,
        processed_directory: str = DEFAULT_PROCESSED_DIRECTORY,
        max_context_tokens: int = DEFAULT_CONTEXT_TOKENS,
        method: str = "bm25",
        semantic_weight: float = SEMANTIC_WEIGHT,
        use_cache: bool = False,
    ) -> None:
        """検索してから、モデルで 1 つの質問に答える。

        Args:
            query: 質問。
            k: 使うソースの数。
            processed_directory: index の場所。
            max_context_tokens: プロンプトに入れる文脈のトークン数の上限。
            method: bm25、semantic、hybrid のどれか。
            semantic_weight: hybrid で、意味検索の順位にかける重み。
            use_cache: True なら、検索結果と回答をキャッシュする。
        """
        query = required_text("the query", query)
        k = positive_integer("--k", k)
        max_context_tokens = positive_integer(
            "--max_context_tokens", max_context_tokens
        )
        searcher = make_searcher(
            processed_directory, method, semantic_weight, use_cache
        )

        if not searcher.search(query, k):
            print(NO_CONTEXT_ANSWER)
            return
        # torch の読み込みは数秒かかるので、answer のときだけ import する。
        from src.generation import AnswerGenerator
        sources, answer = searcher.answer(
            AnswerGenerator(), query, k, max_context_tokens
        )
        searcher.save_cache()
        print(answer)
        print("\nSources:")
        for source in sources:
            first = source.first_character_index
            last = source.last_character_index
            print(f"  {source.file_path} [{first}:{last}]")

    def answer_dataset(
        self,
        student_search_results_path: str = "",
        save_directory: str = "",
        max_context_tokens: int = DEFAULT_CONTEXT_TOKENS,
    ) -> None:
        """検索結果ファイルの全質問に、モデルで答える。

        Args:
            student_search_results_path: search_dataset が書いたファイル。
            save_directory: 回答つきの結果を書くフォルダ。
            max_context_tokens: プロンプトに入れる文脈のトークン数の上限。
        """
        results_path = required_text(
            "--student_search_results_path", student_search_results_path
        )
        save_directory = required_text("--save_directory", save_directory)
        max_context_tokens = positive_integer(
            "--max_context_tokens", max_context_tokens
        )
        results = load_json(results_path, StudentSearchResults)
        total = len(results.search_results)
        print(f"Loaded {total} questions")

        from src.generation import AnswerGenerator
        generator = AnswerGenerator()
        answers = []
        for result in tqdm(
            results.search_results, desc="Answering", unit="question"
        ):
            answers.append(
                MinimalAnswer(
                    question_id=result.question_id,
                    question=result.question,
                    retrieved_sources=result.retrieved_sources,
                    answer=generator.answer(
                        result.question,
                        result.retrieved_sources,
                        max_context_tokens,
                    ),
                )
            )
        print(f"Processed {len(answers)} of {total} questions")

        output_path = Path(save_directory) / Path(results_path).name
        save_json(
            StudentSearchResultsAndAnswer(
                search_results=answers, k=results.k
            ),
            output_path,
        )
        print(f"Saved student_search_results_and_answer to {output_path}")

    def serve(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        processed_directory: str = DEFAULT_PROCESSED_DIRECTORY,
        method: str = "bm25",
        semantic_weight: float = SEMANTIC_WEIGHT,
        use_cache: bool = True,
        max_context_tokens: int = DEFAULT_CONTEXT_TOKENS,
    ) -> None:
        """ローカル HTTP API を起動する。

        Args:
            host: 待ち受けるアドレス。
            port: 待ち受けるポート（0 なら空いているポート）。
            processed_directory: index の場所。
            method: bm25、semantic、hybrid のどれか。
            semantic_weight: hybrid で、意味検索の順位にかける重み。
            use_cache: True なら、結果をキャッシュする。
            max_context_tokens: プロンプトに入れる文脈のトークン数の上限。
        """
        host = required_text("--host", host)
        if isinstance(port, bool) or not isinstance(port, int) or not (
            0 <= port <= 65535
        ):
            raise RagError(f"--port must be between 0 and 65535, got {port!r}")
        max_context_tokens = positive_integer(
            "--max_context_tokens", max_context_tokens
        )
        searcher = make_searcher(
            processed_directory, method, semantic_weight, use_cache
        )
        # FastAPI の読み込みは時間がかかるので、serve のときだけ import する。
        from src.server import run_server
        run_server(
            searcher, make_answer_generator, host, port, max_context_tokens
        )

    def evaluate(
        self,
        student_search_results_path: str = "",
        dataset_path: str = "",
    ) -> None:
        """検索結果を、正解つきのデータセットと比べて recall を表示する。

        Args:
            student_search_results_path: search_dataset が書いたファイル。
            dataset_path: AnsweredQuestions のデータセット。
        """
        results_path = required_text(
            "--student_search_results_path", student_search_results_path
        )
        dataset_path = required_text("--dataset_path", dataset_path)
        results = load_json(results_path, StudentSearchResults)
        dataset = load_json(dataset_path, RagDataset)
        evaluated = len(answered_questions(dataset))
        if evaluated == 0:
            raise RagError(
                f"{dataset_path} has no reference source: "
                f"use a dataset of AnsweredQuestions"
            )

        print("Evaluation Results")
        print("=" * 40)
        print(f"Questions evaluated: {evaluated}")
        print(" ".join(
            f"Recall@{k}: {recall_at_k(dataset, results, k):.3f}"
            for k in RECALL_CUTOFFS
        ))


def load_previous_index(processed_directory: str) -> SearchIndex | None:
    """前の index を読む。

    Args:
        processed_directory: index の場所。

    Returns:
        前の index。なければ（壊れていても）None で、全部作り直す。
    """
    try:
        return load_index(processed_directory)
    except RagError:
        return None


def make_searcher(
    processed_directory: str, method: str, semantic_weight: object,
    use_cache: bool,
) -> Searcher:
    """ユーザーが入力した値を検査して、検索器を作る。

    Args:
        processed_directory: index の場所。
        method: bm25、semantic、hybrid のどれか。
        semantic_weight: 意味検索の順位の重み（0 以上）。
        use_cache: True なら、キャッシュを使う。

    Returns:
        検索器。

    Raises:
        RagError: 値が正しくないとき。
    """
    # method は Searcher が検査する。
    return Searcher(
        required_text("--processed_directory", processed_directory),
        method,
        non_negative_number("--semantic_weight", semantic_weight),
        bool(use_cache),
    )


def make_answer_generator() -> Generator:
    """回答を書くモデルを読み込む。

    モデルは、最初の /answer が来たときに読み込む（起動を速くするため）。

    Returns:
        回答を書くもの。
    """
    from src.generation import AnswerGenerator
    return AnswerGenerator()
